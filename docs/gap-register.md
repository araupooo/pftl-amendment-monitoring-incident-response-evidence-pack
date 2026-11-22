# Gap register
| ID | Gap | Why it is a gap | Consequence |
| --- | --- | --- | --- |
| G-01 | Live vote tallies are not observable from the public RPC. | Vote counts are admin-only in injectJson (AmendmentTable.cpp:1000-1025); the public feature RPC returns no counts. | Activation approach cannot be trended; only the majority timestamp is visible, after majority is reached. |
| G-02 | History-service data provenance is unverified. | VHS is an unauthenticated third-party read API; its amendment rows cannot be cross-checked against ledger history. | The activation ledger/date (86785, 2026-02-09) rests on a single external source. |
| G-03 | Ledger-86785 activation transactions are not re-fetchable. | The public node retains ledgers 8200054-8283008 only; tx lookup returns txnNotFound. | The bulk enablement cannot be independently re-derived from the node. |
| G-04 | Veto behavior was never exercised live. | Veto requires admin access ([veto_amendments] config + table.veto); the public RPC cannot veto. | Runbook B's veto step is code-verified only, not live-tested. |
| G-05 | The unsupported-amendment majority path was never exercised live. | No unsupported amendment currently holds a majority, so firstUnsupportedExpected_ has never fired on this network. | Runbook B's warning path is code-verified only, not live-tested. |
| G-06 | The two-week majority-hold clock was never measured live. | No amendment has held a majority on this network, so the hold-to-enable transition is unobserved. | The 14-day figure is code-specified (SystemParameters.h:88), not measured. |
| G-07 | No documented amendment policy exists. | The whitepaper contains zero 'amend' mentions and no public policy document was found. | There is no baseline to judge whether a future up-vote is intended or rogue. |

Counts (recomputed from this table): 7 gaps.
