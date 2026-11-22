# Runbook A — amendment activation stalls / fails to reach consensus

## Trigger

Alert rule A1 has not fired (no amendment holds a majority), but a
candidate amendment is expected to activate and is not progressing — or
the operator wants to confirm that a stalled candidate cannot activate
on its own.

## How activation works (pinned code)

1. Each validator votes for the amendments it supports and has not vetoed
   (`doValidation`, AmendmentTable.cpp:813–838). Validators vote for the
   64 DefaultYes amendments and for nothing else, by default.
2. Each close, the node tallies trusted validations. A candidate passes
   when its yes votes are strictly greater than
   floor(trusted × 67/100) (`AmendmentSet::passes`,
   AmendmentTable.cpp:359–378; the post-fix 67/100 rule applies because
   `fixAmendmentMajorityCalc` is enabled live).
3. When a candidate first gains a majority, the node injects a
   `tfGotMajority` pseudo-transaction — but only if the local node itself
   votes up (`doVoting`, AmendmentTable.cpp:884–940). A DefaultNo
   amendment never self-enables, even if validators vote for it.
4. The majority must then hold for two weeks
   (`defaultAmendmentMajorityTime`, SystemParameters.h:88). Only then
   does the node inject the enabling pseudo-transaction — and only at a
   flag ledger, where (seq−1)/256 changes (AmendmentTable.cpp:944–956).

## Decision tree

```
candidate not progressing
  ├─ votes < needed (17 at UNL 25)? → STALLED: no majority, no clock.
  │   Wait or campaign for validator up-votes. Nothing activates.
  ├─ votes ≥ needed but no majority field in feature output?
  │   → Check again at the next flag ledger; majority is recorded in the
  │     validated ledger, not in real time.
  └─ majority field present? → Not a stall. Go to runbook B (the clock
      is running) or monitor the two-week hold.
```

## Timed lab drill (drill A, 15 cases, all PASS)

| Case | Check | Result |
| --- | --- | --- |
| A-01 (×8) | Votes needed at 25/24/20/17/16/10/2/1 trusted validators | 17/17/14/12/11/7/2/1 |
| A-02 | 16/25 votes does not pass at UNL 25 | PASS |
| A-03 | 17/25 votes passes at UNL 25 | PASS |
| A-04 | A DefaultNo amendment never self-enables on majority | PASS |
| A-05 | Flag-ledger rule present in pinned code | PASS |
| A-06 | Next flag ledger 8283137 is 1 mod 256, 130 ledgers ahead (~371 s) | PASS |
| A-07 | Live: zero amendments hold a majority | PASS |
| A-08 | Stall decision window is one flag interval (~731 s) | PASS |

Full log: `outputs/drill-run.log`. The drill wall time is 0.01 s
(lab simulation; no live calls).

## Actions

1. Confirm the stall: read `feature` output, confirm no `majority`
   field for the candidate, and confirm the enabled count is unchanged
   (64).
2. Identify the cause: the candidate is DefaultNo (21 of them are), or
   fewer than 17 trusted validators vote for it, or the majority was
   lost (`tfLostMajority` is injected when validators stop voting yes).
3. Decide: wait (the candidate cannot activate while stalled), campaign
   for up-votes (validator operators must set the amendment in
   `[amendments]`), or abandon the candidate.
4. Do not force it: there is no manual enable path from the public RPC.
   The only in-protocol paths are validator voting and the genesis
   ledger's desired set.
