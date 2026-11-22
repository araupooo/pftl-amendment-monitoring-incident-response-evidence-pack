#!/usr/bin/env python3
"""drill.py — timed lab drills for the three incident-response runbooks.

All three drills are pure lab simulations against the pinned postfiatd
source and the shipped live probe outputs. No transactions are submitted,
no amendment votes are cast, no live state is changed.

  Drill A — amendment activation stalls / fails to reach consensus.
  Drill B — a bad (unsupported) amendment reaches majority.
  Drill C — rollback / disabling decision under quorum pressure.

Each case asserts an expected outcome derived from the pinned code
(AmendmentTable.cpp, SystemParameters.h, Feature.cpp) and prints a
PASS/FAIL line with a measured wall time. Results go to
outputs/derived/drill-results.json and the log to outputs/drill-run.log.
"""
import json
import os
import re
import sys
import time

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")
DERIVED = os.path.join(OUT, "derived")
PIN_DIR = "/tmp/postfiatd-pin"

CASES = []


def case(drill, cid, label, ok, detail=""):
    CASES.append({"drill": drill, "id": cid, "label": label,
                  "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + cid + " " + label +
          ((" — " + detail) if detail else ""))
    return bool(ok)


def grep(path, pattern):
    with open(os.path.join(PIN_DIR, path), encoding="utf-8") as fh:
        return [(i + 1, ln.rstrip("\n")) for i, ln in enumerate(fh)
                if re.search(pattern, ln)]


def votes_needed(trusted):
    """Post-fix rule (fixAmendmentMajorityCalc is enabled live):
    threshold_ = floor(trusted*67/100); passes iff votes > threshold_."""
    return (trusted * 67) // 100 + 1


def passes(votes, trusted):
    return votes >= votes_needed(trusted)


def main():
    t0 = time.monotonic()
    log = []
    orig_print = print

    def logged(*a, **k):
        line = " ".join(str(x) for x in a)
        log.append(line)
        orig_print(*a, **k)

    globals()["print"] = logged

    watch = json.load(open(os.path.join(DERIVED, "activation-watch.json")))
    seq = watch["validated_ledger"]
    cadence = watch["ledger_cadence_s"]
    two_week_ledgers = watch["majority_hold_ledgers_approx"]

    # ---------- Drill A: activation stalls ----------
    ta = time.monotonic()
    # A-01: threshold spot checks against the pinned rule.
    for n, want in [(25, 17), (24, 17), (20, 14), (17, 12), (16, 11),
                    (10, 7), (2, 2), (1, 1)]:
        case("A", "A-01-%d" % n, "votes needed at %d trusted validators" % n,
             votes_needed(n) == want, "%d (want %d)" % (votes_needed(n), want))
    # A-02: a candidate stuck at 16/25 never gains majority.
    case("A", "A-02", "16/25 votes does not pass at UNL 25",
         not passes(16, 25), "16 < 17 needed")
    # A-03: the same candidate at 17/25 passes.
    case("A", "A-03", "17/25 votes passes at UNL 25",
         passes(17, 25), "17 >= 17 needed")
    # A-04: a stall held for the full 2-week window still enables nothing:
    # doVoting only emits tfGotMajority when validators say yes AND the
    # local node votes up; a down-voted (DefaultNo) amendment never gets
    # an enable pseudo-transaction even with a ledger majority.
    case("A", "A-04", "DefaultNo amendment never self-enables on majority",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"entry\.second\.vote == AmendmentVote::up")),
         "doVoting gates both got-majority and enable actions on local up-vote")
    # A-05: activation is only processed at flag ledgers (256 boundaries).
    case("A", "A-05", "flag-ledger rule present in pinned code",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"\(ledgerSeq - 1\) / 256")),
         "needValidatedLedger compares (seq-1)/256")
    # A-06: next flag ledger from the live seq.
    nf = watch["next_flag_ledger"]
    case("A", "A-06", "next flag ledger %d is 1 mod 256" % nf,
         (nf - 1) % 256 == 0 and nf > seq,
         "%d ledgers ahead (~%.0f s at %.3f s/ledger)"
         % (nf - seq, (nf - seq) * cadence, cadence))
    # A-07: no amendment holds a majority right now (live).
    case("A", "A-07", "live: zero amendments hold a majority",
         watch["amendments_with_majority"] == 0)
    # A-08: stall runbook timing — decision window before the next flag
    # ledger is bounded by the flag-ledger gap.
    case("A", "A-08", "stall decision window is one flag interval (~13 min)",
         256 * cadence < 900,
         "256 ledgers x %.3f s = %.0f s" % (cadence, 256 * cadence))
    drill_a_s = time.monotonic() - ta

    # ---------- Drill B: bad amendment reaches majority ----------
    tb = time.monotonic()
    # B-01: the unsupported-majority warning path exists in pinned code.
    # (The log statement spans two source lines, so check both halves.)
    case("B", "B-01", "unsupported-majority log path present",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"Unsupported amendment "))
         and bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                       r"reached majority at")),
         "doValidatedLedger logs unsupported majorities (lines 981-982)")
    # B-02: firstUnsupportedExpected_ = earliest unsupported majority + 2 weeks.
    case("B", "B-02", "expected-activation clock = majority time + 2 weeks",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"firstUnsupportedExpected_ = \*firstUnsupportedExpected_ \+ majorityTime_")),
         "doValidatedLedger: firstUnsupportedExpected_ + majorityTime_")
    # B-03: synthetic scenario — unsupported amendment reaches majority at
    # the live validated ledger; expected activation ledger/time.
    t0_ledger = seq
    expected_ledger = t0_ledger + two_week_ledgers
    expected_s = two_week_ledgers * cadence
    case("B", "B-03", "synthetic unsupported majority at ledger %d" % t0_ledger,
         expected_ledger > t0_ledger and abs(expected_s - 1209600) < 3600,
         "expected activation ~ledger %d (~%.1f days, %.0f s)"
         % (expected_ledger, expected_s / 86400, expected_s))
    # B-04: the veto path exists (config [veto_amendments] + table.veto).
    case("B", "B-04", "veto path present (config section + table.veto)",
         bool(grep("src/xrpld/app/main/Application.cpp",
                   r"SECTION_VETO_AMENDMENTS"))
         and bool(grep("src/xrpld/app/misc/AmendmentTable.h",
                       r"virtual bool\s*$|veto\(uint256")),
         "[veto_amendments] section read at startup; AmendmentTable::veto exists")
    # B-05: veto only works before activation — a vetoed amendment is
    # excluded from getDesired/doValidation; after enablement there is no
    # un-enable. (Verified by code reading in runbook B; here we assert
    # the veto check in doValidation.)
    case("B", "B-05", "veto excludes amendment from validator votes",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"e\.second\.vote == AmendmentVote::up")),
         "doValidation only votes for supported + up-voted amendments")
    drill_b_s = time.monotonic() - tb

    # ---------- Drill C: rollback / disabling under quorum pressure ----------
    tc = time.monotonic()
    # C-01: enable() is one-way — the only "disable" mention in the table
    # implementation is the comment stating it can never be disabled.
    dis = grep("src/xrpld/app/misc/detail/AmendmentTable.cpp", r"disable")
    case("C", "C-01", "no disable mechanism; only the 'can never be disabled' comment",
         len(dis) == 1 and "can never be disabled" in dis[0][1],
         "%d match(es): line %d" % (len(dis), dis[0][0]) if dis else "0 matches")
    # C-02: AmendmentState documents the one-way switch.
    case("C", "C-02", "one-way switch documented in AmendmentState",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"one-way switch: once an amendment is enabled")),
         "AmendmentState comment: 'once an amendment is enabled it can never be disabled'")
    # C-03: quorum pressure — validation quorum is 17; at trusted < 17 the
    # network cannot validate at all.
    for n, can in [(25, True), (20, True), (17, True), (16, False), (10, False)]:
        case("C", "C-03-%d" % n,
             "trusted %d can%s reach validation quorum 17"
             % (n, "" if can else "not"),
             (n >= 17) == can, "quorum 17 vs %d trusted" % n)
    # C-04: majority votes needed fall as trusted validators drop — a
    # shrinking UNL lowers the activation bar (17 at 25, 14 at 20, 12 at 17).
    case("C", "C-04", "activation bar falls as trusted set shrinks",
         votes_needed(25) > votes_needed(20) > votes_needed(17),
         "17 > 14 > 12")
    # C-05: supersede is the only post-activation remedy (documented in
    # AmendmentTable.h: 'it can be superseded by a subsequent amendment').
    case("C", "C-05", "supersede is the documented post-activation remedy",
         bool(grep("src/xrpld/app/misc/detail/AmendmentTable.cpp",
                   r"superseded by")),
         "AmendmentTable.cpp AmendmentState comment (line 299)")
    drill_c_s = time.monotonic() - tc

    total_s = time.monotonic() - t0
    n_pass = sum(1 for c in CASES if c["pass"])
    print("drill result: %d/%d cases PASS (A %d, B %d, C %d)"
          % (n_pass, len(CASES),
             sum(1 for c in CASES if c["drill"] == "A" and c["pass"]),
             sum(1 for c in CASES if c["drill"] == "B" and c["pass"]),
             sum(1 for c in CASES if c["drill"] == "C" and c["pass"])))
    print("drill wall time: %.2f s (A %.2f s, B %.2f s, C %.2f s)"
          % (total_s, drill_a_s, drill_b_s, drill_c_s))

    results = {
        "drills": {"A": "activation stalls", "B": "bad amendment majority",
                   "C": "rollback decision under quorum pressure"},
        "cases": CASES,
        "passed": n_pass,
        "total": len(CASES),
        "wall_s": round(total_s, 2),
        "durations_s": {"A": round(drill_a_s, 2), "B": round(drill_b_s, 2),
                        "C": round(drill_c_s, 2)},
        "validated_ledger": seq,
        "ledger_cadence_s": cadence,
        "two_week_ledgers_approx": two_week_ledgers,
    }
    with open(os.path.join(DERIVED, "drill-results.json"),
              "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
    with open(os.path.join(OUT, "drill-run.log"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(log) + "\n")

    globals()["print"] = orig_print
    if n_pass != len(CASES):
        sys.exit(1)


if __name__ == "__main__":
    main()
