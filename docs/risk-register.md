# Risk register
| ID | Severity | Risk | Finding | Likelihood | Impact |
| --- | --- | --- | --- | --- | --- |
| R-01 | HIGH | Silent activation approach: an amendment reaches majority with no public early warning. | F-02 | Medium | High |
| R-02 | HIGH | Bulk enablement precedent: a future restart/genesis could enable DefaultNo amendments without the two-week process. | F-01 | Low | High |
| R-03 | HIGH | Registry drift: monitoring keyed to the history service misses node-unknown amendments. | F-03 | Medium | High |
| R-04 | MEDIUM | Flag-ledger timing: activation lands at most one flag interval (~12 min) after majority-hold expiry. | F-04 | Medium | Medium |
| R-05 | MEDIUM | A shrinking trusted set lowers the activation bar (17 votes at 25, 14 at 20, 12 at 17). | F-05 | Medium | Medium |
| R-06 | MEDIUM | PostFiat governance features are inert: vote tracking and account exclusion cannot be used. | F-06 | High | Medium |
| R-07 | MEDIUM | No rollback: a bad activation is permanent until a superseding amendment exists. | F-07 | Low | High |
| R-08 | MEDIUM | Retired-amendment confusion: 16 retired names still appear in registries and RPC output. | F-08 | Medium | Low |
| R-09 | LOW | Major features disabled: MPT, NFT, permissioned DEX, vaults and bridges are unavailable. | F-09 | High | Low |
| R-10 | LOW | Activation history unverifiable: the 86785 bulk event cannot be re-derived from the node. | F-10 | High | Low |
| R-11 | LOW | Majority-time misconfiguration: a 15-minute setting removes the two-week warning window. | F-11 | Low | Medium |
| R-12 | LOW | No documented amendment policy: no public commitment on vote order or veto criteria. | F-12 | High | Low |
| R-13 | MEDIUM | Quorum pressure: trusted validators below 17 halt validation entirely, and amendment voting with it. | F-05 | Low | High |
| R-14 | INFO | Explorer degraded (HTTP 500): the public explorer cannot serve as a second monitoring source. | F-02 | High | Low |

Counts (recomputed from this table): 14 risks — HIGH 3, INFO 1, LOW 4, MEDIUM 6.
