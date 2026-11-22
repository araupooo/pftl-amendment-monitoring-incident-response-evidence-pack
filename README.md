# PFTL Amendment Monitoring and Incident-Response Evidence Pack

## Verdict

**WATCHFUL, NOT BLIND.** The activation machinery is sound and fully
specified in code, but the public monitoring surface cannot see an
activation approaching: no vote counts, no majority until it exists,
and no documented policy.

## Headline numbers (live, 2026-11-22 23:30–23:39 UTC)

- Node: postfiatd 1.0.9, network 2025, validated ledger 8,283,007,
  21 peers, validation quorum 17, UNL 25 validators.
- Amendments: 101 in the node table (64 enabled, 37 disabled); 103
  known to the history service; 107 registered in the pinned code.
- All 64 enabled amendments activated in one bulk event at ledger
  86785, 2026-02-09T14:31:12Z. No amendment has ever activated through
  the normal two-week majority process on this network.
- No amendment currently holds a majority; none is vetoed.
- Both PostFiat amendments (PF_ValidatorVoteTracking,
  PF_AccountExclusion) are DefaultNo and disabled.
- Ledger cadence 2.857 s/ledger (21 ledgers / 60 s). Next flag ledger
  8283137 (~371 s from probe).
- Majority rule: votes > floor(trusted × 67/100) — 17 of 25 at the
  current UNL. Majority must hold two weeks; activation lands only at
  flag ledgers (every 256 ledgers). Enablement is one-way.
- Lab drill: 29/29 cases PASS (A 15, B 5, C 9). Monitor: 16/16 checks
  PASS.
- Findings: 12 (3 HIGH / 5 MEDIUM / 3 LOW / 1 INFO; 8 MEASURED /
  4 SPECIFIED). Claims: 30 (19 VERIFIED / 8 SPECIFIED / 1 UNVERIFIED /
  2 UNTESTABLE). Risks: 14. Gaps: 7.

## Pinned source

postfiatd commit `0085a1ff885d6a446369cf73a4430f75af22be55` (2026-10-10,
PR #50 merge, v1.0.9). Verified from a local checkout
(`git rev-parse HEAD`). Every cited line number was verified with
`grep -n` on that checkout.

## Contents

- `docs/decision-memo.md` — verdict, reasoning, next steps.
- `docs/amendment-inventory.md` — the complete inventory (103 rows) with
  enabled state, vote behavior, activation ledger/date.
- `docs/monitoring-spec.md` — what to watch, thresholds, 8 alert rules.
- `docs/runbook-a.md` — activation stalls / fails to reach consensus.
- `docs/runbook-b.md` — a bad amendment reaches majority.
- `docs/runbook-c.md` — rollback / disabling decision under quorum pressure.
- `docs/methodology.md` — how every number was produced, boundaries.
- `docs/claim-index.md` — 30 claims with status and primary source.
- `docs/risk-register.md` — 14 risks. `docs/gap-register.md` — 7 gaps.
- `docs/evidence-index.md` — every file and what it is.
- `docs/citations.md` — pinned-source and live-source citations.
- `src/amendment_monitor.py` — inventory + activation-watch builder.
- `scripts/drill.py` — the three timed lab drills (29 cases).
- `scripts/probe_all.sh` — read-only live probes (13 RPC POSTs, 10 GETs).
- `scripts/extract_excerpts.py` — pinned-source excerpt extractor.
- `fixtures/source-excerpts/` — 18 verbatim pinned-source excerpts.
- `fixtures/features.macro` — the full registration table, verbatim.
- `outputs/` — unedited probe responses + derived results + drill log.
- `configs/monitoring-thresholds.json` — the watch thresholds.

## Reproduce

```sh
bash scripts/clean_reproduce.sh   # exit 0 only if every check passes
bash scripts/verify_digests.sh    # verifies SHA-256 digests of the pack
```

`clean_reproduce.sh` copies the pack to a throwaway directory, drops
all generated outputs, re-runs the probes, monitor, drill, excerpt
extraction and analysis from scratch, and compares the fresh numbers
with the shipped ones. Only read-only public probes run; no
transactions, no amendment votes, no live key material.

## Safety boundary

Bounded observation only. Read-only queries against public endpoints.
No transactions submitted, no amendment votes cast, no flood traffic,
no config changed on any node, no live key material used.
