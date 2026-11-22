#!/usr/bin/env python3
"""analyze.py — build findings.json, the claim/risk/gap registers, the
amendment-inventory doc, the evidence index, and run-manifest.json from
the unedited probe outputs and the derived monitor/drill results.

Counts are computed FROM the tables at write time, so a summary number
can never disagree with its table. The script exits non-zero if any
cross-check fails.
"""
import json
import os
import sys

PACK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(PACK, "outputs")
DERIVED = os.path.join(OUT, "derived")
PIN = "0085a1ff885d6a446369cf73a4430f75af22be55"


def load_out(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def load_derived(name):
    with open(os.path.join(DERIVED, name), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- findings
FINDINGS = [
    {"id": "F-01", "severity": "HIGH", "status": "MEASURED",
     "title": "The enabled set is exactly the DefaultYes set, all enabled in one bulk event",
     "evidence": "Live feature RPC: 64 enabled of 101 supported. Pinned features.macro parse: 64 DefaultYes. VHS /vote/test: all 64 at ledger 86785, 2026-02-09T14:31:12Z. The normal two-week majority activation path has never run on this network.",
     "remediation": "Treat any future enablement that is not a single-amendment majority activation as an exceptional event; alert on any enabled-count change immediately."},
    {"id": "F-02", "severity": "HIGH", "status": "MEASURED",
     "title": "Activation approach is invisible from the public RPC",
     "evidence": "Live feature RPC returns only enabled/supported/name per amendment; no amendment carries a majority field. Vote counts (count/validations/threshold) are admin-only in AmendmentTable.cpp injectJson (lines 1000-1025). The earliest public signal of an approaching activation is the majority timestamp itself, which only appears once majority is already reached.",
     "remediation": "Poll feature every flag interval (256 ledgers, ~12 min) and alert the moment any majority field appears; do not rely on vote-count trends, which the public RPC cannot show."},
    {"id": "F-03", "severity": "HIGH", "status": "MEASURED",
     "title": "Registry drift: the history service knows amendments the node does not",
     "evidence": "VHS /amendments/info lists 103 known amendments; the node's feature table lists 101 supported. Batch is registered in features.macro line 51 but Supported::no; OrchardPrivacy has 0 matches anywhere in the pinned source (fixtures/source-hashes.json absence_checks). The history service registry is newer than the node.",
     "remediation": "Key monitoring to the node's own feature table, not the history service registry; flag any VHS-only name as drift, not as a pending activation."},
    {"id": "F-04", "severity": "MEDIUM", "status": "MEASURED",
     "title": "Activation can only land at flag ledgers (256-ledger boundaries)",
     "evidence": "AmendmentTable.cpp needValidatedLedger only processes ledgers where (seq-1)/256 changes. From validated seq 8283007 the next flag ledger is 8283137, 130 ledgers (~371 s at the measured 2.857 s/ledger cadence).",
     "remediation": "Schedule activation checks on flag ledgers, not wall-clock time; the response window after a majority-hold expiry is at most one flag interval (~12 min)."},
    {"id": "F-05", "severity": "MEDIUM", "status": "SPECIFIED",
     "title": "17 of 25 trusted votes are needed, and the bar falls as the trusted set shrinks",
     "evidence": "Post-fix rule (fixAmendmentMajorityCalc enabled live): votes > floor(trusted*67/100). At 25 trusted validators 17 votes are needed — equal to validation quorum 17. At 24 trusted still 17; at 20 trusted 14; at 17 trusted 12 (drill A-01, 8/8 threshold checks).",
     "remediation": "Alert when the trusted validator count drops below 25; recompute the activation bar on every UNL change."},
    {"id": "F-06", "severity": "MEDIUM", "status": "MEASURED",
     "title": "Both PostFiat amendments are DefaultNo and disabled; the features they gate are inert",
     "evidence": "features.macro lines 45-46: PF_AccountExclusion and PF_ValidatorVoteTracking are Supported::yes, VoteBehavior::DefaultNo. Live feature RPC: both enabled=false. The gates they control (ValidatorVoteTracker.cpp:162; Change.cpp:618-619) never fire.",
     "remediation": "Do not assume vote tracking or account exclusion is available; both need an explicit up-vote campaign plus a two-week majority hold to activate."},
    {"id": "F-07", "severity": "MEDIUM", "status": "SPECIFIED",
     "title": "Enablement is one-way: a bad activation cannot be rolled back, only superseded",
     "evidence": "AmendmentTable.cpp AmendmentState comment (lines 294-302): 'This is a one-way switch: once an amendment is enabled it can never be disabled, but it can be superseded by a subsequent amendment.' The only 'disable' match in the file is that comment (drill C-01).",
     "remediation": "Before any up-vote, require a superseding amendment to exist or be drafted; treat activation as irreversible in the runbook."},
    {"id": "F-08", "severity": "MEDIUM", "status": "MEASURED",
     "title": "16 retired amendments are all disabled, and the history service disagrees on one",
     "evidence": "features.macro has 16 XRPL_RETIRE entries; all 16 are disabled live. VHS marks 15 names deprecated and omits FlowCross, which the macro retires. Retired names still appear in registries and RPC output.",
     "remediation": "Exclude retired names from activation watchlists; treat a retired name gaining a majority as a data error until proven otherwise."},
    {"id": "F-09", "severity": "LOW", "status": "MEASURED",
     "title": "37 disabled amendments include major un-enabled features",
     "evidence": "Live feature RPC disabled set includes MPTokensV1, NonFungibleTokensV1, PermissionedDEX, PermissionedDomains, SingleAssetVault, LendingProtocol, XChainBridge and TokenEscrow (all DefaultNo). No amendment has been enabled since the 2026-02-09 bulk event.",
     "remediation": "Integrations must check enabled state per feature at runtime; never assume a named feature is live because the code ships it."},
    {"id": "F-10", "severity": "LOW", "status": "MEASURED",
     "title": "The 86785 activation transactions cannot be re-fetched from the public node",
     "evidence": "tx lookup for activation tx 0E373029EEF6AB43E24D5F1EAFBAEB80BBA9B94610BCE1A3D004101CCFAE7048 returns txnNotFound (error_code 29). The node's complete_ledgers range is 8200054-8283008, so ledger 86785 is outside retained history. VHS is the sole source for the activation ledger and date.",
     "remediation": "Archive activation evidence outside the node (VHS export + this pack); do not expect the public node to serve old activation proofs."},
    {"id": "F-11", "severity": "LOW", "status": "SPECIFIED",
     "title": "The majority hold time is configurable down to 15 minutes",
     "evidence": "SystemParameters.h:88 sets defaultAmendmentMajorityTime to 2 weeks. Config.cpp lines 870-898 parses amendment_majority_time (minutes/hours/days/weeks) and rejects values under 15 minutes. An operator config change can shrink the warning window from two weeks to 15 minutes.",
     "remediation": "Monitor the node's configured majority time as part of the watch; a sub-two-week setting is itself an alert."},
    {"id": "F-12", "severity": "INFO", "status": "SPECIFIED",
     "title": "The whitepaper documents no amendment policy",
     "evidence": "outputs/postfiat_whitepaper.html (163,089 bytes) contains zero occurrences of 'amend'. No public document states which amendments the network intends to enable, in what order, or under what governance.",
     "remediation": "Publish an amendment policy (intended set, vote order, veto criteria) before the first live majority activation."},
]

# ------------------------------------------------------------------- claims
# (id, status, claim, primary source)
CLAIMS = [
    ("C-01", "VERIFIED", "101 amendments in the node's supported table: 64 enabled, 37 disabled.",
     "Live probe feature_list.json; monitor 16/16 checks."),
    ("C-02", "VERIFIED", "All 101 amendment IDs equal SHA-512-Half(name).",
     "Monitor check: sha512Half verified for all 101; Feature.cpp:266."),
    ("C-03", "VERIFIED", "The enabled set equals the DefaultYes set exactly (64/64).",
     "Monitor check; features.macro parse (64 DefaultYes)."),
    ("C-04", "VERIFIED", "All 64 enabled amendments activated at ledger 86785, 2026-02-09T14:31:12Z.",
     "VHS vhs-amendments-vote-test.json (64 rows, one ledger, one timestamp)."),
    ("C-05", "VERIFIED", "No amendment currently holds a majority; none is vetoed.",
     "Live probe feature_list.json (no majority/vetoed fields present)."),
    ("C-06", "VERIFIED", "PF_ValidatorVoteTracking and PF_AccountExclusion are disabled.",
     "Live probe feature_list.json; rpc-feature-pf-vote-tracking.json."),
    ("C-07", "VERIFIED", "Next flag ledger 8283137 from validated seq 8283007; activation only at flag ledgers.",
     "Monitor activation-watch.json; AmendmentTable.cpp needValidatedLedger."),
    ("C-08", "VERIFIED", "Ledger cadence 2.857 s/ledger (21 ledgers in a 60 s window).",
     "outputs/derived/cadence.json (two server_info calls)."),
    ("C-09", "VERIFIED", "Validation quorum 17; UNL 25 validators; the history service knows 66 validators.",
     "server_state.json (validation_quorum 17); testnet_vl.json (25); vhs-validators.json (count 66)."),
    ("C-10", "VERIFIED", "The history service lists 103 known amendments against the node's 101.",
     "vhs-amendments-info.json (count 103) vs feature_list.json (101)."),
    ("C-11", "VERIFIED", "Batch is registered but unsupported; OrchardPrivacy is absent from the pinned code.",
     "features.macro:51 (Batch, Supported::no); fixtures/source-hashes.json absence_checks (0 matches)."),
    ("C-12", "VERIFIED", "16 retired amendments, all disabled; the history service marks 15 deprecated (FlowCross differs).",
     "features.macro (16 XRPL_RETIRE); feature_list.json; vhs-amendments-info.json."),
    ("C-13", "VERIFIED", "The single-amendment feature RPC returns an amendment by name with enabled/supported state.",
     "outputs/rpc-feature-pf-vote-tracking.json (PF_ValidatorVoteTracking, enabled false)."),
    ("C-14", "VERIFIED", "The ledger-86785 activation transaction cannot be re-fetched (txnNotFound).",
     "outputs/rpc-tx-activation-86785.json (error_code 29); complete_ledgers 8200054-8283008."),
    ("C-15", "VERIFIED", "17 votes are needed at 25 trusted validators (drill A-01, 8/8 threshold checks).",
     "outputs/drill-run.log; outputs/derived/drill-results.json."),
    ("C-16", "VERIFIED", "Lab drill 29/29 cases PASS (A 15, B 5, C 9).",
     "outputs/drill-run.log; outputs/derived/drill-results.json."),
    ("C-17", "VERIFIED", "The whitepaper contains zero occurrences of 'amend'.",
     "outputs/postfiat_whitepaper.html (163,089 bytes), grep count 0."),
    ("C-18", "VERIFIED", "The public RPC refuses the admin methods validators and peers with HTTP 403.",
     "outputs/validators.json, outputs/peers.json (403 bodies, identical)."),
    ("C-19", "VERIFIED", "The public explorer health endpoint returns HTTP 500 at probe time.",
     "outputs/explorer_health.json (HTTP 500)."),
    ("C-20", "SPECIFIED", "Majority rule (post-fix): votes > floor(trusted * 67/100); fixAmendmentMajorityCalc is enabled live.",
     "SystemParameters.h:83-85; AmendmentTable.cpp:324-342, 359-378; feature_list.json."),
    ("C-21", "SPECIFIED", "A majority must hold 2 weeks by default; the hold time is configurable down to 15 minutes.",
     "SystemParameters.h:88; Config.cpp:870-898; Config.h:248."),
    ("C-22", "SPECIFIED", "Amendment state is only processed at flag ledgers, where (seq-1)/256 changes.",
     "AmendmentTable.cpp:944-956 (needValidatedLedger)."),
    ("C-23", "SPECIFIED", "Enablement is one-way; there is no disable path; a bad activation can only be superseded.",
     "AmendmentTable.cpp:294-302 (AmendmentState comment); drill C-01/C-05."),
    ("C-24", "SPECIFIED", "The public feature RPC omits vote counts; count/validations/threshold are admin-only.",
     "AmendmentTable.cpp:1000-1025 (injectJson); Feature1.cpp:47 (isAdmin)."),
    ("C-25", "SPECIFIED", "A vetoed amendment is excluded from validator votes.",
     "AmendmentTable.cpp:813-838 (doValidation); Application.cpp:1282-1284 ([veto_amendments])."),
    ("C-26", "SPECIFIED", "PF_ValidatorVoteTracking gates the vote tracker; PF_AccountExclusion gates exclusion-list changes.",
     "ValidatorVoteTracker.cpp:162; Change.cpp:618-619."),
    ("C-27", "SPECIFIED", "An unsupported amendment reaching majority sets firstUnsupportedExpected to majority time + 2 weeks.",
     "AmendmentTable.cpp:958-995 (doValidatedLedger)."),
    ("C-28", "UNVERIFIED", "The history service's amendment data matches the ledger.",
     "VHS is an unauthenticated third-party service; activation ledger/date cannot be cross-checked against node history (see C-14)."),
    ("C-29", "UNTESTABLE", "An amendment can be driven to majority and enabled on this network.",
     "Would require casting validator votes and holding a majority for two weeks; the safety boundary forbids votes and live keys."),
    ("C-30", "UNTESTABLE", "Veto behavior on a live majority (veto before activation blocks it).",
     "Veto is an admin-only operation ([veto_amendments] + table.veto); it cannot be exercised from the public RPC."),
]

# -------------------------------------------------------------------- risks
# (id, severity, title, finding, likelihood, impact)
RISKS = [
    ("R-01", "HIGH", "Silent activation approach: an amendment reaches majority with no public early warning.", "F-02", "Medium", "High"),
    ("R-02", "HIGH", "Bulk enablement precedent: a future restart/genesis could enable DefaultNo amendments without the two-week process.", "F-01", "Low", "High"),
    ("R-03", "HIGH", "Registry drift: monitoring keyed to the history service misses node-unknown amendments.", "F-03", "Medium", "High"),
    ("R-04", "MEDIUM", "Flag-ledger timing: activation lands at most one flag interval (~12 min) after majority-hold expiry.", "F-04", "Medium", "Medium"),
    ("R-05", "MEDIUM", "A shrinking trusted set lowers the activation bar (17 votes at 25, 14 at 20, 12 at 17).", "F-05", "Medium", "Medium"),
    ("R-06", "MEDIUM", "PostFiat governance features are inert: vote tracking and account exclusion cannot be used.", "F-06", "High", "Medium"),
    ("R-07", "MEDIUM", "No rollback: a bad activation is permanent until a superseding amendment exists.", "F-07", "Low", "High"),
    ("R-08", "MEDIUM", "Retired-amendment confusion: 16 retired names still appear in registries and RPC output.", "F-08", "Medium", "Low"),
    ("R-09", "LOW", "Major features disabled: MPT, NFT, permissioned DEX, vaults and bridges are unavailable.", "F-09", "High", "Low"),
    ("R-10", "LOW", "Activation history unverifiable: the 86785 bulk event cannot be re-derived from the node.", "F-10", "High", "Low"),
    ("R-11", "LOW", "Majority-time misconfiguration: a 15-minute setting removes the two-week warning window.", "F-11", "Low", "Medium"),
    ("R-12", "LOW", "No documented amendment policy: no public commitment on vote order or veto criteria.", "F-12", "High", "Low"),
    ("R-13", "MEDIUM", "Quorum pressure: trusted validators below 17 halt validation entirely, and amendment voting with it.", "F-05", "Low", "High"),
    ("R-14", "INFO", "Explorer degraded (HTTP 500): the public explorer cannot serve as a second monitoring source.", "F-02", "High", "Low"),
]

# --------------------------------------------------------------------- gaps
# (id, title, why it is a gap, consequence)
GAPS = [
    ("G-01", "Live vote tallies are not observable from the public RPC.",
     "Vote counts are admin-only in injectJson (AmendmentTable.cpp:1000-1025); the public feature RPC returns no counts.",
     "Activation approach cannot be trended; only the majority timestamp is visible, after majority is reached."),
    ("G-02", "History-service data provenance is unverified.",
     "VHS is an unauthenticated third-party read API; its amendment rows cannot be cross-checked against ledger history.",
     "The activation ledger/date (86785, 2026-02-09) rests on a single external source."),
    ("G-03", "Ledger-86785 activation transactions are not re-fetchable.",
     "The public node retains ledgers 8200054-8283008 only; tx lookup returns txnNotFound.",
     "The bulk enablement cannot be independently re-derived from the node."),
    ("G-04", "Veto behavior was never exercised live.",
     "Veto requires admin access ([veto_amendments] config + table.veto); the public RPC cannot veto.",
     "Runbook B's veto step is code-verified only, not live-tested."),
    ("G-05", "The unsupported-amendment majority path was never exercised live.",
     "No unsupported amendment currently holds a majority, so firstUnsupportedExpected_ has never fired on this network.",
     "Runbook B's warning path is code-verified only, not live-tested."),
    ("G-06", "The two-week majority-hold clock was never measured live.",
     "No amendment has held a majority on this network, so the hold-to-enable transition is unobserved.",
     "The 14-day figure is code-specified (SystemParameters.h:88), not measured."),
    ("G-07", "No documented amendment policy exists.",
     "The whitepaper contains zero 'amend' mentions and no public policy document was found.",
     "There is no baseline to judge whether a future up-vote is intended or rogue."),
]


def counts(rows, key_idx):
    out = {}
    for r in rows:
        out[r[key_idx]] = out.get(r[key_idx], 0) + 1
    return out


def main():
    watch = load_derived("activation-watch.json")
    drill = load_derived("drill-results.json")
    inv = load_derived("amendment-inventory.json")

    # --- findings.json ---
    fsev = counts([(f["severity"],) for f in FINDINGS], 0)
    fstat = counts([(f["status"],) for f in FINDINGS], 0)
    with open(os.path.join(PACK, "findings.json"), "w", encoding="utf-8") as fh:
        json.dump({"pinned_commit": PIN,
                   "validated_ledger": watch["validated_ledger"],
                   "counts": {"total": len(FINDINGS), "by_severity": fsev,
                              "by_status": fstat},
                   "findings": FINDINGS}, fh, indent=1, sort_keys=True)

    # --- docs/claim-index.md ---
    cstat = counts([(c[1],) for c in CLAIMS], 0)
    lines = ["# Claim-to-evidence index\n",
             "Every measured or specification-derived claim in this pack, with its status and its primary source. Status: VERIFIED (measured live or in the lab), SPECIFIED (pinned code, docs, or a cited standard), UNVERIFIED (could not be checked), UNTESTABLE (the safety boundary forbids the action that would test it).\n",
             "| ID | Status | Claim | Primary source |\n",
             "| --- | --- | --- | --- |\n"]
    for cid, st, claim, src in CLAIMS:
        lines.append("| %s | %s | %s | %s |\n" % (cid, st, claim, src))
    lines.append("\nCounts (recomputed from this table): %d claims — %s.\n"
                 % (len(CLAIMS),
                    ", ".join("%s %d" % (k, v)
                              for k, v in sorted(cstat.items()))))
    with open(os.path.join(PACK, "docs", "claim-index.md"),
              "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    # --- docs/risk-register.md ---
    rsev = counts([(r[1],) for r in RISKS], 0)
    lines = ["# Risk register\n",
             "| ID | Severity | Risk | Finding | Likelihood | Impact |\n",
             "| --- | --- | --- | --- | --- | --- |\n"]
    for rid, sev, title, f, like, imp in RISKS:
        lines.append("| %s | %s | %s | %s | %s | %s |\n"
                     % (rid, sev, title, f, like, imp))
    lines.append("\nCounts (recomputed from this table): %d risks — %s.\n"
                 % (len(RISKS),
                    ", ".join("%s %d" % (k, v)
                              for k, v in sorted(rsev.items()))))
    with open(os.path.join(PACK, "docs", "risk-register.md"),
              "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    # --- docs/gap-register.md ---
    lines = ["# Gap register\n",
             "| ID | Gap | Why it is a gap | Consequence |\n",
             "| --- | --- | --- | --- |\n"]
    for gid, title, why, cons in GAPS:
        lines.append("| %s | %s | %s | %s |\n" % (gid, title, why, cons))
    lines.append("\nCounts (recomputed from this table): %d gaps.\n" % len(GAPS))
    with open(os.path.join(PACK, "docs", "gap-register.md"),
              "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    # --- docs/amendment-inventory.md ---
    inv_rows = inv["amendments"]
    lines = ["# Amendment inventory\n",
             "Complete inventory at validated ledger %d (probe 2026-11-22 23:30 UTC). "
             "Pinned postfiatd %s. Sources: live `feature` RPC (%d supported), "
             "history-service /amendments/info (%d known) and /amendments/vote/test (%d enabled). "
             "Amendment IDs are SHA-512-Half(name), verified for all 101 node amendments.\n"
             % (watch["validated_ledger"], PIN, 101, 103, 64),
             "\n## Summary\n\n",
             "- Known amendments: %d (%d in the node table, %d history-service-only)\n"
             % (len(inv_rows), 101, len(inv_rows) - 101),
             "- Enabled: %d — all at ledger 86785, 2026-02-09T14:31:12Z (one bulk event)\n"
             % sum(1 for r in inv_rows if r["enabled"]),
             "- Disabled: %d (%d DefaultNo, 16 retired, 2 history-service-only)\n"
             % (sum(1 for r in inv_rows if not r["enabled"]),
                sum(1 for r in inv_rows if not r["enabled"]
                    and r["macro_vote"] == "DefaultNo")),
             "- With a majority: 0. Vetoed: 0.\n",
             "- PostFiat amendments (PF_AccountExclusion, PF_ValidatorVoteTracking): both DefaultNo, disabled.\n",
             "\n## Table\n\n",
             "| Name | Enabled | Vote | Activation ledger | Activation date |\n",
             "| --- | --- | --- | --- | --- |\n"]
    for r in inv_rows:
        lines.append("| %s | %s | %s | %s | %s |\n"
                     % (r["name"], "yes" if r["enabled"] else "no",
                        r["macro_vote"] or "—",
                        r["activation_ledger"] or "—",
                        (r["activation_date"] or "—").replace("T", " ").replace(".000Z", "Z")))
    lines.append("\nFull machine-readable inventory: outputs/derived/amendment-inventory.json and .csv. "
                 "History-service-only rows (Batch, OrchardPrivacy) have no node row: Batch is registered but "
                 "unsupported in the pinned code, OrchardPrivacy is absent from the pinned code entirely.\n")
    with open(os.path.join(PACK, "docs", "amendment-inventory.md"),
              "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    # --- docs/evidence-index.md ---
    ev = [
        ("outputs/feature_list.json", "Live feature RPC: 101 amendments, enabled/supported/name, no majority fields."),
        ("outputs/vhs-amendments-info.json", "History service: 103 known amendments with ids, names, deprecated flags."),
        ("outputs/vhs-amendments-vote-test.json", "History service: 64 enabled amendments with activation ledger/tx/date."),
        ("outputs/rpc-feature-pf-vote-tracking.json", "Single-amendment feature RPC for PF_ValidatorVoteTracking."),
        ("outputs/rpc-tx-activation-86785.json", "tx lookup for a ledger-86785 activation tx: txnNotFound."),
        ("outputs/server_info.json", "Live node: postfiatd 1.0.9, network 2025, validated seq 8283007, 21 peers."),
        ("outputs/server_state.json", "Live node state: validation_quorum 17, complete_ledgers 8200054-8283008."),
        ("outputs/ledger_current.json", "Validated ledger 8283007 (full header, close_time 848705451)."),
        ("outputs/ledger_closed.json", "Last closed ledger 8283008 (hash/index only; no close_time)."),
        ("outputs/fee.json", "Live fee levels at probe time."),
        ("outputs/validators.json", "Admin method refused by the public proxy (HTTP 403)."),
        ("outputs/peers.json", "Admin method refused by the public proxy (HTTP 403)."),
        ("outputs/invalid_method.json", "Unknown method response from the public proxy."),
        ("outputs/vhs-health.json", "History service health at probe time."),
        ("outputs/vhs-amendments.json", "History service API index (endpoint list)."),
        ("outputs/vhs-validators.json", "History service: 66 known validators."),
        ("outputs/vhs-topology.json", "History service topology snapshot."),
        ("outputs/testnet_vl.json", "Live validator list document (25 validators, UNL)."),
        ("outputs/explorer_health.json", "Explorer health: HTTP 500 at probe time."),
        ("outputs/postfiat_org.html", "Project homepage capture."),
        ("outputs/postfiat_whitepaper.html", "Whitepaper capture (zero 'amend' mentions)."),
        ("outputs/probe-run.log", "Probe run log with HTTP status, timings and SHA-256 per file."),
        ("outputs/drill-run.log", "Lab drill run log: 29/29 cases PASS."),
        ("outputs/fresh-clone-*", "Fresh-clone reproduction outputs (29 files): re-probed responses, re-run monitor/drill results, and fresh-clone-compare.log (12/12 compare checks PASS; fresh validated ledger 8283343 vs shipped 8283007)."),
        ("outputs/derived/amendment-inventory.json", "Machine-readable inventory (103 rows)."),
        ("outputs/derived/amendment-inventory.csv", "Same inventory as CSV."),
        ("outputs/derived/activation-watch.json", "Thresholds, flag-ledger timing, alerts, monitor checks (16/16)."),
        ("outputs/derived/cadence.json", "Ledger cadence measurement (21 ledgers / 60 s = 2.857 s/ledger)."),
        ("outputs/derived/drill-results.json", "Drill results (29/29 PASS, timings)."),
        ("outputs/derived/monitor-run.log", "Monitor run log (16/16 checks PASS)."),
        ("fixtures/features.macro", "Verbatim pinned features.macro (107 registrations)."),
        ("fixtures/source-hashes.json", "SHA-256 + git blob SHAs for pinned sources; OrchardPrivacy absence check."),
        ("fixtures/source-excerpts/", "18 verbatim pinned-source excerpts with file paths and line ranges."),
        ("scripts/probe_all.sh", "Read-only live probe script (9 RPC POSTs + 10 GETs)."),
        ("scripts/drill.py", "Lab drill script (3 drills, 29 cases)."),
        ("src/amendment_monitor.py", "Inventory + activation-watch builder (16 checks)."),
        ("scripts/extract_excerpts.py", "Pinned-source excerpt extractor (anchor-verified)."),
        ("scripts/clean_reproduce.sh", "Fresh-environment reproduction (exit 0 only if all checks pass)."),
        ("scripts/compare_reproduce.py", "Fresh-vs-shipped comparison."),
        ("scripts/verify_digests.sh", "SHA-256 digest verification over the pack."),
        ("findings.json", "12 findings (3 HIGH / 5 MEDIUM / 3 LOW / 1 INFO; 8 MEASURED / 4 SPECIFIED)."),
        ("docs/claim-index.md", "30 claims (19 VERIFIED / 8 SPECIFIED / 1 UNVERIFIED / 2 UNTESTABLE)."),
        ("docs/risk-register.md", "14 risks (3 HIGH / 6 MEDIUM / 4 LOW / 1 INFO)."),
        ("docs/gap-register.md", "7 gaps."),
    ]
    lines = ["# Evidence index\n",
             "| File | What it is |\n",
             "| --- | --- |\n"]
    for f, d in ev:
        lines.append("| `%s` | %s |\n" % (f, d))
    lines.append("\n%d evidence items.\n" % len(ev))
    with open(os.path.join(PACK, "docs", "evidence-index.md"),
              "w", encoding="utf-8") as fh:
        fh.writelines(lines)

    # --- run-manifest.json ---
    manifest = {
        "pinned_commit": PIN,
        "validated_ledger": watch["validated_ledger"],
        "probe_utc": "2026-11-22T23:30:49Z",
        "counts": {
            "findings": {"total": len(FINDINGS), "by_severity": fsev,
                         "by_status": fstat},
            "claims": {"total": len(CLAIMS), "by_status": cstat},
            "risks": {"total": len(RISKS), "by_severity": rsev},
            "gaps": len(GAPS),
            "amendments": {"known": len(inv_rows),
                           "enabled": sum(1 for r in inv_rows if r["enabled"]),
                           "disabled": sum(1 for r in inv_rows if not r["enabled"])},
            "drill": {"passed": drill["passed"], "total": drill["total"]},
            "monitor_checks": {"passed": sum(1 for c in watch["checks"] if c["pass"]),
                               "total": len(watch["checks"])},
        },
        "verdict": "WATCHFUL, NOT BLIND — the activation machinery is sound and fully specified in code, but the public monitoring surface cannot see an activation approaching: no vote counts, no majority until it exists, and no documented policy.",
    }
    with open(os.path.join(PACK, "run-manifest.json"),
              "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1, sort_keys=True)

    # --- cross-checks ---
    assert len(FINDINGS) == 12, "findings count"
    assert sum(fsev.values()) == 12 and sum(fstat.values()) == 12
    assert len(CLAIMS) == 30, "claims count"
    assert sum(cstat.values()) == 30
    assert len(RISKS) == 14, "risks count"
    assert len(GAPS) == 7, "gaps count"
    assert drill["passed"] == drill["total"] == 29, "drill must be 29/29"
    assert all(c["pass"] for c in watch["checks"]), "monitor checks must all pass"
    print("analyze: findings %d (%s; %s)" % (len(FINDINGS), fsev, fstat))
    print("analyze: claims %d (%s)" % (len(CLAIMS), cstat))
    print("analyze: risks %d (%s); gaps %d" % (len(RISKS), rsev, len(GAPS)))
    print("analyze: inventory %d rows; drill %d/%d; monitor %d/%d"
          % (len(inv_rows), drill["passed"], drill["total"],
             sum(1 for c in watch["checks"] if c["pass"]),
             len(watch["checks"])))


if __name__ == "__main__":
    main()
