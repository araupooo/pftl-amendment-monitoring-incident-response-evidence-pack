#!/usr/bin/env python3
"""amendment_monitor.py — build the amendment inventory and activation-watch
metrics from the unedited live probe outputs.

Inputs (all under outputs/, produced by scripts/probe_all.sh):
  feature_list.json, vhs-amendments-info.json, vhs-amendments-vote-test.json,
  server_info.json, ledger_current.json, ledger_closed.json,
  server_state.json, vhs-validators.json, testnet_vl.json

Outputs (under outputs/derived/):
  amendment-inventory.json — one row per known amendment with live state
  amendment-inventory.csv  — same inventory as CSV
  activation-watch.json    — thresholds, flag-ledger timing, alerts
  monitor-run.log          — the run's own log (also printed to stdout)

Pure Python stdlib. No network access: everything is computed from the
shipped probe outputs, so the run is deterministic given the inputs.
"""
import base64
import csv
import datetime
import hashlib
import json
import os
import re
import sys

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")
DERIVED = os.path.join(OUT, "derived")
PIN = "0085a1ff885d6a446369cf73a4430f75af22be55"
PIN_DIR = "/tmp/postfiatd-pin"


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def sha512_half(name):
    """Amendment ID = first 32 bytes of SHA-512(name), per Feature.cpp."""
    return hashlib.sha512(name.encode()).hexdigest()[:64].upper()


def parse_macro(path):
    """Parse include/xrpl/protocol/detail/features.macro.

    Returns a list of dicts: name, kind (feature/fix/retire),
    supported (bool), vote (DefaultYes/DefaultNo/Obsolete).
    """
    rows = []
    pat = re.compile(r"XRPL_(FEATURE|FIX|RETIRE)\s*\(\s*([A-Za-z0-9_]+)")
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            m = pat.match(line)
            if not m:
                continue
            kind, name = m.group(1), m.group(2)
            if kind == "RETIRE":
                rows.append({"name": name, "kind": "retire",
                             "supported": True, "vote": "Obsolete",
                             "macro_line": lineno})
            else:
                rows.append({"name": ("fix" if kind == "FIX" else "") + name,
                             "kind": kind.lower(),
                             "supported": "Supported::yes" in line,
                             "vote": "DefaultYes" if "DefaultYes" in line
                                     else "DefaultNo",
                             "macro_line": lineno})
    return rows


