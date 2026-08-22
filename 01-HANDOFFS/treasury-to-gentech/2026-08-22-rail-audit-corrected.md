# Treasury Rail Audit — CORRECTED (Aug 22, 2026)

**From:** Treasury → **To:** Gentech (HQ) / Gin
**Supersedes:** `2026-08-22-rail-audit.md` (first pass had 2 errors — corrected below).

## Correction — Algorand is KEYED (first pass was wrong)
The Algorand key WAS generated Aug 5 and lives at `/root/.algorand/`:
- `jordan-mainnet.sk` (89 bytes, chmod 600)
- `jordan-mainnet.mnemonic` (25 words, chmod 600)
- `jordan-mainnet.addr` (matches advertised payTo `6IXPRM…4MTI` exactly ✅)
First pass searched the wrong dirs. **Algorand = 🟢 keyed, movable.**

## Correction — Solana is the genuinely keyless rail
`Hv2N2XJ…57Ru` (advertised in `.env` as `X402_PAYTO_SOLANA`) matches **NO keypair on disk**.
Swept `.gentech/wallets/`, `.solana-trade/`, `.blockrun/`, both `secure/` — the only Solana
keypair we hold is `BE815V7…UvP` (jordan-personal, different address). **Solana = 🔴 keyless.**

## Final rail status
| Rail | Receive | Key? | Move? | Status |
|------|---------|------|-------|--------|
| Base | 0x7ebf…96a (re-pointed today) | ✅ | ✅ 2.94 USDC | 🟢 |
| Avalanche | 0x7ebf…96a | ✅ | ⚠️ 0.099 AVAX (< $1 floor) | 🟡 top-up gas |
| XLayer | 0x7ebf…96a | ✅ | ✅ | 🟢 |
| Algorand | 6IXPRM…4MTI | ✅ /root/.algorand | ✅ | 🟢 |
| Solana | Hv2N2…57Ru | ❌ NO KEYPAIR | ❌ | 🔴 |

## Gas floor standard — $0.60–$1.00/chain (Jordan, Aug 22)
`steward_bridge.py` `GAS_FLOOR_AVAX` = **0.60** (Jordan's $0.60–$1.00 standard). Each chain
keeps ~$0.60–$1.00 native gas so the agentic bridge can always move funds. Most times we
won't need that much, but the floor means we never worry about stranded funds. Current
Avalanche signer gas = 0.099 AVAX (~$0.74) — within range, no action needed.

## Next actions
1. **Solana**: generate + store a keypair, or re-point `X402_PAYTO_SOLANA` to a wallet we
   control. (Treasury owns — Jordan greenlit generating both.)
2. **Avalanche**: top up native gas to ≥$1.00.
3. **Algorand**: key confirmed; keep `/root/.algorand/` chmod 600. Algorand Challenge #7/#21
   active ($100K + 500K ALGO) — workshop next Thursday (Jordan may miss; request recording).
