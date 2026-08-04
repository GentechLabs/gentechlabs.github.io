# GTA Execution Rail — LIVE (Aug 4, 2026)

## Breakthrough: CDP wallet secret obtained + wired
- **Root cause of the execution blocker:** the value previously stored at
  `/root/.blockrun/cdp-wallet-secret` (88-char base64) was an **Ed25519 key** — the
  same shape as the read-only `CDP_API_KEY_SECRET`. The SDK's wallet-signing path
  needs a **DER PKCS#8 EC P-256 (secp256r1) key** for ES256 signing.
- **Jordan provided the correct secret** (starts `MIGHAgEA…`, decodes to 138-byte DER
  EC P-256). Verified via `serialization.load_der_private_key` → `ECPrivateKey`, curve
  `secp256r1`. Persisted to `/root/.blockrun/cdp-wallet-secret` (chmod 600).
- **Wired into BOTH profiles** `.env`: `gentech-treasury` and `gentech`.

## Verified working
- `CdpClient()` auth → `list_accounts` → 3 server accounts on Base.
- CDP server account `0x77C6…` funded: **10.5 USDC + 0.0003 ETH** (gas).
- `get_swap_price` (USDC→cbBTC) → live quote `price_ratio=0.0015438`.
- `gta_coinbase_leg.py --symbol BTC --side buy --dry-run` → quote_received:true.

## Cron fix (Treasury profile)
- **Root cause:** GTA/Treasury cron jobs run under the `gentech-treasury` profile, but
  ALL scripts lived in the `gentech` profile `scripts/` dir. Treasury `scripts/` was
  EMPTY → every bare-script `no_agent` cron failed with "Script not found".
- **Fix:** copied the full script set (`tradesta-watcher/signal`, `gta-arb-monitor`,
  `gta-arb-api`, `gta_executor`, `gta_coinbase_leg`, `cmc-watchlist`,
  `narrative-rotation`, `agentic-treasury.*`, `coin-rainbow`, `yield-rainbow`,
  `fed-event-tracker`, `lp-monitor-v2`, `cron_theme`, + JSON state) into
  `/root/.hermes/profiles/gentech-treasury/scripts/`.
- Verified `tradesta-watcher.py` and `gta-arb-monitor.py` run cleanly from treasury dir.
- `agentic-treasury.sh` hardcodes the gentech path — intentional, still works.

## ✅ FIRST REAL TRADE EXECUTED (Aug 4, 2026)
- $5 USDC → cbBTC on Base. **Swap SUCCESS on-chain (block 49546749).**
- USDC 10.5→5.5, cbBTC 0.0000772 received, native ETH intact.

### ⚠️ CRITICAL LESSONS (SDK misled us — verify on-chain ALWAYS)
1. **`executed: true` from the SDK is NOT proof of success.** First attempt returned
   `executed: true` + a tx hash but the tx actually **reverted on-chain**
   (`TRANSFER_FROM_FAILED`, status 0). The Permit2 approval was missing.
2. **Permit2 approval is a REQUIRED one-time step.** CDP server-account USDC swaps use
   Permit2 signatures. Until the wallet grants `approve(USDC → Permit2, max)`, every
   swap reverts silently. Fix: send an `approve(address,uint256)` tx via
   `acct.send_transaction(...)` to Permit2 (`0x000000000022D473030F116dDEE9F6B43aC78BA3`).
   Now done — allowance is max uint, persists.
3. **Always read the tx receipt** (`get_transaction_receipt`, check `status==1`) + verify
   balances changed before declaring success. Never trust the SDK's success flag alone.
4. **CDP CLI bug:** `gta_coinbase_leg.py --dry-run` defaults True with NO way to disable
   via CLI (`--no-dry-run` fails). Real execution must call `run_spot_leg(dry_run=False)`
   programmatically, not the CLI.

## Next
- Remit path CDP server account → Jordan EOA for profit return.
- Buy-list acquisition rails (SOL/TAO/AVAX/LINK/ONDO/PAXG) + vault brain research.
- Expand `SUPPORTED` map in gta_coinbase_leg.py with verified PAXG/AVAX addresses.

## Remit path — BUILT + dry-run verified (Aug 4, 2026)
`gta_remit.py` returns profit from the CDP server account (`0x77C6…`) → Jordan's GTA
EOA (`0x3d117Bf42218c3244AA0Ad011E8651A615230eCb`) → spendable via his Coinbase card.
- Uses the CDP account's `transfer()` — signing key stays in Coinbase's TEE, never touched.
- Dry-run is the default; `--no-dry-run` executes. Verified from BOTH profiles.
- Synced to treasury profile. NOT yet executed with real funds (nothing to remit — $0 profit so far).
- ⚠️ Reminder: ALWAYS verify the receipt on-chain; the SDK's success flag is not proof.

## Buy-list acquisition rails (Aug 4, 2026)
Verified via live CDP quote + CoinGecko + vault brain:

| Asset | Native chain | Base rail? | Acquisition path |
|---|---|---|---|
| **BTC/cbBTC** | Base | ✅ wired + traded | CDP spot leg (DONE, $5 fill) |
| **LINK** | Base | ✅ VERIFIED + added to SUPPORTED | CDP spot leg — 0x88fb150bdc53a65fe94dea0c9ba0a6daf8c6e196, 18 dec, quotes live |
| **PAXG** | Ethereum | ❌ no native Base | CDP spot on **ethereum** net, OR bridged (verify live first) |
| **AVAX** | Avalanche | ❌ no native Base | native Avalanche rail (our wallet / CDP server account is Base-only) |
| **ONDO** | Ethereum | ❌ no native Base | CDP spot on ethereum, OR bridged (verify live) |
| **SOL/TAO** | Solana | ❌ EVM rail N/A | **Jupiter swap** on Solana; USDC bridge Base→Solana exists at `10-Labs/AAE-Dry-Powder-Vault/agent/solana_bridge_adapter.py` (Across) |

**Key discipline:** a CoinGecko `platforms.base` address is a *candidate*, not verified. Only
LINK passed live CDP quote verification. PAXG/AVAX/ONDO/SOL/TAO need either a real on-chain
address verified against `get_swap_price` (for EVM) or a Jupiter swap path (for Solana)
before we claim the buy list is executable. Do NOT invent addresses.

## Agentic Treasury now tracks executed positions (Aug 4, 2026)
- Added a 💼 GTA Pos layer to `agentic-treasury.py` that reads LIVE on-chain balances
  of the CDP server account each run (USDC + cbBTC), so the fused report shows REAL
  executed holdings — not just arb windows.
- Shows: `💼 GTA Pos | USDC $5.50 | cbBTC 0.000077` — tracks our $5 cbBTC fill + remaining USDC.
- Implementation: web3 eth_call (base.drpc.org), `int.from_bytes(raw,'big')` (NOT int(raw,16)
  — eth_call returns bytes, not hex). RPC 403s raw urllib; must use web3.
- Cron (Agentic Treasury `1cbde1d52242`) picks this up automatically — no job change needed.
