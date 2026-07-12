---
title: "Codebase Assessment — Almanak SDK (DeFi Agent Framework)"
date: 2026-04-29
type: assessment
tags: [defi, sdk, python, traderjoe, avalanche, lp, strategy, aae-integration]
status: ready
---

# Codebase Assessment: Almanak SDK
**Repo:** https://github.com/almanak-co/sdk
**License:** Apache-2.0 | **Stars:** 53 | **Language:** Python 3.12+
**Version:** 2.15.0 | **Commits:** 1,112 | **Last push:** 6 hours ago

## Overview
Almanak is an intent-based Python framework for developing, testing, and deploying autonomous DeFi strategies. Strategies express trading logic as high-level intents (Swap, LP, Borrow, etc.) — the framework handles compilation, execution, and state management across 12 chains and 20+ protocols. Includes a gRPC gateway for non-custodial execution via Safe wallets, backtesting engine with Monte Carlo analysis, and an AI coding assistant ("Almanak Code").

## Codebase Metrics
| Metric | Value |
|--------|-------|
| Files | 2,726 Python files |
| Lines of code | 1,075,352 |
| Proto definitions | 1 (gateway.proto) |
| Demo strategies | 100+ (across 12 chains) |
| Test directories | 15+ (unit, integration, e2e, visual) |
| Protocol connectors | 25+ (TraderJoe, Uniswap, Aave, Morpho, GMX, etc.) |

## Architecture
```
almanak/
├── framework/          # Core SDK
│   ├── connectors/     # Protocol adapters (traderjoe_v2, uniswap_v3, aave_v3, etc.)
│   ├── intents/        # Intent vocabulary + compiler (Intent → ActionBundle)
│   ├── strategies/     # Strategy base classes (IntentStrategy, MultiStepStrategy)
│   ├── state/          # HOT/WARM persistence (SQLite/PostgreSQL)
│   ├── execution/      # Transaction signing, simulation, submission
│   ├── permissions/    # Zodiac Roles auto-generated manifests
│   ├── backtesting/    # PnL simulation, Monte Carlo, parameter sweeps
│   ├── data/           # Price feeds, token resolver, technical indicators
│   ├── portfolio/      # Portfolio tracking
│   ├── alerting/       # Telegram/Slack notifications
│   └── web3/           # Web3 utilities
├── gateway/            # gRPC sidecar (strategy ↔ platform bridge)
│   ├── proto/          # Protobuf definitions
│   ├── core/           # Settings, auth
│   ├── services/       # gRPC service implementations
│   └── lifecycle/      # Gateway process management
├── demo_strategies/    # 100+ example strategies
│   ├── traderjoe_lp/          # ← DIRECTLY RELEVANT TO AAE
│   ├── traderjoe_crisis_lp/   # Emergency LP management
│   ├── traderjoe_sweep_lp/    # Sweep + LP strategy
│   └── ...
├── strategies/
│   ├── probes/         # Lifecycle probes (avalanche_lp_lifecycle = us)
│   └── experiments/    # Edge strategies
└── cli/                # almanak CLI (strat new, strat run, strat backtest)
```

## Key Integration Points with AAE

### 1. TraderJoe V2 Connector (930 + 972 lines)
Full SDK for TraderJoe Liquidity Book V2 on Avalanche:
- `TraderJoeV2SDK` — pool discovery, swap quotes, LP operations
- `TraderJoeV2Adapter` — intent compilation for Swap, LP_OPEN, LP_CLOSE
- Receipt parser for fee tracking
- Supports bin math, fungible LP tokens (ERC1155), dynamic fees

**AAE overlap:** Our `lp-position-reader.py` (474 lines) does raw eth_call against the same contracts. Almanak's connector is production-tested with 930 lines of adapter logic + 972 lines of SDK.

### 2. Intent System
Strategies return high-level intents:
```python
Intent.swap("USDC", "WAVAX", amount_usd=Decimal("1"))
Intent.lp_open(protocol="traderjoe_v2", pool="WAVAX/USDC/20", ...)
Intent.lp_close(position_id="...")
```
Compiler handles: token resolution, approval, routing, gas estimation, slippage.

**AAE opportunity:** Replace manual `decide()` logic in our cron with declarative intents.

### 3. Avalanche LP Lifecycle Probe
Almanak already has a probe strategy (`strategies/probes/avalanche_lp_lifecycle/`) that does:
- Bridge USDC Base→Avalanche
- Swap USDC→WAVAX via Enso
- LP_OPEN on TraderJoe V2
- LP_CLOSE
- Swap back + bridge out

**This is exactly what AAE does manually.** Their probe is a fire-once phase machine with budget tracking.

### 4. State Management
Three-tier persistence (HOT/WARM/COLD) with CAS semantics:
- SQLite for local dev
- PostgreSQL for production
- Auto-migrations, position tracking

**AAE opportunity:** Replace our JSON state files (`.lfj-position-state.json`, `.lfj-range-state.json`) with proper state management.

### 5. Backtesting Engine
- PnL simulation against historical data
- Monte Carlo analysis
- Parameter sweeps with Optuna (Bayesian optimization)
- Paper trading on Anvil forks

**AAE opportunity:** Backtest our LP range strategies before deploying. Currently we rebalance based on gut feel.

### 6. Gateway Architecture
gRPC sidecar between strategy containers and platform:
- Non-custodial via Safe wallets
- Transaction simulation (Tenderly, Alchemy)
- Flashbots submission
- Zodiac Roles permissions (auto-generated minimum-privilege manifests)

