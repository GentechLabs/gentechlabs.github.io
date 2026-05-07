---
name: blockchain-operations
description: Blockchain operations — DeFi strategy engines, protocol monitoring, cross-chain queries (Base, Solana, Avalanche), LP rebalancing, and price feeds.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [blockchain, defi, protocol, base, solana, avalanche, lp, price]
    related_skills: []
---

# Blockchain Operations

Class-level skill covering all blockchain workflows. Use this for:
- DeFi strategy engines (regime detection, allocation matrices)
- Protocol ecosystem monitoring (GitHub, SDKs, CVEs)
- Cross-chain queries (Base, Solana, Avalanche)
- LP range rebalancing and monitoring
- Price feeds and fallback chains

---

## 1. DeFi Hybrid Strategy Engine

Build multi-strategy portfolio allocation systems that compare returns across DeFi strategies and dynamically rotate based on market conditions.

### Architecture
```
Market Data → Regime Classification → Strategy Comparison → Allocation Recommendation
     │                │                       │                      │
 DexScreener    regime_classifier.py   strategy_returns.py   allocation_engine.py
 DeFiLlama                                (DeFiLlama rates)
 On-chain RPC
```

### Module Files
| Module | File | Purpose |
|--------|------|---------|
| Regime Classifier | `regime_classifier.py` | Classifies market into 6 regimes |
| Strategy Returns | `strategy_returns.py` | Fetches rates, compares returns across strategies |
| Allocation Engine | `allocation_engine.py` | Maps regime → allocation, detects rotation needs |
| Unified Pipeline | `aae-hybrid-signal.py` | Chains all three, outputs unified signal |

### Regime Classification
| Regime | Condition | Allocation Tilt |
|--------|-----------|-----------------|
| `BULL_TRENDING` | Momentum >10%, volume >1.3x, RSI >55 | HODL dominant (60%) |
| `BEAR_TRENDING` | Momentum <-10%, volume >1.3x, RSI <45 | Staking dominant (50%) |
| `RANGE_BOUND` | |Momentum| <5%, volume normal | LP dominant (40%) |
| `HIGH_VOLATILITY` | ATR/price >8% | Diversified (no tilt) |
| `ACCUMULATION` | Flat after dump, volume declining | HODL + staking (65%) |
| `PRICE_DISCOVERY` | New highs/lows, wide range | HODL dominant (70%) |

### Pitfalls
- **DeFiLlama project names:** Benqi is `benqi-lending` + `benqi-staked-avax`, NOT `benqi`.
- **DexScreener 404 errors:** Always include `User-Agent` header.
- **Price history cold start:** Regime classifier needs 15+ data points for RSI/ATR.

### Multi-Year Compounding Strategy: Cross-Chain Yield + RWA Diversification
**Use case:** 2-3 year horizon with DCA approach, combining active yield generation on high-throughput chains with directional holds on low-correlation RWA tokens (real estate, commodities).

#### Strategic Architecture
```
Yield Generation Layer (Active)        RWA Diversification Layer (Passive)
Solana yield farms (Marinade,          PROPS/LAND (Avalanche RWA tokens)
MarginFi, Raydium) → stablecoin        → inflation hedge, non-correlated
compounding → capital base              → long-term holds (not LP)
         ↓                                       ↓
Profit allocation (DCA)               Separate wallet tracking
         ↓
Reinvest into yield base + RWA adds
```

#### Allocation Matrix (Regime-Aware)
| Regime | Yield Farm % | RWA Hold % | Blue Chip % | Rationale |
|--------|--------------|------------|-------------|-----------|
| `RANGE_BOUND` | 70% | 10% | 20% | LP efficiency high, harvest yield to buy RWA on dips |
| `BULL_TRENDING` | 60% | 15% | 25% | RWA outperforms in late-cycle inflation; increase allocation |
| `BEAR_TRENDING` | 50% | 20% | 30% | RWA as defensive hold; reduce farm risk, hold more |
| `HIGH_VOLATILITY` | 65% | 5% | 30% | RWA illiquid → avoid adding during volatility |
| `ACCUMULATION` | 75% | 10% | 15% | Aggressive yield compounding, minimal RWA |
| `PRICE_DISCOVERY` | 50% | 25% | 25% | New market regime → increase diversification |

