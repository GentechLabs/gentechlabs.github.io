# Handoff to Gentech (HQ) — Revenue Monitor + new keypairs (Aug 22, 2026)

**From:** Treasury → **To:** Gentech (HQ) / Gin

## Summary
All treasury rails are now keyed. The Revenue Monitor will pick up settlements on every
rail. No keyless wallets remain.

## New keypairs / rails (all stored, chmod 600)
| Rail | Address | Key location | Status |
|------|---------|--------------|--------|
| Base | 0x7ebf…96a (re-pointed) | jordan-personal-avax-key | 🟢 |
| Avalanche | 0x7ebf…96a | jordan-personal-avax-key | 🟢 |
| XLayer | 0x7ebf…96a | jordan-personal-avax-key | 🟢 |
| Algorand | 6IXPRM…4MTI | /root/.algorand/ (mnemonic+sk) | 🟢 |
| Solana | DjCjLZM…Xbf3 (NEW) | secure/solana-treasury-payto.json | 🟢 |

## Revenue Monitor — will now pick up all of these
- **Solana** `DjCjLZM…Xbf3` — new keyed rail. Revenue Monitor scans Solana USDC; the new
  address is keyed so any settlement is spendable. (New address has 0 SOL — fund before
  first settlement.)
- **Algorand** `6IXPRM…4MTI` — keyed, settlement test verified live (HTTP 200 `paid:true`).
- **Base/Avalanche/XLayer** — signer keyed, already scanned.

## Key rule now structural
`agent-kit-self-tracking/provision.sh` enforces: every wallet/rail must be keyed or
externally-controlled (Jordan, Aug 22). No keyless wallets going forward.

## Note
Algorand Global x402 Challenge (#7/#21, $100K + 500K ALGO) — workshop next Thursday.
Jordan may miss it; a recording will be sent. Treasury will chase it for the quantum-safe
rotation angle.