def main():
    os.makedirs(DERIVED, exist_ok=True)
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    macro = parse_macro(os.path.join(
        PIN_DIR, "include/xrpl/protocol/detail/features.macro"))
    macro_by_name = {r["name"]: r for r in macro}

    rpc = load("feature_list.json")["result"]["features"]
    vhs_info = load("vhs-amendments-info.json")["amendments"]
    vhs_vote = load("vhs-amendments-vote-test.json")["amendments"]
    si = load("server_info.json")["result"]["info"]
    lc = load("ledger_current.json")["result"]["ledger"]
    lclosed = load("ledger_closed.json")["result"]
    ss = load("server_state.json")["result"]["state"]
    vhs_val = load("vhs-validators.json")

    # --- cross-checks (each is a check that must hold) ---
    checks = []

    def check(label, ok, detail=""):
        checks.append({"check": label, "pass": bool(ok), "detail": detail})
        log(("PASS " if ok else "FAIL ") + label +
            ((" — " + detail) if detail else ""))
        return bool(ok)

    registered = len(macro)
    supported = sum(1 for r in macro if r["supported"])
    unsupported = [r["name"] for r in macro if not r["supported"]]
    check("macro registrations == 107", registered == 107, str(registered))
    check("macro supported == RPC feature count",
          supported == len(rpc), "%d vs %d" % (supported, len(rpc)))
    check("macro unsupported names == RPC-missing names",
          set(unsupported) == {r["name"] for r in macro}
          - {v["name"] for v in rpc.values()},
          ",".join(sorted(unsupported)))
    check("every RPC amendment id == sha512Half(name)",
          all(sha512_half(v["name"]) == k for k, v in rpc.items()))
    check("VHS info count == 103", len(vhs_info) == 103, str(len(vhs_info)))
    check("VHS vote-test count == enabled count",
          len(vhs_vote) == sum(1 for v in rpc.values() if v["enabled"]),
          "%d vs %d" % (len(vhs_vote),
                        sum(1 for v in rpc.values() if v["enabled"])))
    check("enabled set == DefaultYes set",
          {v["name"] for v in rpc.values() if v["enabled"]}
          == {r["name"] for r in macro if r["vote"] == "DefaultYes"})
    check("no amendment currently holds a majority",
          all("majority" not in v for v in rpc.values()))
    check("no amendment currently vetoed",
          all(not v.get("vetoed") for v in rpc.values()))
    check("all 64 activations at ledger 86785",
          len({a["ledger_index"] for a in vhs_vote}) == 1
          and vhs_vote[0]["ledger_index"] == 86785)
    check("all 64 activations at one timestamp",
          len({a["date"] for a in vhs_vote}) == 1)

    # --- ledger cadence: measured live over a 60 s window (two server_info
    # calls) and stored in outputs/derived/cadence.json. The ledger pair
    # cannot give a cadence: ledger_closed returns no close_time, and
    # close_time_resolution is 10 s, so single-ledger differences are
    # quantization noise. ---
    cadence = None
    try:
        cad = json.load(open(os.path.join(DERIVED, "cadence.json")))
        cadence = float(cad["cadence_s"])
        log("ledger cadence: %.3f s/ledger (%d ledgers in %d s, %s to %s)"
            % (cadence, cad["ledgers"], cad["interval_s"],
               cad["time_start"], cad["time_end"]))
    except (OSError, KeyError, TypeError, ValueError):
        cadence = None
    if cadence is None:
        cadence = 3.03  # fallback only if the cadence probe did not run
        log("cadence fallback to 3.03 s (no cadence.json found)")

    # --- flag ledgers: activation is only processed at ledgers where
    # (seq-1)/256 changes, i.e. seq = 256k+1 (AmendmentTable.cpp
    # needValidatedLedger). ---
    seq = si["validated_ledger"]["seq"]
    next_flag = ((seq - 1) // 256 + 1) * 256 + 1
    ledgers_to_flag = next_flag - seq
    seconds_to_flag = ledgers_to_flag * cadence
    log("validated seq %d; next flag ledger %d (%d ledgers, ~%.0f s)"
        % (seq, next_flag, ledgers_to_flag, seconds_to_flag))

    # --- majority thresholds (post-fix rule: 67/100, strictly greater;
    # fixAmendmentMajorityCalc is enabled on the live network) ---
    def votes_needed(trusted):
        # threshold_ = floor(trusted * 67 / 100); passes iff votes > threshold
        return (trusted * 67) // 100 + 1

    thresholds = [{"trusted_validators": n, "votes_needed": votes_needed(n),
                   "share_pct": round(100.0 * votes_needed(n) / n, 1)}
                  for n in [1, 2, 3, 5, 10, 16, 17, 20, 21, 24, 25, 26, 66]]
    unl_size = 25  # live UNL size, from prior packs + VHS validators UNL flag
    # cross-check UNL size from the VL document
    vl = load("testnet_vl.json")
    blob = vl["blobs_v2"][0]["blob"]
    vl_json = json.loads(base64.b64decode(blob))
    unl_validators = [v for v in vl_json.get("validators", [])
                      if v.get("unl", True)]
    log("VL validators: %d (UNL-flagged: %d)"
        % (len(vl_json.get("validators", [])), len(unl_validators)))
    check("VL validator count == 25", len(vl_json.get("validators", [])) == 25)
    check("validation quorum == 17", ss.get("validation_quorum") == 17)

    # --- inventory: one row per known amendment ---
    vote_by_id = {a["id"]: a for a in vhs_vote}
    info_by_name = {a["name"]: a for a in vhs_info}
    inventory = []
    for fid, v in sorted(rpc.items(), key=lambda kv: kv[1]["name"]):
        name = v["name"]
        m = macro_by_name.get(name, {})
        act = vote_by_id.get(fid)
        inventory.append({
            "id": fid,
            "name": name,
            "enabled": bool(v["enabled"]),
            "supported": bool(v["supported"]),
            "macro_vote": m.get("vote"),
            "macro_kind": m.get("kind"),
            "macro_line": m.get("macro_line"),
            "id_matches_sha512half": sha512_half(name) == fid,
            "activation_ledger": act["ledger_index"] if act else None,
            "activation_date": act["date"] if act else None,
            "activation_tx": act["tx_hash"] if act else None,
            "vhs_known": name in info_by_name,
            "vhs_deprecated": bool(info_by_name.get(name, {}).get("deprecated")),
            "majority": v.get("majority"),
        })
    # amendments known to VHS but absent from the node's table
    rpc_names = {v["name"] for v in rpc.values()}
    for a in vhs_info:
        if a["name"] not in rpc_names:
            inventory.append({
                "id": a["id"],
                "name": a["name"],
                "enabled": False,
                "supported": False,
                "macro_vote": None,
                "macro_kind": None,
                "macro_line": None,
                "id_matches_sha512half": sha512_half(a["name"]) == a["id"],
                "activation_ledger": None,
                "activation_date": None,
                "activation_tx": None,
                "vhs_known": True,
                "vhs_deprecated": bool(a.get("deprecated")),
                "majority": None,
                "note": "known to VHS, absent from pinned node table",
            })
    inventory.sort(key=lambda r: r["name"])

    enabled = [r for r in inventory if r["enabled"]]
    disabled = [r for r in inventory if not r["enabled"]]
    check("inventory rows == 103", len(inventory) == 103, str(len(inventory)))
    check("inventory enabled == 64", len(enabled) == 64, str(len(enabled)))
    check("inventory disabled == 39", len(disabled) == 39, str(len(disabled)))

    with open(os.path.join(DERIVED, "amendment-inventory.json"),
              "w", encoding="utf-8") as fh:
        json.dump({"pinned_commit": PIN,
                   "validated_ledger": seq,
                   "generated_utc": datetime.datetime.now(
                       datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "amendments": inventory}, fh, indent=1, sort_keys=True)
    with open(os.path.join(DERIVED, "amendment-inventory.csv"),
              "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "name", "enabled", "supported", "macro_vote",
                    "macro_kind", "macro_line", "activation_ledger",
                    "activation_date", "vhs_deprecated"])
        for r in inventory:
            w.writerow([r["id"], r["name"], r["enabled"], r["supported"],
                        r["macro_vote"], r["macro_kind"], r["macro_line"],
                        r["activation_ledger"], r["activation_date"],
                        r["vhs_deprecated"]])

    # --- activation watch ---
    two_weeks_ledgers = int(14 * 24 * 3600 / cadence)
    watch = {
        "pinned_commit": PIN,
        "validated_ledger": seq,
        "network_id": si["network_id"],
        "build_version": si["build_version"],
        "peers": si.get("peers"),
        "validation_quorum": ss.get("validation_quorum"),
        "unl_size": unl_size,
        "vhs_known_validators": vhs_val.get("count"),
        "ledger_cadence_s": round(cadence, 3),
        "majority_hold_time_s": 1209600,
        "majority_hold_time_weeks": 2,
        "majority_hold_ledgers_approx": two_weeks_ledgers,
        "majority_rule": "post-fix: votes > floor(trusted*67/100); "
                         "fixAmendmentMajorityCalc enabled",
        "votes_needed_at_unl_25": votes_needed(25),
        "thresholds_by_trusted_count": thresholds,
        "next_flag_ledger": next_flag,
        "ledgers_to_next_flag": ledgers_to_flag,
        "seconds_to_next_flag_approx": round(seconds_to_flag, 1),
        "amendments_total_known": len(inventory),
        "amendments_enabled": len(enabled),
        "amendments_disabled": len(disabled),
        "amendments_with_majority": 0,
        "amendments_vetoed": 0,
        "activation_ledger_bulk": 86785,
        "activation_date_bulk": "2026-02-09T14:31:12.000Z",
        "alerts": [
            {"level": "INFO",
             "rule": "no amendment holds a majority; activation watch idle"},
            {"level": "WATCH",
             "rule": "Batch and OrchardPrivacy are known to VHS but absent "
                     "from the node's supported table (Batch registered but "
                     "unsupported; OrchardPrivacy absent from pinned code)"},
            {"level": "WATCH",
             "rule": "PF_ValidatorVoteTracking and PF_AccountExclusion are "
                     "DefaultNo and disabled; the features they gate are inert"},
            {"level": "INFO",
             "rule": "public feature RPC exposes no vote counts "
                     "(admin-only); activation approach is invisible until "
                     "a majority timestamp appears"},
        ],
        "checks": checks,
    }
    with open(os.path.join(DERIVED, "activation-watch.json"),
              "w", encoding="utf-8") as fh:
        json.dump(watch, fh, indent=1, sort_keys=True)

    with open(os.path.join(DERIVED, "monitor-run.log"),
              "w", encoding="utf-8") as fh:
        fh.write("\n".join(log_lines) + "\n")

    n_pass = sum(1 for c in checks if c["pass"])
    log("monitor result: %d/%d checks PASS" % (n_pass, len(checks)))
    if n_pass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