#### Execution Workflow
1. **Token Discovery** — Watchlist scanning (PROPS: propbase, LAND: landshare via CoinGecko)
2. **Chain/Pool Verification** — Confirm DEX pool existence on target chain (LFJ, Pangolin for Avalanche)
3. **IL Risk Assessment** — Small-cap + low TVL = directional exposure dominates; require wide ranges (>15% spread)
4. **Reward Audit** — Check for staking/farming programs beyond pure LP fees
5. **Position Sizing** — Cap RWA allocation at 5-10% per token due to micro-cap ($795K-$2.4M MCap)
6. **Monitoring Hooks** — Separate trackers: yield farm performance (daily) vs RWA price (weekly)

#### Key Insights
- **Yield farm on Solana** (low fees, high throughput) → compound in USDC/SOL pools
- **Hold RWA tokens directly** (not as LP) → avoid IL from volatility mismatch
- **Treat RWA as inflation hedge** — not yield generator; expect 0-5% APY max vs 8-20% on Solana farms
- **Rebalance quarterly** — shift profits from yield layer to RWA layer based on MCap growth

#### Pitfalls Specific to RWA Diversification Strategy
- **Cross-chain fragmentation** — Yield on Solana, holds on Avalanche → need bridge monitoring and wallet segregation
- **Micro-cap liquidity risk** — PROPS ($2.4M), LAND ($795K) can have 24h volume < $10K → slippage on buys
- **Token reward dependency** — Small-cap RWA LPs often rely on token emissions, not trading fees; if rewards dry up, APY collapses
- **Data availability gaps** — LAND token often missing from price APIs; fallback to CoinGecko only
- **Narrative drift** — RWA meta can rotate out; monitor sector trends quarterly

#### References
- [Cross-chain allocation monitor design](references/cross-chain-allocation-monitor.md)
- [RWA token IL calculator](references/rwa-il-calculator.md)
- [Solana yield farm platform comparison](references/solana-yield-platforms.md)

### References
- [DeFiLlama API guide](references/defillama-api.md)
- [Regime classification debug script](scripts/regime-debug.py)

---

## 2. Protocol Ecosystem Monitoring

Automated bi-weekly/monthly research for blockchain protocol ecosystems. Tracks stats, SDK updates, GitHub activity, security risks, and build opportunities.

### Key Data Points
| Field | Why It Matters |
|-------|---------------|
| Transactions (30d) | Adoption velocity |
| Volume (30d) | Economic activity |
| Buyers/Sellers | Network health |
| Ecosystem partners | Integration surface |

### GitHub Activity
```bash
# Recent commits (last 5)
curl -s "https://api.github.com/repos/[org]/[repo]/commits?per_page=5" | jq -r '.[].commit.message'

# Search for new SDKs, facilitators, or infra
curl -s "https://api.github.com/search/repositories?q=[protocol]+fork:true+stars:>5&per_page=5" | jq -r '.items[] | "\(.full_name) - \(.stargazers_count) stars"'
```

### Security Risks
```bash
# Search for CVEs or exploits in GitHub issues
curl -s "https://api.github.com/search/issues?q=repo:[org]/[repo]+label:security" | jq -r '.items[] | "\\(.title) - \\(.html_url)"'

# Check GitHub Security Advisories for the org
curl -s "https://api.github.com/repos/[org]/[repo]/security-advisories" | jq -r '.[] | "\\(.ghsa_id): \\(.summary) [\\(.severity)]"'

# Fetch advisory details (requires GHSA ID)
curl -s "https://api.github.com/repos/[org]/[repo]/security-advisories/GHSA-XXXX-XXXX-XXXX" | jq '{summary, severity, description, vulnerabilities}'
```

### References
- [Protocol research template](templates/protocol-research-template.md)
- [GitHub API rate limit guide](references/github-api-limits.md)

---

