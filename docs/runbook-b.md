# Runbook B — a bad amendment reaches majority

## Trigger

Alert rule A1 or A6: a `majority` field appears in `feature` output for
an amendment that should not activate — either an unsupported amendment
or a supported amendment the operators do not want.

## How the clock works (pinned code)

1. When an amendment first gains a majority, the validated ledger
   records the majority start time. The public `feature` RPC exposes it
   as the `majority` field (Feature1.cpp:60–64).
2. The node also tracks unsupported majorities: `doValidatedLedger`
   (AmendmentTable.cpp:958–995) logs `Unsupported amendment <hash>
   reached majority at <time>` and sets `firstUnsupportedExpected_` to
   the earliest unsupported majority time plus the hold time (two weeks
   by default).
3. After the majority has held for two weeks, the node injects the
   enabling pseudo-transaction at the next flag ledger
   (`doVoting`, AmendmentTable.cpp:884–940). The activation ledger is
   therefore approximately the majority ledger + ~423,360 ledgers (at
   2.857 s/ledger).

## Decision tree

```
majority field appears
  ├─ amendment is supported AND wanted? → Monitor the hold; no action.
  │   Activation is expected in ~2 weeks (majority time + 2 weeks).
  ├─ amendment is supported but NOT wanted?
  │   → VETO before activation (step 1 below). Veto only works pre-activation.
  └─ amendment is UNSUPPORTED?
      → The node itself is at risk: it will enable an amendment it has
        no code for. Veto immediately AND plan an upgrade to a build
        that supports or retires it. If activation lands first, see
        runbook C.
```

## Timed lab drill (drill B, 5 cases, all PASS)

| Case | Check | Result |
| --- | --- | --- |
| B-01 | Unsupported-majority log path present (lines 981–982) | PASS |
| B-02 | Expected-activation clock = majority time + 2 weeks | PASS |
| B-03 | Synthetic unsupported majority at ledger 8283007 → expected activation ~ledger 8706367 (~14.0 days) | PASS |
| B-04 | Veto path present ([veto_amendments] + table.veto) | PASS |
| B-05 | Veto excludes the amendment from validator votes | PASS |

Full log: `outputs/drill-run.log`.

## Actions (in order, before activation)

1. **Veto.** Add the amendment ID to the `[veto_amendments]` section of
   the node config and restart the node (`Application.cpp:1282–1284`;
   `AmendmentTable::veto`). A vetoed amendment is excluded from
   `doValidation`, so the node stops voting for it, and the majority
   cannot be sustained by this node. Note: veto is an admin/config
   action — it cannot be done from the public RPC (gap G-04).
2. **Coordinate.** Tell the other validator operators to veto as well.
   A single node's veto does not stop the network majority; the veto
   must spread to enough validators to drop the yes count below the
   threshold (17 at UNL 25).
3. **Watch the flag ledgers.** Re-check `feature` output every flag
   ledger (every ~12 min). If the `majority` field disappears, the
   majority was lost (`tfLostMajority`) and the clock resets.
4. **If activation is unavoidable** (majority held, veto too late):
   prepare a superseding amendment. Activation is one-way — see
   runbook C.

## Timing

The window between the first public signal (the `majority` field) and
activation is the two-week hold, minus the time already elapsed. The
response window after hold expiry is one flag interval (~12 min). The
veto must land before the enabling flag ledger.
