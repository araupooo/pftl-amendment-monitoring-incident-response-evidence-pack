# Evidence index
| File | What it is |
| --- | --- |
| `outputs/feature_list.json` | Live feature RPC: 101 amendments, enabled/supported/name, no majority fields. |
| `outputs/vhs-amendments-info.json` | History service: 103 known amendments with ids, names, deprecated flags. |
| `outputs/vhs-amendments-vote-test.json` | History service: 64 enabled amendments with activation ledger/tx/date. |
| `outputs/rpc-feature-pf-vote-tracking.json` | Single-amendment feature RPC for PF_ValidatorVoteTracking. |
| `outputs/rpc-tx-activation-86785.json` | tx lookup for a ledger-86785 activation tx: txnNotFound. |
| `outputs/server_info.json` | Live node: postfiatd 1.0.9, network 2025, validated seq 8283007, 21 peers. |
| `outputs/server_state.json` | Live node state: validation_quorum 17, complete_ledgers 8200054-8283008. |
| `outputs/ledger_current.json` | Validated ledger 8283007 (full header, close_time 848705451). |
| `outputs/ledger_closed.json` | Last closed ledger 8283008 (hash/index only; no close_time). |
| `outputs/fee.json` | Live fee levels at probe time. |
| `outputs/validators.json` | Admin method refused by the public proxy (HTTP 403). |
| `outputs/peers.json` | Admin method refused by the public proxy (HTTP 403). |
| `outputs/invalid_method.json` | Unknown method response from the public proxy. |
| `outputs/vhs-health.json` | History service health at probe time. |
| `outputs/vhs-amendments.json` | History service API index (endpoint list). |
| `outputs/vhs-validators.json` | History service: 66 known validators. |
| `outputs/vhs-topology.json` | History service topology snapshot. |
| `outputs/testnet_vl.json` | Live validator list document (25 validators, UNL). |
| `outputs/explorer_health.json` | Explorer health: HTTP 500 at probe time. |
| `outputs/postfiat_org.html` | Project homepage capture. |
| `outputs/postfiat_whitepaper.html` | Whitepaper capture (zero 'amend' mentions). |
| `outputs/probe-run.log` | Probe run log with HTTP status, timings and SHA-256 per file. |
| `outputs/drill-run.log` | Lab drill run log: 29/29 cases PASS. |
| `outputs/fresh-clone-*` | Fresh-clone reproduction outputs (29 files): re-probed responses, re-run monitor/drill results, and fresh-clone-compare.log (12/12 compare checks PASS; fresh validated ledger 8283343 vs shipped 8283007). |
| `outputs/derived/amendment-inventory.json` | Machine-readable inventory (103 rows). |
| `outputs/derived/amendment-inventory.csv` | Same inventory as CSV. |
| `outputs/derived/activation-watch.json` | Thresholds, flag-ledger timing, alerts, monitor checks (16/16). |
| `outputs/derived/cadence.json` | Ledger cadence measurement (21 ledgers / 60 s = 2.857 s/ledger). |
| `outputs/derived/drill-results.json` | Drill results (29/29 PASS, timings). |
| `outputs/derived/monitor-run.log` | Monitor run log (16/16 checks PASS). |
| `fixtures/features.macro` | Verbatim pinned features.macro (107 registrations). |
| `fixtures/source-hashes.json` | SHA-256 + git blob SHAs for pinned sources; OrchardPrivacy absence check. |
| `fixtures/source-excerpts/` | 18 verbatim pinned-source excerpts with file paths and line ranges. |
| `scripts/probe_all.sh` | Read-only live probe script (9 RPC POSTs + 10 GETs). |
| `scripts/drill.py` | Lab drill script (3 drills, 29 cases). |
| `src/amendment_monitor.py` | Inventory + activation-watch builder (16 checks). |
| `scripts/extract_excerpts.py` | Pinned-source excerpt extractor (anchor-verified). |
| `scripts/clean_reproduce.sh` | Fresh-environment reproduction (exit 0 only if all checks pass). |
| `scripts/compare_reproduce.py` | Fresh-vs-shipped comparison. |
| `scripts/verify_digests.sh` | SHA-256 digest verification over the pack. |
| `findings.json` | 12 findings (3 HIGH / 5 MEDIUM / 3 LOW / 1 INFO; 8 MEASURED / 4 SPECIFIED). |
| `docs/claim-index.md` | 30 claims (19 VERIFIED / 8 SPECIFIED / 1 UNVERIFIED / 2 UNTESTABLE). |
| `docs/risk-register.md` | 14 risks (3 HIGH / 6 MEDIUM / 4 LOW / 1 INFO). |
| `docs/gap-register.md` | 7 gaps. |

44 evidence items.