## 8. Protocol Ecosystem Research & Intelligence (x402 Pattern)

**Use this for:** Comprehensive bi-weekly protocol health checks — stats, SDK versions, ecosystem integrators, security posture, and build opportunity identification.

### Research Vectors (Parallelize These)
| Vector | Primary Sources | Fallback Sources |
|--------|----------------|-----------------|
| Live stats | `x402.org` homepage HTML | `/ecosystem` page, docs subdomains |
| SDK versions | npm registry `registry.npmjs.org/<package>` | unpkg.com, jsdelivr mirrors |
| GitHub activity | `api.github.com/repos/<org>/<repo>` | raw.githubusercontent.com (bypasses rate limits) |
| Security advisories | `api.github.com/repos/.../security-advisories` | HackerOne program page |
| Contract code | `api.github.com/repos/.../contents/contracts` | direct raw URL fetch |
| Ecosystem integrators | `/ecosystem` page partner data | GitHub code search `x402+[name]` |

### Core Methodology
```bash
# 1. Stats extraction — when structured API absent, parse HTML context
# x402 pattern: numbers embedded in text blocks "75.41M Transactions $24.24M Volume"
curl -s https://x402.org | \
  grep -oP '\d+(?:\.\d+)?[KM]? (?:Transactions|Volume|Buyers|Sellers)' | \
  head -4

# 2. NPM version alignment check — verify all @x402/* packages at same version
for pkg in @x402/core @x402/evm @x402/svm @x402/extensions; do
  curl -s "https://registry.npmjs.org/$pkg" | jq -r '"\(.name) latest: \(.["dist-tags"].latest)"'
done

# 3. GitHub rate limit bypass — switch to raw.githubusercontent.com
# If api.github.com returns 403, use:
curl -s "https://raw.githubusercontent.com/x402-foundation/x402/main/README.md"

# 4. Security advisory deep-dive — fetch GHSA details via both HTML and API
curl -s "https://github.com/x402-foundation/x402/security/advisories/GHSA-xxx"  # HTML full description
curl -s "https://api.github.com/repos/x402-foundation/x402/security-advisories/GHSA-xxx" | jq .  # JSON

# 5. Ecosystem partner discovery — scrape ecosystem page for org/repo pairs
curl -s https://x402.org/ecosystem | \
  grep -oP 'github\.com/\K[A-Za-z0-9_-]+/[A-Za-z0-9_-]+' | sort -u
```

### Pitfalls (Hard-Won)
- **Rate limit 403 on GitHub API:** Unauthenticated requests have very low limits. Use `raw.githubusercontent.com` for file content; it's not rate-limited the same way. For repo metadata, have a personal access token ready or accept partial results.
- **Stats not in structured JSON:** Many protocol homepages (x402, etc.) embed stats directly in HTML text with no API. You must parse surrounding text context. Look for patterns like "Last 30 days 75.41M Transactions $24.24M Volume".
- **Multiple namespace migrations:** Protocols often migrate from one npm namespace to another (`@dexterai/x402` → `@x402/*`). Always check BOTH namespaces for active development and version history.
- **Advisory details require dual-source:** GitHub advisory API (`/security-advisories/GHSA-id`) often returns minimal JSON; the HTML page (`github.com/.../security/advisories/GHSA-id`) contains full description and impact details. Fetch both.
- **Contracts may not be in `contracts/` directory:** x402 stores mechanism code in TypeScript packages, not Solidity. Do not assume EVM projects have Solidity files; check `packages/*/src` for payment logic. Search by `.sol` extension if you expect contracts.
- **Version alignment across monorepo:** When a project uses a monorepo (like `x402-foundation/x402`), all `@x402/*` packages should have the same version. If you see misalignment (e.g., core 2.11.0 but evm 2.10.0), it indicates a release lag or breaking change in progress.
- **Ecosystem page data may be in TypeScript files, not JSON:** x402 stores partner data in `typescript/site/app/ecosystem/data.ts` as TypeScript interfaces + arrays, not JSON. You must extract the array literal from the TS source; do not expect a `.json` endpoint.
- **Zero-Solidity protocol:** Some protocols (x402, etc.) are application-layer HTTP standards with NO on-chain contracts. The "contracts" directory may be empty or contain only interfaces. Base security assumptions on SDK code, not Solidity analysis.

