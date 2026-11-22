# Citations

Primary sources, pinned to postfiatd commit
`0085a1ff885d6a446369cf73a4430f75af22be55` unless stated otherwise.
Verbatim excerpts are in `fixtures/source-excerpts/`; the full
registration table is `fixtures/features.macro`.

| Claim area | Primary source |
| --- | --- |
| Amendment registration table (107 entries) | `include/xrpl/protocol/detail/features.macro` (full file shipped) |
| PF amendments DefaultNo | `features.macro:45-46` |
| Unsupported amendments (Batch et al.) | `features.macro:35,39,41,51,53,67` |
| Amendment ID = SHA-512-Half(name) | `src/libxrpl/protocol/Feature.cpp:266` |
| DefaultNo/DefaultYes voting guidance | `src/libxrpl/protocol/Feature.cpp:74-84` |
| Majority thresholds 204/256 (pre-fix) and 67/100 (post-fix) | `include/xrpl/protocol/SystemParameters.h:83-85` |
| Majority hold time 2 weeks (default) | `include/xrpl/protocol/SystemParameters.h:88` |
| Threshold computation and strictly-greater pass rule | `src/xrpld/app/misc/detail/AmendmentTable.cpp:324-342, 359-378` |
| Voting decision tree (got/lost majority, enable) | `src/xrpld/app/misc/detail/AmendmentTable.cpp:884-940` |
| Flag-ledger processing rule | `src/xrpld/app/misc/detail/AmendmentTable.cpp:944-956` |
| Unsupported-majority warning + expected-activation clock | `src/xrpld/app/misc/detail/AmendmentTable.cpp:958-995` |
| One-way enablement (no disable path) | `src/xrpld/app/misc/detail/AmendmentTable.cpp:294-302` |
| Admin-only vote counts in RPC output | `src/xrpld/app/misc/detail/AmendmentTable.cpp:1000-1025` |
| Validator voting set (supported + up-voted + not enabled) | `src/xrpld/app/misc/detail/AmendmentTable.cpp:813-838` |
| `feature` RPC handler (majority field, admin gating) | `src/xrpld/rpc/handlers/Feature1.cpp:40-70, 76-95` |
| Majority-time config parsing (min 15 minutes) | `src/xrpld/core/detail/Config.cpp:870-898` |
| Majority-time default | `src/xrpld/core/Config.h:248` |
| Node startup: amendment table + veto section | `src/xrpld/app/main/Application.cpp:1270-1293` |
| PF_ValidatorVoteTracking gate | `src/xrpld/app/misc/ValidatorVoteTracker.cpp:155-165` |
| PF_AccountExclusion gate | `src/xrpld/app/tx/detail/Change.cpp:615-625` |
| FeatureBitset size bound | `include/xrpl/protocol/Feature.h:105-115` |

## Live sources (probed 2026-11-22 23:30–23:39 UTC)

| Source | Endpoint | File |
| --- | --- | --- |
| postfiatd JSON-RPC | `https://rpc.testnet.postfiat.org/` | `outputs/server_info.json`, `outputs/feature_list.json`, `outputs/ledger_current.json`, `outputs/ledger_closed.json`, `outputs/fee.json`, `outputs/server_state.json`, `outputs/validators.json`, `outputs/peers.json`, `outputs/invalid_method.json`, `outputs/rpc-feature-pf-vote-tracking.json`, `outputs/rpc-tx-activation-86785.json` |
| Validator History Service | `https://vhs.testnet.postfiat.org/v1/` | `outputs/vhs-health.json`, `outputs/vhs-amendments.json`, `outputs/vhs-amendments-info.json`, `outputs/vhs-amendments-vote-test.json`, `outputs/vhs-validators.json`, `outputs/vhs-topology.json` |
| Validator list | `https://postfiat.org/testnet_vl.json` | `outputs/testnet_vl.json` |
| Explorer health | `https://explorer.testnet.postfiat.org/api/v1/health` | `outputs/explorer_health.json` |
| Project site / whitepaper | `https://postfiat.org/`, `https://postfiat.org/whitepaper/` | `outputs/postfiat_org.html`, `outputs/postfiat_whitepaper.html` |

## Notes on the history service

The Validator History Service (VHS) is an unauthenticated third-party
read API derived from the XRPL data API. Its amendment rows are the
sole source for the activation ledger (86785) and date (2026-02-09) of
the 64 enabled amendments, because the public node retains only ledgers
8200054–8283008. Where VHS and the node disagree (103 vs 101 known
amendments; 15 vs 16 deprecated names), the pack records the
disagreement rather than picking a side. See claims C-28 (UNVERIFIED)
and findings F-03, F-08, F-10.
