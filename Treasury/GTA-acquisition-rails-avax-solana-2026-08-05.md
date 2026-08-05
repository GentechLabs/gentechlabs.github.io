# GTA Acquisition Rails — Avalanche + Solana Research (Aug 5, 2026)

## Avalanche rail: Almanak (almanak.co) — DeFi Agent Framework
- `pip install almanak` (v1.0.9 on PyPI; 1.0.0–1.0.9). Open-source Python SDK:
  github.com/almanak-co/sdk.
- **Avalanche-native**: official demo strategies are `traderjoe_lp` (TraderJoe V2),
  `benqi_lending_lifecycle`, `benqi_looping` (leveraged AVAX loop) — all on Avalanche.
- 12 chains / 20+ protocol connectors (Uniswap, Aave, Morpho, GMX, Polymarket, TraderJoe, BENQI...).
- Intent-based: `Swap`, `LP`, `Borrow` intents; SDK compiles + executes.
- `almanak ax` CLI does DIRECT DeFi actions — `almanak ax swap USDC AVAX <amt> --dry-run`,
  `almanak ax balance USDC --chain avalanche`, natural-language mode.
- Non-custodial: deploys via Safe smart accounts; gateway keeps secrets isolated (gRPC sidecar).
- Backtest: PnL sim, Anvil fork paper trade, Monte Carlo, parameter sweeps.
- Backed by Delphi Labs, Bankless VC, Hashkey, Matrix (institutional credibility).
- **Constraint:** requires **Python 3.12+**; our venv is 3.11.15 → needs a separate 3.12 venv.
- Avalanche USDC from brain config: `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` (C-Chain).
- AVAX token = native C-Chain asset.

## Solana rail: Jupiter — DEX aggregator (jup.ag)
- **The** swap rail for Solana. Routes across 30+ DEXs (Raydium, Orca, Meteora, Phoenix) in one call.
- 0% platform fee; ~0.05–0.30% underlying DEX fees; swaps confirm in 1–2s; sub-$0.01 gas.
- No official Python SDK → either use community **jupiter-python-sdk** (0xTaoDev) or call
  REST API directly + sign with `solders`/`solana`:
  - Quote: `GET https://quote-api.jup.ag/v6/quote` (inputMint/outputMint/amount/slippageBps)
  - Swap: `POST https://api.jup.ag/swap/v1/swap` (keyless lite `lite-api.jup.ag`, or X-API-Key)
  - Sign `swapTransaction` (base64 → VersionedTransaction) with `Keypair`, send via RPC.
  - **Always use median priority fee** (not max) via getRecentPrioritizationFees.
- SOL mint: `So11111111111111111111111111111111111111112`; USDC mint:
  `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`.
- **TAO (Bittensor)** is native on Solana — Jupiter can buy it (input SOL or bridged USDC).
- Funding: bridge USDC Base→Solana via **CCTP / Across** (adapter exists at
  `10-Labs/AAE-Dry-Powder-Vault/agent/solana_bridge_adapter.py`, Across SpokePool on Base).
- Needs a **Solana keypair** (solders Keypair) + RPC endpoint.

## Buy-list coverage after this
| Asset | Rail | Status |
|---|---|---|
| BTC, LINK | CDP spot (Base) | ✅ live |
| PAXG, ONDO | CDP spot (Ethereum) | ✅ live |
| **AVAX** | **Almanak** (Avalanche) | 🔧 candidate — needs 3.12 venv + Safe setup |
| **SOL/TAO** | **Jupiter** (Solana) | 🔧 candidate — needs keypair + USDC bridge + RPC |

## Decision needed from Jordan
1. AVAX via Almanak — build a 3.12 venv + scaffold a strategy? (bigger lift; institutional-grade
   but heavier than our thin CDP leg). Or keep AVAX on a simpler native Avalanche swap first?
2. SOL/TAO via Jupiter — build a thin `gta_solana_leg.py` mirroring our CDP leg pattern
   (quote → sign → swap → verify tx)? This matches our existing architecture best.

## Solana leg BUILT (Aug 5, 2026) — gta_solana_leg.py
- Mirrors the CDP leg pattern: quote -> sign -> swap -> verify. Uses Jupiter.
- SOL VERIFIED + quoting live: ~0.0135 SOL per $1 USDC (dry-run).
- TAO mint NOT yet verified -> leg gracefully returns unverified-mint-TAO. (Discipline:
  never invent an address. Placeholder returned "WrongSize" from Jupiter.)
- ⚠️ Jupiter endpoint gotcha: `quote-api.jup.ag` and `tokens.jup.ag` are IPv6-only /
  blocked on this VPS. The working host is **`api.jup.ag/swap/v1/quote`** (IPv4, returns
  real quotes). lite-api is IPv6-only. This is the #1 gotcha for any Solana build here.
- Wallet: existing keypair 4CTVx59fQThAQEN1yV3eUMsVCcmuXNjCmfRH8Bd9UcPb (Anchor deploy key)
  has **0 SOL** — needs SOL for gas + USDC (bridged Base->Solana via CCTP/Across) to trade.
- To execute SOL: fund the keypair, set SOLANA_KEYPAIR_FILE, run with no --dry-run.