### Output Structure (Report Template)
```markdown
## 📊 Stats
- [ ] Current 30-day tx/volume numbers vs last check
- [ ] Buyer/seller counts

## 🆕 What's New
- [ ] New SDK versions (major/minor/patch)
- [ ] New ecosystem adopters (named, with evidence links)
- [ ] GitHub repo changes (migration, restructuring)

## 🔒 Security
- [ ] Active advisories (GHSA IDs, severity, affected packages, action required)
- [ ] New CVEs in dependencies (check viem, solana/web3.js, etc.)
- [ ] Known exploits/attack patterns in ecosystem repos

## ⚡ Labs Relevance
- [ ] Immediate upgrade actions (who, what version)
- [ ] Protocol version compatibility notes (v1 vs v2)
- [ ] Trust model changes (facilitator, custody, verification)

## 🏗️ Build Opportunities
- [ ] Infrastructure gaps identified
- [ ] Hackathon-worthy project ideas
- [ ] Tooling needs (monitoring, migration, testing)
```

### Critical Intelligence Cross-Checks
1. **Version drift:** Compare latest against last-check baseline. Major bumps (1.x→2.x, namespace changes) = breaking changes.
2. **Advisory scope:** Distinguish "clients not affected" from "facilitators must upgrade" — impacts your architecture decisions.
3. **Integrator cadence:** New projects using x402 in last 30 days = growth vector; stale projects = declining interest.
4. **Dependency chain:** Check versions of `viem`, `@solana/*`, `zod` — a vulnerability in any cascades to your builds.

### References
- [x402 V2 spec separation patterns](references/x402-v2-spec-changes.md)
- [NPM namespace migration checklist](references/npm-namespace-migration.md)
- [GitHub rate limit bypass techniques](references/github-rate-limit-bypass.md)
- [x402 ecosystem partner extraction TS pattern](references/x402-ecosystem-data-extraction.md)
- [GHSA advisory API vs HTML content differences](references/ghsa-advisory-fetch-pattern.md)

---

## 3. Base Blockchain Queries

Query Base (Ethereum L2) blockchain data with USD pricing — wallet balances, token info, transaction details, gas analysis, contract inspection, whale detection, and live network stats.

### Quick Reference
```bash
python3 base_client.py wallet   <address> [--limit N] [--all] [--no-prices]
python3 base_client.py tx       <hash>
python3 base_client.py token    <contract_address>
python3 base_client.py gas
python3 base_client.py contract <address>
python3 base_client.py whales   [--min-eth N]
python3 base_client.py stats
python3 base_client.py price    <contract_address_or_symbol>
```

### Pitfalls
- **CoinGecko rate-limits:** ~10-30 requests/minute. Use `--no-prices` for speed.
- **Public RPC rate-limits:** Set `BASE_RPC_URL` to a private endpoint.
- **Wallet shows known tokens only:** EVM chains have no built-in "get all tokens" RPC.

### References
- [Base RPC endpoints](references/base-rpc-endpoints.md)
- [CoinGecko rate limit guide](references/coingecko-limits.md)

---

## 4. Solana Blockchain Queries

Query Solana blockchain data with USD pricing — wallet balances, token portfolios, transaction details, NFTs, whale detection, and live network stats.

### Quick Reference
```bash
python3 solana_client.py wallet   <address> [--limit N] [--all] [--no-prices]
python3 solana_client.py tx       <signature>
python3 solana_client.py token    <mint_address>
python3 solana_client.py activity <address> [--limit N]
python3 solana_client.py nft      <address>
python3 solana_client.py whales   [--min-sol N]
python3 solana_client.py stats
python3 solana_client.py price    <mint_or_symbol>
```

### Pitfalls
- **NFT detection is heuristic:** amount=1 + decimals=0. Compressed NFTs (cNFTs) and Token-2022 NFTs won't appear.
- **Transaction history:** Public RPC keeps ~2 days. Older transactions may not be available.

