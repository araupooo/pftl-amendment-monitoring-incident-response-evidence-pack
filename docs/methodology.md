# Methodology

## Pinned source

All code claims cite postfiatd commit `0085a1ff885d6a446369cf73a4430f75af22be55`
(2026-10-10, PR #50 merge, postfiatd 1.0.9). The commit was cloned fresh
and verified with `git rev-parse HEAD` before any excerpt was taken. Every
cited line number was verified with `grep -n` on that checkout; no line
number in this pack comes from a web fetch. Verbatim excerpts live in
`fixtures/source-excerpts/`; the full `features.macro` registration table
is shipped as `fixtures/features.macro`. Blob SHAs are in
`fixtures/source-hashes.json`.

## Live probes

All live data comes from read-only probes run 2026-11-22 23:30–23:39 UTC
against the public PFTL testnet (network ID 2025):

- postfiatd JSON-RPC at `https://rpc.testnet.postfiat.org/`: 13 POSTs in
  total — 9 in `scripts/probe_all.sh` (`server_info`, `ledger`,
  `ledger_closed`, `fee`, `feature`, `server_state`, `validators`,
  `peers`, an unknown method), 2 follow-ups (`feature` for
  `PF_ValidatorVoteTracking` by name, `tx` for a ledger-86785 activation
  transaction), and 2 for the live cadence measurement (two `server_info`
  calls 60 s apart).
- Validator History Service at `https://vhs.testnet.postfiat.org/`: 6 GETs
  (health, amendments index, amendments/info, amendments/vote/test,
  validators, topology).
- `https://postfiat.org/testnet_vl.json` (validator list), the project
  homepage and whitepaper, and the explorer health endpoint.

Unedited responses are in `outputs/`; the probe log is
`outputs/probe-run.log`. No transactions were submitted, no amendment
votes were cast, no flood traffic was sent.

## Derived results

- `src/amendment_monitor.py` parses `features.macro`, the live `feature`
  output and the history-service files, cross-checks the three registries
  against each other (16 checks, all PASS), and builds the inventory and
  the activation watch. Amendment IDs are verified as SHA-512-Half(name),
  the same derivation the pinned code uses (`Feature.cpp:266`).
- Ledger cadence was measured live: two `server_info` calls 60 s apart
  (21 ledgers, 2.857 s/ledger, `outputs/derived/cadence.json`). A cadence
  cannot be derived from a single ledger pair: `ledger_closed` returns no
  close time, and close times have 10 s resolution.
- `scripts/drill.py` runs the three incident-response drills as lab
  simulations against the pinned code and the shipped probe outputs
  (29 cases, all PASS). Nothing in the drills touches the live network.
- `scripts/analyze.py` builds the findings, claim index, risk register,
  gap register, inventory doc and evidence index, computing every count
  from the table it summarizes.

## Boundaries

- The public `feature` RPC exposes no vote counts (admin-only in the
  pinned code). Live vote tallies, veto state and majority approach below
  the majority threshold are not observable from the public RPC; the
  corresponding claims are marked SPECIFIED (code) or UNTESTABLE, never
  VERIFIED.
- The history service is an unauthenticated third-party read API. Its
  amendment rows (including the activation ledger/date for the 64 enabled
  amendments) cannot be cross-checked against ledger history from the
  public node, because the node retains only ledgers 8200054–8283008 and
  the activation ledger 86785 is outside that range. The claim is marked
  UNVERIFIED.
- The whitepaper contains no amendment content; there is no documented
  amendment policy to check against.
- No live key material was used. No validator was operated. No config
  file was changed on any node.
