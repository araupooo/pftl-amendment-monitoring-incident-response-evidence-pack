# Claim-to-evidence index
Every measured or specification-derived claim in this pack, with its status and its primary source. Status: VERIFIED (measured live or in the lab), SPECIFIED (pinned code, docs, or a cited standard), UNVERIFIED (could not be checked), UNTESTABLE (the safety boundary forbids the action that would test it).
| ID | Status | Claim | Primary source |
| --- | --- | --- | --- |
| C-01 | VERIFIED | 101 amendments in the node's supported table: 64 enabled, 37 disabled. | Live probe feature_list.json; monitor 16/16 checks. |
| C-02 | VERIFIED | All 101 amendment IDs equal SHA-512-Half(name). | Monitor check: sha512Half verified for all 101; Feature.cpp:266. |
| C-03 | VERIFIED | The enabled set equals the DefaultYes set exactly (64/64). | Monitor check; features.macro parse (64 DefaultYes). |
| C-04 | VERIFIED | All 64 enabled amendments activated at ledger 86785, 2026-02-09T14:31:12Z. | VHS vhs-amendments-vote-test.json (64 rows, one ledger, one timestamp). |
| C-05 | VERIFIED | No amendment currently holds a majority; none is vetoed. | Live probe feature_list.json (no majority/vetoed fields present). |
| C-06 | VERIFIED | PF_ValidatorVoteTracking and PF_AccountExclusion are disabled. | Live probe feature_list.json; rpc-feature-pf-vote-tracking.json. |
| C-07 | VERIFIED | Next flag ledger 8283137 from validated seq 8283007; activation only at flag ledgers. | Monitor activation-watch.json; AmendmentTable.cpp needValidatedLedger. |
| C-08 | VERIFIED | Ledger cadence 2.857 s/ledger (21 ledgers in a 60 s window). | outputs/derived/cadence.json (two server_info calls). |
| C-09 | VERIFIED | Validation quorum 17; UNL 25 validators; the history service knows 66 validators. | server_state.json (validation_quorum 17); testnet_vl.json (25); vhs-validators.json (count 66). |
| C-10 | VERIFIED | The history service lists 103 known amendments against the node's 101. | vhs-amendments-info.json (count 103) vs feature_list.json (101). |
| C-11 | VERIFIED | Batch is registered but unsupported; OrchardPrivacy is absent from the pinned code. | features.macro:51 (Batch, Supported::no); fixtures/source-hashes.json absence_checks (0 matches). |
| C-12 | VERIFIED | 16 retired amendments, all disabled; the history service marks 15 deprecated (FlowCross differs). | features.macro (16 XRPL_RETIRE); feature_list.json; vhs-amendments-info.json. |
| C-13 | VERIFIED | The single-amendment feature RPC returns an amendment by name with enabled/supported state. | outputs/rpc-feature-pf-vote-tracking.json (PF_ValidatorVoteTracking, enabled false). |
| C-14 | VERIFIED | The ledger-86785 activation transaction cannot be re-fetched (txnNotFound). | outputs/rpc-tx-activation-86785.json (error_code 29); complete_ledgers 8200054-8283008. |
| C-15 | VERIFIED | 17 votes are needed at 25 trusted validators (drill A-01, 8/8 threshold checks). | outputs/drill-run.log; outputs/derived/drill-results.json. |
| C-16 | VERIFIED | Lab drill 29/29 cases PASS (A 15, B 5, C 9). | outputs/drill-run.log; outputs/derived/drill-results.json. |
| C-17 | VERIFIED | The whitepaper contains zero occurrences of 'amend'. | outputs/postfiat_whitepaper.html (163,089 bytes), grep count 0. |
| C-18 | VERIFIED | The public RPC refuses the admin methods validators and peers with HTTP 403. | outputs/validators.json, outputs/peers.json (403 bodies, identical). |
| C-19 | VERIFIED | The public explorer health endpoint returns HTTP 500 at probe time. | outputs/explorer_health.json (HTTP 500). |
| C-20 | SPECIFIED | Majority rule (post-fix): votes > floor(trusted * 67/100); fixAmendmentMajorityCalc is enabled live. | SystemParameters.h:83-85; AmendmentTable.cpp:324-342, 359-378; feature_list.json. |
| C-21 | SPECIFIED | A majority must hold 2 weeks by default; the hold time is configurable down to 15 minutes. | SystemParameters.h:88; Config.cpp:870-898; Config.h:248. |
| C-22 | SPECIFIED | Amendment state is only processed at flag ledgers, where (seq-1)/256 changes. | AmendmentTable.cpp:944-956 (needValidatedLedger). |
| C-23 | SPECIFIED | Enablement is one-way; there is no disable path; a bad activation can only be superseded. | AmendmentTable.cpp:294-302 (AmendmentState comment); drill C-01/C-05. |
| C-24 | SPECIFIED | The public feature RPC omits vote counts; count/validations/threshold are admin-only. | AmendmentTable.cpp:1000-1025 (injectJson); Feature1.cpp:47 (isAdmin). |
| C-25 | SPECIFIED | A vetoed amendment is excluded from validator votes. | AmendmentTable.cpp:813-838 (doValidation); Application.cpp:1282-1284 ([veto_amendments]). |
| C-26 | SPECIFIED | PF_ValidatorVoteTracking gates the vote tracker; PF_AccountExclusion gates exclusion-list changes. | ValidatorVoteTracker.cpp:162; Change.cpp:618-619. |
| C-27 | SPECIFIED | An unsupported amendment reaching majority sets firstUnsupportedExpected to majority time + 2 weeks. | AmendmentTable.cpp:958-995 (doValidatedLedger). |
| C-28 | UNVERIFIED | The history service's amendment data matches the ledger. | VHS is an unauthenticated third-party service; activation ledger/date cannot be cross-checked against node history (see C-14). |
| C-29 | UNTESTABLE | An amendment can be driven to majority and enabled on this network. | Would require casting validator votes and holding a majority for two weeks; the safety boundary forbids votes and live keys. |
| C-30 | UNTESTABLE | Veto behavior on a live majority (veto before activation blocks it). | Veto is an admin-only operation ([veto_amendments] + table.veto); it cannot be exercised from the public RPC. |

Counts (recomputed from this table): 30 claims — SPECIFIED 8, UNTESTABLE 2, UNVERIFIED 1, VERIFIED 19.