### References
- [Solana RPC endpoints](references/solana-rpc-endpoints.md)

---

## 5. Crypto Price Fetch

Fetch cryptocurrency prices with automatic fallback between providers.

### Fallback Chain
1. **CoinMarketCap** (primary) — needs API key in environment
2. **CoinGecko** (free, no key) — reliable fallback, rate-limited

### Pitfalls
- **CoinMarketCap key may be absent:** Always handle fallback gracefully.
- **CoinGecko free tier is rate-limited:** ~10-30 req/min.
- **CoinGecko IDs do not match ticker symbols:** AVAX maps to `avalanche-2`.
- **Multi-profile key drift:** Each profile may have its own script copy reading from a different config path.

### References
- [Price fetch debug script](scripts/price-fetch-debug.py)
- [CoinGecko ID mapping table](references/coingecko-id-map.md)

---

## 6. LP Range Rebalance

Edit LP monitor scripts (range changes, feature additions, config tweaks) — vault→runtime→test workflow. Covers both v3 and AAE scripts.

### Key Files
| File | Purpose |
|------|---------|
| `~/.hermes/scripts/.lfj-aae-config.json` | AAE script runtime config — **overrides Python DEFAULT_CONFIG** |
| `~/.hermes/scripts/.lfj-position-tracker.json` | v3 script position tracker (entry values, fees) |
| `~/.hermes/scripts/.lfj-range-state.json` | v3 script range state (warnings, cooldowns) |
| `~/.hermes/scripts/.lfj-milestone-tracker.json` | AAE milestone progression state |

### Range Update Workflow (Jordan-initiated)
When Jordan provides a new range (e.g., "new range is 9.25 - 9.59"):
1. Read current config: `cat ~/.hermes/scripts/.lfj-aae-config.json`
2. Fetch current price: DexScreener API for the pool pair
3. Update `position.range_low` and `position.range_high` in the JSON
4. Calculate price position in new range: `((price - low) / (high - low)) * 100` — report as % (0%=low, 100%=high)
5. Update memory (replace existing LFJ entry with new range)
6. Confirm with user: price, range, position-in-range %, and shape

### Pitfalls
- **Multiple profile config copies:** Configs exist in DMOB, Gentech, YoYo, Desmond profile directories. There are 6+ copies of `.lfj-aae-config.json`. The script reads from `~/.hermes/scripts/.lfj-aae-config.json` which resolves to the *calling profile's* home, NOT a shared path. Updating the wrong copy = silent stale data. **Always verify with `python3 -c "import os,json; print(json.load(open(os.path.expanduser('~/.hermes/scripts/.lfj-aae-config.json')))['position'])"` after editing.**
- **Runtime JSON config overrides Python DEFAULT_CONFIG:** Edit both. The `DEFAULT_CONFIG` in the script is a fallback; the JSON config file wins via `merged.update(cfg)`. But if the JSON file has the wrong values, you get wrong behavior with no error.
- **`~` resolves to profile home, not `/root/`:** Use absolute paths. Each profile has its own `~/` root.
- **Cron jobs read from their own profile:** The `cronjob` tool only lists jobs in your profile.
- **Config sync across profiles is manual:** When updating range/shape/position values, you must update ALL profile copies. Use `find /root/.hermes/profiles -name ".lfj-aae-config.json"` to find them all. Don't assume one update is enough.
- **Vision tool model errors:** `browser_vision` can fail with "Not supported model" errors. Fallback: use `tesseract <image> stdout | head -80` for OCR extraction from trading UI screenshots. Output is messy but key numbers (price, balance, fees, range) are usually recoverable. If tesseract unavailable, ask Jordan to type the values.
- **Memory replace fails on Unicode:** En-dashes (–) in memory entries may not match literal `old_text` strings due to encoding. Workaround: add a new memory entry replacing the old one's content, or accept the existing memory if it's already current (check the injected MEMORY block first — it may have been updated by another session).

