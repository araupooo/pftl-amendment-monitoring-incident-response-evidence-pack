# Amendment inventory
Complete inventory at validated ledger 8283007 (probe 2026-11-22 23:30 UTC). Pinned postfiatd 0085a1ff885d6a446369cf73a4430f75af22be55. Sources: live `feature` RPC (101 supported), history-service /amendments/info (103 known) and /amendments/vote/test (64 enabled). Amendment IDs are SHA-512-Half(name), verified for all 101 node amendments.

## Summary

- Known amendments: 103 (101 in the node table, 2 history-service-only)
- Enabled: 64 — all at ledger 86785, 2026-02-09T14:31:12Z (one bulk event)
- Disabled: 39 (21 DefaultNo, 16 retired, 2 history-service-only)
- With a majority: 0. Vetoed: 0.
- PostFiat amendments (PF_AccountExclusion, PF_ValidatorVoteTracking): both DefaultNo, disabled.

## Table

| Name | Enabled | Vote | Activation ledger | Activation date |
| --- | --- | --- | --- | --- |
| AMM | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| AMMClawback | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| Batch | no | — | — | — |
| CheckCashMakesTrustLine | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| Checks | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| Clawback | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| Credentials | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| CryptoConditions | no | Obsolete | — | — |
| CryptoConditionsSuite | no | DefaultNo | — | — |
| DID | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| DeepFreeze | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| DeletableAccounts | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| DepositAuth | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| DepositPreauth | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| DisallowIncoming | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| DynamicNFT | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| EnforceInvariants | no | Obsolete | — | — |
| Escrow | no | Obsolete | — | — |
| ExpandedSignerList | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| FeeEscalation | no | Obsolete | — | — |
| Flow | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| FlowCross | no | Obsolete | — | — |
| FlowSortStrands | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| HardenedValidations | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| ImmediateOfferKilled | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| LendingProtocol | no | DefaultNo | — | — |
| MPTokensV1 | no | DefaultNo | — | — |
| MultiSign | no | Obsolete | — | — |
| MultiSignReserve | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| NFTokenMintOffer | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| NegativeUNL | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| NonFungibleTokensV1 | no | DefaultNo | — | — |
| NonFungibleTokensV1_1 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| OrchardPrivacy | no | — | — | — |
| PF_AccountExclusion | no | DefaultNo | — | — |
| PF_ValidatorVoteTracking | no | DefaultNo | — | — |
| PayChan | no | Obsolete | — | — |
| PermissionedDEX | no | DefaultNo | — | — |
| PermissionedDomains | no | DefaultNo | — | — |
| PriceOracle | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| RequireFullyCanonicalSig | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| SingleAssetVault | no | DefaultNo | — | — |
| SortedDirectories | no | Obsolete | — | — |
| TickSize | no | Obsolete | — | — |
| TicketBatch | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| TokenEscrow | no | DefaultNo | — | — |
| TrustSetAuth | no | Obsolete | — | — |
| XChainBridge | no | DefaultNo | — | — |
| XRPFees | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1201 | no | Obsolete | — | — |
| fix1368 | no | Obsolete | — | — |
| fix1373 | no | Obsolete | — | — |
| fix1512 | no | Obsolete | — | — |
| fix1513 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1515 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1523 | no | Obsolete | — | — |
| fix1528 | no | Obsolete | — | — |
| fix1543 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1571 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1578 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1623 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fix1781 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixAMMClawbackRounding | no | DefaultNo | — | — |
| fixAMMOverflowOffer | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixAMMv1_1 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixAMMv1_2 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixAMMv1_3 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixAmendmentMajorityCalc | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixCheckThreading | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixDirectoryLimit | no | DefaultNo | — | — |
| fixDisallowIncomingV1 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixEmptyDID | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixEnforceNFTokenTrustline | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixEnforceNFTokenTrustlineV2 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixFillOrKill | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixFrozenLPTokenTransfer | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixIncludeKeyletFields | no | DefaultNo | — | — |
| fixInnerObjTemplate | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixInnerObjTemplate2 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixInvalidTxFlags | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixMPTDeliveredAmount | no | DefaultNo | — | — |
| fixMasterKeyAsRegularKey | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixNFTokenDirV1 | no | DefaultNo | — | — |
| fixNFTokenNegOffer | no | DefaultNo | — | — |
| fixNFTokenPageLinks | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixNFTokenRemint | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixNFTokenReserve | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixNonFungibleTokensV1_2 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixPayChanCancelAfter | no | DefaultNo | — | — |
| fixPayChanRecipientOwnerDir | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixPreviousTxnID | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixPriceOracleOrder | no | DefaultNo | — | — |
| fixQualityUpperBound | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixReducedOffersV1 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixReducedOffersV2 | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixRemoveNFTokenAutoTrustLine | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixRmSmallIncreasedQOffers | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixSTAmountCanonicalize | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixTakerDryOfferRemoval | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixTokenEscrowV1 | no | DefaultNo | — | — |
| fixTrustLinesToSelf | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixUniversalNumber | yes | DefaultYes | 86785 | 2026-02-09 14:31:12Z |
| fixXChainRewardRounding | no | DefaultNo | — | — |

Full machine-readable inventory: outputs/derived/amendment-inventory.json and .csv. History-service-only rows (Batch, OrchardPrivacy) have no node row: Batch is registered but unsupported in the pinned code, OrchardPrivacy is absent from the pinned code entirely.
