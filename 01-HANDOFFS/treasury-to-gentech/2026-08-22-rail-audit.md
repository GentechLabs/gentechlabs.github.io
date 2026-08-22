# Treasury Rail Audit — receive / move / key ownership (Aug 22, 2026)

**From:** Treasury → **To:** Gentech (HQ) / Gin
**Trigger:** Stranded $33.63 in `0xF9dc…734` exposed that receive-only ≠ spendable. Jordan
asked for a full audit of every chain we're registered on: **can we receive, can we move,
do we hold the key?**

## The rule now hard-coded (Jordan)
Every wallet/rail we create (agentic treasury OR API receive/payTo) MUST auto-generate
AND store the private key — or point only to a wallet we control. Never keyless.

## Audit result — live gateway `api.gentechlabs.net` (manifest v9.3.2)

Advertised settlement rails: **base, algorand, avalanche, xlayer, solana** (endpoint-level:
ethereum, bnb, arbitrum). Cross-referenced each rail's receive address against our key inventory.

| Rail | Receive address | Key held? | Can move? | Status |
|------|----------------|-----------|-----------|--------|
| **Base** | `0x7ebf…96a` (signer) — RE-POINTED today | ✅ jordan-personal-avax-key | ✅ 2.94 USDC + 0.0007 ETH | 🟢 FIXED today |
| **Avalanche** | `0x7ebf…96a` | ✅ | ✅ 0.099 AVAX native | 🟢 |
| **XLayer** | `0x7ebf…96a` | ✅ | ✅ 0 native (flat) | 🟢 keyed |
| **Solana** | `Hv2N2XJ…57Ru` | ❌ **NO KEYPAIR** | ❌ | 🔴 KEYLESS |
| **Algorand** | `6IXPRMSYQBZ…4MTI` | ❌ NO KEY/MNEMONIC | ❌ | 🔴 KEYLESS |

### Two live-keyless rails — same bug as `0xF9dc…734`
- **Solana** advertises receiving on `Hv2N2N…57Ru` (10M lamports = 0.01 SOL), but there is
  NO `SOLANA_PRIVATE_KEY`, no `SOLANA_KEYPAIR_FILE`, and no keypair JSON anywhere.
  `gta_solana_leg.py` / `solana_homebase.py` will only execute if a keypair exists — so any
  Solana settlement would be received and then **unspendable**. Fix BEFORE first real SOL settlement.
- **Algorand** advertises `6IXPRM…4MTI` but no mnemonic/algosdk key exists. Same risk.

## Re-point performed today (Base)
- `X402_PAYTO_ADDRESS` now = `0x7ebf…96a` in `gentech/.env` (was unset → fell back to stranded `0xF9dc…734`).
- `server.py` `payto_default` for Base updated `0xF9dc…734→0x7ebf…96a` so the fallback is safe.
- Verified: 0 functional refs to `0xF9dc` remain in gateway.

## Next actions (Gin / Treasury)
1. **Solana**: before first real settlement, generate + store a Solana keypair, or re-point
   rail to a wallet we control. (Treasury owns this.)
2. **Algorand**: same — key/mnemonic or re-point. If Algorand is a dead/low-value rail, drop it.
3. **XLayer/Avalanche** confirmed keyed. Monitor per revenue cron.
4. Update marketplace registry rows that advertise these chains when rails change.

## Clean cost of the lesson
~$33.63 stranded (the `0xF9dc…734` wallet). Compare to a real user's funds or a live revenue
stream at scale. We bought the rule cheap.