### References
- [LP rebalance template](templates/lp-rebalance-template.md)
- [Config copy debug script](scripts/config-copy-debug.py)
- [Screenshot OCR fallback pattern](references/screenshot-ocr-fallback.md) -- when vision model fails, use tesseract for trading UI screenshots

---

## 7. Unified LP Monitoring with Milestone Tracking

**Pattern:** Single script consolidates LP position reading, fee efficiency calculation, milestone progression, and DCA logic. Avoid script duplication — one source of truth.

### Preferred Architecture
- **Primary script:** `lp-aae-signal-monitor.py` (hourly cadence)
- **State files:** Shared JSON for position, milestone, and regime state
- **Cron integration:** Hermes cron job with skill-based execution
- **Silence logic:** Only post when status changes or action required

### User Preferences (Jordan)

#### Milestone Thresholds
Use a simple, achievable ladder:
| Tier | Daily Fee Target | Unlocks |
|------|------------------|---------|
| Scout | $5/day | Entry strategies (CURVE) |
| Raider | $20/day | SPOT + BIDIRECTIONAL shapes |
| Warlord | $50/day | Multi-pool positions |
| Sovereign | $100/day | Custom strategy creation |
| Freedom | $200/day | Mentorship + full autonomy |

#### Alert Triggers
| Condition | Threshold | Action |
|-----------|-----------|--------|
| Fee efficiency low | <30% | Warning + rebalance recommendation |
| Out of range | Price < low OR > high | Wait 10 min to confirm, then 5 min grace, then RED alert |
| Milestone crossed | Any tier reached | celebrate + next target |
| Compound ready | Fees earned ≥ $50 | Auto-compound suggestion |

#### DCA Adaptation
Shape-aware DCA sizing:
- Center zone (efficiency >70%, CURVE): full weekly DCA
- Mid zone (50–70% efficiency): reduced DCA
- Low zone (30–50%): micro-DCA + rebalance warning
- Edge/crash (<30% or out-of-range): minimal DCA + urgent rebalance

### Consolidation Checklist
When refactoring duplicated LP monitoring scripts:
- [ ] Identify all scripts computing fee efficiency independently
- [ ] Merge position fetching (on-chain + wallet balances) to single function
- [ ] Centralize milestone comparison logic in one place
- [ ] Standardize config keys across `.lfj-aae-config.json`, `.lfj-milestone-tracker.json`
- [ ] Update ALL scripts with new milestone thresholds (5/20/50/100/200)
- [ ] Remove/disable legacy cron jobs after migration
- [ ] Test unified script standalone before scheduling

#### Common Pitfalls
- **Undefined constants:** Ensure all thresholds (e.g., `EFFICIENCY_RED_THRESHOLD`) are declared at module level.
- **State divergence:** Multiple scripts may read/write same state file concurrently → race conditions.
- **Timezone drift:** Use UTC timestamps in state files; convert to user timezone only for display.
- **Cron delivery duplication:** Old cron jobs may still fire after new one is added → duplicate alerts.
- **Source-of-truth confusion:** HTML position tracker is a rendered view; the authoritative values reside in `.lfj-aae-config.json` (position_usd, range) and `~/.hermes/scripts/.lfj-aae-state.json` (cumulative fees). Cross-check to avoid stale data errors.
- **Out-of-range earnings collapse:** If price < range_low or > range_high, estimated daily fees ≈ $0 irrespective of capital. Always check `in_range` status before calculating gap or projecting DCA timeline; treat OOR as a blocker to milestone progress.
- **DexScreener lacks APR field:** Do not attempt to read `apr` from the API response; compute it manually from `volume_24h`, `liquidity.usd`, `position_usd`, and `fee_tier_bps`. Volume can collapse suddenly, making APR volatile—validate with at least two data points before concluding.
- **State file location:** The AAE state file path is `~/.hermes/scripts/.lfj-aae-state.json` (not `.lfj-milestone-tracker.json`). It stores `last_position_usd`, `total_fees_earned_usd`, `total_days_in_range`. Ensure this file exists and is readable by the cron job.

### Analysis: Capital Position + Yield Gap + DCA Projection

