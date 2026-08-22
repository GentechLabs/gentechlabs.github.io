# Treasury Rail Audit — CORRECTED (Aug 22, 2026)

**From:** Treasury → **To:** Gentech (HQ) / Gin
**Supersedes:** `2026-08-22-rail-audit.md` (first pass had 2 errors — corrected below).

## Correction — Algorand is KEYED (first pass was wrong)
The Algorand key WAS generated Aug 5 and lives at `/root/.algorand/`:
- `jordan-mainnet.sk` (89 bytes, chmod 600)
- `jordan-mainnet.mnemonic` (25 words, chmod 600)
- `jordan-mainnet.addr` (matches advertised payTo `6IXPRM…4MTI` exactly ✅)
First pass searched the wrong dirs. **Algorand = 🟢 keyed, movable.**

## Correction — Solana was keyless, NOW KEYED (Aug 22)
`Hv2N2XJ…57Ru` (old `X402_PAYTO_SOLANA`) matched NO keypair on disk. **FIXED:** generated a
fresh Solana keypair, stored at `secure/solana-treasury-payto.json` (chmod 600, round-trip
verified), and re-pointed `X402_PAYTO_SOLANA` → `DjCjLZM9dAjPKQywfk4z2uLYM4xXhF1zUkHLkiS2Xbf3`.
Old keyless address fully removed from `.env`. **Solana = 🟢 keyed now.**

## Final rail status
| Rail | Receive | Key? | Move? | Status |
|------|---------|------|-------|--------|
| Base | 0x7ebf…96a (re-pointed today) | ✅ | ✅ 2.94 USDC | 🟢 |
| Avalanche | 0x7ebf…96a | ✅ | ✅ 0.099 AVAX (in $0.60–$1.00 range) | 🟢 |
| XLayer | 0x7ebf…96a | ✅ | ✅ | 🟢 |
| Algorand | 6IXPRM…4MTI | ✅ /root/.algorand | ✅ | 🟢 |
| Solana | DjCjLZM…Xbf3 (re-pointed) | ✅ secure/solana-treasury-payto.json | ✅ | 🟢 |

## Gas floor standard — $0.60–$1.00/chain (Jordan, Aug 22)
`steward_bridge.py` `GAS_FLOOR_AVAX` = **0.60** (Jordan's $0.60–$1.00 standard). Each chain
keeps ~$0.60–$1.00 native gas so the agentic bridge can always move funds. Most times we
won't need that much, but the floor means we never worry about stranded funds. Current
Avalanche signer gas = 0.099 AVAX (~$0.74) — within range, no action needed.

## Next actions
1. **Solana**: ✅ DONE — keypair generated + stored (`secure/solana-treasury-payto.json`),
   rail re-pointed to `DjCjLZM…Xbf3`. New address has 0 SOL — fund before first settlement.
2. **Avalanche**: gas in range (0.099 AVAX ≈ $0.74), no action needed.
3. **Algorand**: key confirmed; keep `/root/.algorand/` chmod 600. Algorand Challenge #7/#21
   active ($100K + 500K ALGO) — workshop next Thursday (Jordan may miss; request recording).
