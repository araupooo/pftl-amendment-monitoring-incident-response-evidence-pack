# Decision memo

## Verdict

**WATCHFUL, NOT BLIND.** The activation machinery is sound and fully
specified in code, but the public monitoring surface cannot see an
activation approaching: no vote counts, no majority until it exists,
and no documented policy.

## What was measured (live, 2026-11-22 23:30–23:39 UTC)

- Node: postfiatd 1.0.9, network 2025, validated ledger 8,283,007,
  21 peers, validation quorum 17, UNL 25 validators.
- Amendments: 101 in the node table (64 enabled, 37 disabled); 103
  known to the history service; 107 registered in the pinned code.
- All 64 enabled amendments activated in a single bulk event at ledger
  86785, 2026-02-09T14:31:12Z. No amendment has activated through the
  normal two-week majority process on this network.
- No amendment currently holds a majority; none is vetoed.
- Both PostFiat amendments (PF_ValidatorVoteTracking,
  PF_AccountExclusion) are DefaultNo and disabled.
- Ledger cadence 2.857 s/ledger (21 ledgers / 60 s). Next flag ledger
  8283137.
- Drill: 29/29 cases PASS. Monitor: 16/16 checks PASS.

## What the code says (pinned commit 0085a1ff)

- Majority rule: votes > floor(trusted × 67/100) — 17 of 25 at the
  current UNL. The pre-fix 204/256 rule is superseded because
  `fixAmendmentMajorityCalc` is enabled.
- Majority must hold two weeks (configurable down to 15 minutes).
- Activation is processed only at flag ledgers (every 256 ledgers).
- Enablement is one-way; the only remedy is a superseding amendment.
- Vote counts and veto state are admin-only in the `feature` RPC.
- A vetoed amendment is excluded from validator votes.

## The three findings that matter most

1. **F-01 — the bulk enablement.** The enabled set is exactly the
   DefaultYes set. The network has never run a live majority
   activation. Every runbook in this pack is therefore code-verified,
   not live-tested — the two-week hold, the veto, and the unsupported
   majority warning have never fired on this network.
2. **F-02 — the blind spot.** The public RPC cannot show vote counts.
   The first public signal of an activation is the `majority`
   timestamp, which appears only after majority is reached. Monitoring
   must poll every flag ledger and treat any `majority` field as
   CRITICAL.
3. **F-03 — registry drift.** The history service lists 103 amendments;
   the node knows 101. `Batch` is registered but unsupported;
   `OrchardPrivacy` is absent from the pinned code entirely. Monitoring
   keyed to the history service will chase names the node cannot
   activate.

## What to do next

1. Poll `feature` every flag ledger (~12 min) and alert on any
   `majority` field (rule A1) or any enabled-count change (rule A2).
2. Publish an amendment policy: which amendments the network intends
   to enable, in what order, and the veto criteria (F-12).
3. Get admin access to a trusted node for vote-count visibility
   (gap G-01); public monitoring alone cannot give earlier warning.
4. Decide the fate of the two PostFiat amendments: they are DefaultNo
   and disabled, so vote tracking and account exclusion are inert
   (F-06). Either campaign for them or record the decision not to.
5. Keep this pack's inventory as the baseline: any future change to
   the enabled set, the majority field, or the registry counts is an
   incident until explained.

## What this pack does not claim

- It does not verify the history service's activation ledger/date
  against the ledger: the node retains only ledgers 8200054–8283008
  and the activation ledger 86785 is outside that range (claim C-28,
  UNVERIFIED).
- It does not test a live activation, a live veto, or a live majority
  hold (claims C-29, C-30, UNTESTABLE).
- It does not predict which amendment will activate next. Nothing is
  approaching majority today.
