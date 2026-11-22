# Runbook C — rollback / disabling decision under quorum pressure

## Trigger

An amendment has activated that should not have, or the trusted
validator set is shrinking and the operator must decide whether to
veto, accept, or upgrade — while validation quorum itself is under
pressure.

## The hard constraint (pinned code)

Enablement is one-way. `AmendmentTable.cpp` lines 294–302:

> This is a one-way switch: once an amendment is enabled it can never
> be disabled, but it can be superseded by a subsequent amendment.

There is no disable, un-enable, or rollback call anywhere in the
amendment table (drill C-01: the only "disable" match in the file is
that comment). A bad activation can only be fixed by a later amendment
that supersedes it.

## Quorum pressure (drill C, 9 cases, all PASS)

| Trusted validators | Votes needed to pass an amendment | Can reach validation quorum (17)? |
| --- | --- | --- |
| 25 | 17 | yes |
| 20 | 14 | yes |
| 17 | 12 | yes (exactly) |
| 16 | 11 | **no** — validation halts |
| 10 | 7 | **no** — validation halts |

Two consequences follow:

1. **The activation bar falls as the trusted set shrinks** (17 → 14 →
   12). A shrinking UNL makes it easier, not harder, for an amendment
   to reach majority.
2. **Below 17 trusted validators the network cannot validate at all.**
   Amendment voting stops with validation — no new majority can form,
   and no pending majority can complete its hold.

## Decision tree

```
bad activation OR quorum pressure
  ├─ amendment already enabled?
  │   ├─ YES → No rollback exists. Draft a superseding amendment and
  │   │   run it through the normal vote + two-week hold. Until it
  │   │   activates, operate with the bad amendment enabled.
  │   └─ NO (majority held but not yet enabled) → Veto now (runbook B).
  │       The veto must spread before the enabling flag ledger.
  ├─ trusted validators < 17?
  │   → Validation has halted. Restore validators first; amendment
  │     decisions are moot until validation resumes.
  └─ trusted validators 17–24?
      → Recompute the votes-needed table (17 at 24, 14 at 20, 12 at 17)
        and re-run the monitor; the activation bar has moved.
```

## Timed lab drill (drill C, 9 cases, all PASS)

| Case | Check | Result |
| --- | --- | --- |
| C-01 | No disable mechanism; only the "can never be disabled" comment | PASS |
| C-02 | One-way switch documented in AmendmentState | PASS |
| C-03 (×5) | Trusted 25/20/17 can reach quorum 17; 16/10 cannot | PASS |
| C-04 | Activation bar falls as the trusted set shrinks (17 > 14 > 12) | PASS |
| C-05 | Supersede is the documented post-activation remedy | PASS |

Full log: `outputs/drill-run.log`.

## Actions

1. **If the amendment is already enabled:** accept it, document the
   impact, and start the superseding amendment. Do not restart nodes
   expecting the amendment to disappear — it is stored in the validated
   ledger's enabled set.
2. **If the amendment is in majority hold:** veto immediately (runbook
   B, step 1) and coordinate the veto across operators.
3. **If quorum is under pressure:** restore trusted validators before
   making amendment decisions. A network that cannot validate cannot
   activate anything — but it also cannot recover by voting.
4. **After any incident:** record the activation ledger, the majority
   start time (from the `majority` field), and the validator set size
   at the time, and append them to the inventory.