When generating milestone progress reports, integrate three data sources:

**Data Source Merge Strategy**
| Source | Location | Purpose | Key Fields |
|--------|----------|---------|------------|
| Vault tracker | `~/vaults/gentech/03-Strategies/scripts/.lfj-position-tracker.json` | Historical entry + DCA injections | `entry_total_usd`, `history[].value_usd`, `history[].event` |
| Runtime state | `~/.hermes/profiles/<profile>/home/.hermes/scripts/.lfj-aae-state.json` | Live position, fees earned, days in range | `last_position_usd`, `total_fees_earned_usd`, `total_days_in_range` |
| Live pool data | DexScreener API | Current price, volume, TVL for yield calculation | `priceNative`, `volume.h24`, `liquidity.usd` |

**Capital Change Detection**
1. Read latest vault historical entry's `value_usd`
2. Compare to runtime state's `last_position_usd`
3. If runtime > vault: **DCA Boost detected** — highlight injection amount
4. If runtime < vault: **Impermanent loss or fee harvesting** — note decline reason

**Yield Calculation from Pool Metrics** (fallback when on-chain fee data unavailable)
```
daily_fees = (pool_volume_24h × fee_tier_bps/10000) × (position_usd / pool_tvl_usd)
implied_apr = (daily_fees × 365 / position_usd) × 100
```
**Note:** Volume collapse can crater yield even with unchanged principal.

**Milestone Gap Analysis**
- Shortfall = `target_daily_fees - current_daily_fees`
- Required principal at given APR: `required = shortfall × 365 / (target_apr/100)`
- Present three scenarios: current APR, historical APR, target APR

**DCA Timeline Projection**
```
weeks_needed = required_principal / weekly_dca_rate
```
Where `weekly_dca_rate = (sun_wed_amount + thu_sat_amount)`.
Present both conservative ($50/wk) and aggressive ($100/wk) scenarios.

**Pro Tips to Accelerate Timeline**
1. **Range widening** → higher fee efficiency (captures more volume)
2. **Multi-pool diversification** → higher-fee tiers on chains with better volume
3. **Active rebalance threshold** → if efficiency <30%, rebalance immediately to restore yield
4. **Align DCA cadence** → user's 2×/week preference should match script's `dca_day` and `dca_boost` configuration

### References
- [Shape recommendation engine (volatility-based)](references/shape-recommendation-engine.md)
- [Unified monitoring architecture design](references/lp-monitoring-unified-architecture.md)
- [Consolidation plan: D5 cron cleanup](references/d5-cron-consolidation-plan.md)
- [Milestone state schema](references/milestone-state-schema.md)
- [Debounce pattern: out-of-range confirmation](references/out-of-range-debounce-pattern.md)
- [Yield calculation + gap analysis](references/yield-gap-analysis.md)
- [S2S Milestone Report generation](references/s2s-milestone-schema.md)
- [DexScreener API fields for pool queries](references/dexscreener-api-fields.md)
- [LFJ vault log entry format](references/lfj-vault-log-format.md)
- [S2S Milestone Report generation](references/s2s-milestone-report-format.md)

### S2S Milestone Report Generation Pattern

When asked to "Analyze the current DeFi position and capital accumulation based on the most recent Yield Farm Tracker data," use this standard pattern.

#### Data Source Priority (most recent authoritative first)
1. **S2S Milestone Report JSON** — `03-Projects/DeFi/s2s-milestone-report.json` (comprehensive analysis with calculated gap, DCA path, pro tips)
2. **Vault Position Log** — `03-Projects/DeFi/LFJ-AVAX-USDC.md` (daily manual/automated vault entries)
3. **Runtime State** — `~/.hermes/profiles/<profile>/home/.hermes/scripts/.lfj-aae-state.json` (last seen position, price, fees)
4. **Config** — `03-Strategies/scripts/.lfj-aae-config.json` (configured position_usd, range, shape)