**AAE opportunity:** Instead of raw private key signing, use gateway for secure execution.

### 7. Alerting & Monitoring
Built-in Telegram/Slack notifications, stuck detection, live CLI dashboard.

**AAE overlap:** Our cron already does Telegram alerts. Almanak's alerting is more robust (stuck tx detection, emergency management).

## Dependencies
| Package | Purpose |
|---------|---------|
| web3>=6.15.1 | EVM interaction |
| grpcio | Gateway communication |
| pydantic | Data models |
| pandas | Data analysis |
| optuna | Bayesian optimization |
| asyncpg | PostgreSQL |
| streamlit | Dashboard |
| plotly | Charts |
| python-kraken-sdk | CEX integration |

## API Keys Required
| Provider | Purpose | Required? |
|----------|---------|-----------|
| Alchemy | RPC + archive nodes | Optional (free public RPCs exist) |
| Enso Finance | DEX aggregator routing | Optional |
| The Graph | Historical subgraph data | For backtesting |
| CoinGecko | Price data | For backtesting |
| Almanak Platform | Deployment | For cloud deployment only |

## Setup Requirements
```bash
pipx install almanak
# or
pip install almanak

# For development
git clone https://github.com/almanak-co/sdk.git
cd sdk
uv sync
```

## Functional Testing
| Test | Result |
|------|--------|
| Installation | ✅ `pip install almanak` works |
| Import check | ✅ `import almanak` succeeds |
| CLI available | ✅ `almanak --help` works |
| TraderJoe connector code | ✅ Full adapter + SDK (1,902 lines) |
| Avalanche LP probe | ✅ Complete lifecycle strategy |
| Backtesting engine | ✅ Optuna + Monte Carlo |
| Test suite | ⚠️ Not run (requires Anvil + RPC) |

## Strengths ✅
1. **Production-grade TraderJoe V2 connector** — 1,902 lines, battle-tested with receipt parsing
2. **Intent abstraction** — clean separation of strategy logic from execution mechanics
3. **Backtesting** — Monte Carlo + parameter sweeps (we have nothing like this)
4. **100+ demo strategies** — massive reference library including 7 TraderJoe variants
5. **Active development** — 1,112 commits, last commit 6 hours ago
6. **Apache 2.0** — permissive license, no restrictions
7. **Multi-chain** — 12 chains including Avalanche (our chain)
8. **Gateway security** — non-custodial, Zodiac Roles, simulation before execution
9. **1M+ lines** — this is institutional-quality code
10. **Probes** — they already have an `avalanche_lp_lifecycle` probe that mirrors AAE

## Concerns / Questions ⚠️
1. **Heavy dependency tree** — web3, grpc, pandas, optuna, streamlit, asyncpg. Our AAE monitor is 474 lines of urllib. This is a 1M-line framework.
2. **Gateway complexity** — gRPC sidecar is powerful but adds operational overhead. Do we need it for a single LP position?
3. **Strategy container model** — Almanak assumes strategies run in isolated containers via gateway. Our AAE runs as a cron job. Would need adaptation.
4. **Overkill risk** — We have ONE LP position on ONE pool. Almanak is built for managing portfolios across 12 chains.
5. **Learning curve** — Intent vocabulary, compiler, state machine, gateway... significant onboarding investment.

## Fit Assessment
**Rating: ⭐⭐⭐ (3/5) — Right domain, wrong scale**

### Direct Overlap (High Value)
- **TraderJoe V2 SDK** — could replace our raw eth_call reader entirely
- **Backtesting** — validate range strategies before deploying
- **State management** — replace JSON files with proper persistence

### Partial Overlap (Medium Value)
- **Intent system** — clean abstraction but adds complexity for our use case
- **Alerting** — more robust than our cron alerts
- **Permission system** — useful if we ever use Safe wallets

### Overkill (Low Value for Us)
- **Gateway** — we don't need gRPC sidecar for one position
- **Multi-chain** — we're Avalanche-only for AAE
- **100+ strategies** — we have one strategy

## Potential Use Cases

### Path A: Adopt TraderJoe SDK Only (Recommended)
Extract `almanak/framework/connectors/traderjoe_v2/` as a standalone library. Replace our raw contract calls with the production SDK. Get: pool discovery, swap quotes, LP math, receipt parsing, fee tracking. Estimated effort: 1-2 days.

### Path B: Use Backtesting Engine
Run historical backtests on WAVAX/USDC ranges to optimize our rebalancing strategy. Use Optuna for parameter sweeps. Estimated effort: half day setup.

### Path C: Full Framework Adoption (Not Recommended)
Rewrite AAE as an Almanak strategy. Use intents, gateway, state management. Massive overkill for our single position but would teach us the framework for future strategies.

## Recommendation
**Path A** is the play. The TraderJoe V2 connector is exactly what we need — production-tested, handles all the bin math, receipt parsing, and fee tracking that our 474-line script does manually. The backtesting engine (Path B) is a bonus for optimizing ranges.

Don't adopt the full framework. It's brilliant engineering but designed for multi-chain portfolio management. We have one LP position. Use the connector library, maybe the backtesting, skip the gateway.

## Next Steps
1. Clone the repo (done)
2. Test `TraderJoeV2SDK` against our pool — verify it can read our position
3. Backtest WAVAX/USDC ranges over last 30 days
4. If SDK works, replace `lp-position-reader.py` with Almanak connector
5. Consider using `Intent.lp_open/LP_CLOSE` for automated rebalancing in cron
