# Activation-monitoring and alert specification

## What is watched

The monitor is `src/amendment_monitor.py`, run against fresh
`scripts/probe_all.sh` output. It watches four things:

1. **The enabled set.** Any change in the count (currently 64) or in any
   amendment's `enabled` flag is an alert. Enablement is one-way, so a
   change is permanent.
2. **The majority field.** The public `feature` RPC adds a `majority`
   field (a timestamp) to an amendment once it holds a majority. No
   amendment currently has one. The first appearance of any `majority`
   field is the earliest public warning that an activation is coming.
3. **The registry sets.** The node's supported table (101), the
   history-service known set (103) and the pinned-code registration table
   (107) are cross-checked on every run. Any drift is an alert.
4. **The trusted set and quorum.** Validation quorum (17) and the UNL
   size (25) are re-read on every run; the votes-needed table is
   recomputed, because the activation bar moves with the trusted count.

## Thresholds

| Parameter | Value | Source |
| --- | --- | --- |
| Majority rule | votes > floor(trusted × 67/100) | SystemParameters.h:83–85; AmendmentTable.cpp:324–342, 359–378 |
| Majority hold time | 2 weeks (1,209,600 s), configurable down to 15 min | SystemParameters.h:88; Config.cpp:870–898 |
| Votes needed at UNL 25 | 17 (equals validation quorum 17) | Drill A-01 |
| Votes needed at UNL 24 / 20 / 17 | 17 / 14 / 12 | Drill A-01 |
| Activation processing | flag ledgers only, every 256 ledgers (seq ≡ 1 mod 256) | AmendmentTable.cpp:944–956 |
| Flag interval at measured cadence | 256 ledgers × 2.857 s ≈ 731 s (~12 min) | outputs/derived/cadence.json |
| Two-week hold in ledgers | ≈ 423,360 ledgers at 2.857 s/ledger | outputs/derived/activation-watch.json |
| Poll interval | every flag ledger (≤ 256 ledgers, ~12 min) | This spec |

## Alert rules

| Rule | Condition | Level | Response |
| --- | --- | --- | --- |
| A1 | Any `majority` field appears in `feature` output | CRITICAL | Start runbook B immediately; the activation clock is running (majority time + 2 weeks). |
| A2 | Enabled count changes, or any amendment flips `enabled` | CRITICAL | Verify against the flag ledger; record the activation ledger; start runbook C if the amendment is unexpected. |
| A3 | An amendment in the history-service set is missing from the node table, or vice versa | HIGH | Registry drift (see F-03). Re-run the monitor; do not treat the name as a pending activation. |
| A4 | Trusted validator count (UNL) drops below 25 | HIGH | Recompute the votes-needed table; the activation bar has moved (F-05). |
| A5 | Trusted validator count drops below 17 | CRITICAL | Validation quorum cannot be met; the network cannot validate. Amendment voting stops with it (drill C). |
| A6 | An unsupported amendment appears in `feature` output with a `majority` field | CRITICAL | Unsupported majority (F-07 path). The node's firstUnsupportedExpected clock is running; runbook B. |
| A7 | Node's configured majority time is not 2 weeks | HIGH | The warning window has been shortened (F-11). Confirm the setting is intentional. |
| A8 | `feature` RPC fails, or the history service is unreachable | MEDIUM | Monitoring is blind; fall back to the node table only and retry at the next flag ledger. |

## What the public RPC cannot show (by design)

- Vote counts per amendment (`count` / `validations` / `threshold` are
  admin-only in `injectJson`, AmendmentTable.cpp:1000–1025). There is no
  public trend line for an approaching majority.
- Veto state (`vetoed` is admin-only).
- Whether a specific validator votes for a specific amendment.

Consequence: rule A1 is the first public signal. The monitor cannot
give earlier warning than the majority timestamp. Any monitoring design
that assumes public vote tallies is wrong for this node; admin access to
a trusted node is required for earlier warning (see gap G-01).