#### Capital Change Detection Logic
```python
# 1. Load S2S report capital_update block (if exists)
current_total = report['capital_update']['current_total']  # $135.83 May 2
last_recorded = report['capital_update']['last_recorded_total']  # $138.92 pre-boost
dca_injection = report['capital_update']['dca_injection_usd']  # $55 on Apr 26

# 2. Detect: if current_total < last_recorded_total → capital declined
#    Report as: "DCA Boost detected ($X injection on [date]) | Current: $Y vs Pre-Boost: $Z (net -$Δ)"

# 3. Also cross-check vault log (May 3 shows $134.72 position, $135.60 combined)
#    Note efficiency drop, IL impact, volume collapse as explanation
```

#### Daily Yield Calculation
Two methods depending on data availability:

**Method A — Report-estimated APR** (when S2S report provides `apr_estimate_pct`)
```python
apr = report['milestone_progress']['apr_estimate_pct']  # e.g., 51.4%
daily_rate = apr / 100 / 365
current_daily = current_position_usd * daily_rate
```
Note: This reflects *potential* yield given pool conditions at report time, not actual earned fees which vary with volume.

**Method B — Live DexScreener calculation** (fresh fetch)
```python
url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{pool_address}"
pool_volume = data['pair']['volume']['h24']
pool_tvl = data['pair']['liquidity']['usd']
fee_rate = fee_tier_bps / 10000
daily_fees = pool_volume * fee_rate * (position_usd / pool_tvl)
apr = (daily_fees * 365 / position_usd) * 100
```
Pitfall: Volume collapse → APR can drop from 50% → 6% in one day.

#### Milestone Gap Computation
```python
target_daily = milestone_targets[current_milestone]  # $20 for M2 Raider
gap_usd = (target_daily - current_daily) * 365 / (apr / 100)
principal_needed = current_position + gap_usd
```
Report format:
```
⏳ Gap: $14,069.43 principal needed at current 51.4% APR
```

#### DCA Path Projection
```python
weekly_dca_low = 50   # Sun-Wed split baseline
weekly_dca_high = 100 # maximum weekly injection
weekly_avg = 75       # midpoint used for timeline

weeks_low = gap / weekly_dca_low
weeks_avg = gap / weekly_avg
weeks_high = gap / weekly_dca_high

# Format into years/weeks for readability
years = weeks / 52
weeks_rem = weeks % 52
```
Report format:
```
🛠️ DCA Path: 187.6 weeks (3.6 years) at $75/week avg
Schedule: Sun-Wed + Thu-Sat split ($37.50 per DCA event)
```

#### Output Format (User-Specified)
Always produce exactly:
```
💰 Capital Update: [DCA Boost detected ($X injection on DATE) | Current: $Y vs Pre-Boost: $Z (net -$Δ)]  OR  [Steady]
🏁 Progress: $[current_daily_est] / $[target_daily] ([pct]% to [tier])
⏳ Gap: $[gap_amount] principal needed at current [apr]% APR
🛠️ DCA Path: [X] weeks ([Y] years) at current rate (Sun-Wed/Thu-Sat split)
💡 Pro Tips: [1] Tip title → Expected impact
              [2] Tip title → Expected impact
              [3] Tip title → Expected impact
```

#### Pro Tips Extraction
Priority order:
1. **Range efficiency** — if efficiency < 50%, suggest narrowing range to capture more volume
2. **Config sync** — if multiple monitoring scripts have diverged config values, flag config drift
3. **Compounding cadence** — suggest timing adjustments (bi-weekly vs monthly)
4. **IL warning** — if impermanent loss > 2%, recommend rebalance

#### References
- [S2S Milestone Report JSON schema](references/s2s-milestone-schema.md)\n- [Vault config integration pattern](references/vault-config-integration.md)  <-- NEW
- [Vault log format for LFJ-AVAX-USDC](references/lfj-vault-log-format.md)
- [DexScreener API response fields](references/dexscreener-api-fields.md)
- [Cross-chain allocation monitor design](references/cross-chain-allocation-monitor.md)
- [RWA token IL calculator](references/rwa-il-calculator.md)
- [Solana yield platforms reference](references/solana-yield-platforms.md)
