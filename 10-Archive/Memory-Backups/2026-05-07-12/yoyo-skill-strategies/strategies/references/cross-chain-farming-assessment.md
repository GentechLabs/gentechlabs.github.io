# Cross-Chain Farming Feasibility Assessment

## Quick-Start Decision Matrix

When considering a token for yield farming on a non-native chain, use this matrix:

| Condition | Verdict | Rationale |
|-----------|---------|-----------|
| Token has no native representation on target chain | ❌ NOT VIABLE | Bridging + wrap/unwrap adds 3–5% friction per round-trip; sub-$50M MC tokens rarely have sufficient yield to offset |
| Token has native representation but 24h volume < $1M (Solana) / < $2M (Base) | ❌ ILLIQUID | Exit slippage alone will exceed 30 days of farming fees |
| 24h volume ≥ thresholds but pool TVL < $250K | ⚠️ MARGINAL | Low depth → high IL risk + price impact on rebalance |
| TVL ≥ $500K on Solana / ≥ $1M on L2 | ✅ VIABLE | Proceed to pool-level APR + range sizing analysis |
| Bridge required with >2 hop routes | ❌ NOT WORTH | Each hop adds gas + bridge protocol risk; redemptive complexity |

## Chain-Specific Thresholds (2026 Context)

### Solana
- **Minimum viable volume**: $2M daily
- **Minimum viable pool TVL**: $500K
- **Preferred DEX**: Raydium CLMM or Orca Whirlpools
- **Gas friction**: ~$0.0002 per txn (negligible)
- **Bridge cost pattern**: Wormhole or LayerZero route typically costs $2–$5 in bridge fees + 5–10 min wait
- **Farming style**: Concentrated liquidity (tighter ranges) viable on high-volume pools only

### Base / Ethereum L2s
- **Minimum viable volume**: $5M daily
- **Minimum viable pool TVL**: $1M
- **Preferred DEX**: Uniswap V3 or Aerodrome (Base)
- **Gas friction**: $0.20–$0.80 per txn (moderate)
- **Bridge cost pattern**: Standard L2 bridge ~$3–$8 one-way; bridge back to L1 much higher ($15+)
- **Farming style**: Range orders workable; moderate gas means rebalancing costs matter

### BSC / Polygon / Arbitrum
- **Minimum viable volume**: $1M daily
- **Minimum viable pool TVL**: $250K
- **Preferred DEX**: PancakeSwap (BSC), QuickSwap (Polygon), Uniswap V3 (Arbitrum)
- **Gas friction**: $0.05–$0.30 per txn (low)
- **Bridge cost pattern**: Often direct CEX offramp cheaper than bridge; watch for withdrawal limits
- **Farming style**: x*y=k pools still common; CLMM growing

## Token Platform Verification Pattern

**Step 1: Check vault watchlist for existing chain notes**
```bash
# In 03-Strategies/cron-watchlist-config.md
grep -i "TOKEN_NAME" path/to/cron-watchlist-config.md
# Example entry:
# - PROPS — Propbase, RWA focus (CoinGecko ID: propbase)
```
The notes field often indicates chains if already known.

**Step 2: Query CoinGecko for platforms data**
```python
import requests, json

resp = requests.get(
    "https://api.coingecko.com/api/v3/coins/propbase",
    params={"localization": "false", "tickers": "false", "community_data": "false", "developer_data": "false"}
)
data = resp.json()
platforms = data.get("platforms", {})  # dict of {chain: contract_address}
print("Chains:", list(platforms.keys()))
```

**Step 3: Handle rate limits gracefully**
CoinGecko free tier: 10–30 calls/min. Use batch endpoints when possible:
```python
# Batch fetch multiple tokens
ids = "propbase,landshare,ondo"
resp = requests.get(f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}")
```
If rate-limited (HTTP 429), sleep 60 seconds and retry with exponential backoff.

**Step 4: Search for wrapped tokens if absent**
If the token doesn't appear on target chain in platforms, search:
```bash
curl -s "https://api.coingecko.com/api/v3/search?query=wrapped props solana" | jq '.coins[] | select(.id | contains("wrapped"))'
```
Common wrapped naming:
- Solana: `wrapped-<TOKEN>` or `<TOKEN>-sol`
- Base: `w<TOKEN>` or `<TOKEN>-base`
- Polygon: `<TOKEN>-poly`

If no wrapped token found after searching both "wrapped <name>" and "<name> wrapped", assume no representation.

## Cross-Chain Bridge Friction Model

For tokens present on multiple chains, calculate break-even:

```
Bridge costs:
  - Bridge-in: $2.50 (Solana → Base via Wormhole)
  - Bridge-out: $2.50 (Base → Solana return)
  - Expected slippage (entry + exit): 0.5% × 2 = 1.0% on $1000 = $10
Total one-way friction: $15 (bridge) + exit friction when leaving position

Farm yield projection (30 days):
  - Daily fees at 50% APR on $1000 LP = $1.37/day
  - 30-day gross = $41
  - Net after bridge-out (round-trip exit): $41 - $15 - exit_slippage

Break-even hold time: $15 ÷ $1.37 ≈ 11 days
Rule: Minimum hold 2× break-even → 22 days minimum to justify cross-chain move
```

**Decision rule**: If estimated 30-day net yield < $20 or break-even > 30 days, skip cross-chain.

## Real-World Case Study: PROPS & LAND (May 2026)

### PROPS (Propbase)
- **CoinGecko platforms**: Base (`0xd6aa...`), Aptos (`0xe506...::propbase_coin::PROPS`)
- **Solana representation**: None found (no wrapped version indexed)
- **24h volume**: $1.7M (thin but acceptable if native to target chain)
- **Bridge requirement**: Would need Ethereum mainnet → Base bridge (since no direct Solana route)
- **Pool availability**: Likely on BaseSwap or Aerodrome (Base), not on Solana
- **Verdict**: ❌ **NOT VIABLE for Solana farming**
  - No native Solana token
  - Cross-chain via Ethereum adds 2 bridge hops (Solana→ETH→Base) → excessive friction
  - Thin volume even on Base; LP risk high if market moves

### LAND (Landshare)
- **CoinGecko platforms**: BSC (`0xa731...`), Polygon (`0xc03e...`), Arbitrum (`0x27bc...`)
- **Solana representation**: None
- **24h volume**: $3,002 (extremely thin — exit impossible for any meaningful size)
- **Bridge requirement**: Would need bridge from Solana to any of BSC/Polygon/Arbitrum (no direct routes)
- **Pool availability**: PancakeSwap (BSC), QuickSwap (Polygon), Uniswap V3 (Arbitrum)
- **Verdict**: ❌ **NOT VIABLE period**
  - Volume so low that any LP >$100 would face >5% slippage on exit
  - Even if bridged, cannot exit position reasonably
  - Farm APR (if any) cannot compensate for permanent capital lock

### ONDO (Ondo Finance) — Positive Example
- **CoinGecko platforms**: Ethereum, Solana (native)
- **24h volume**: $28M (healthy)
- **Pool availability**: Orca/ Raydium on Solana confirmed
- **Verdict**: ✅ **VIABLE for native-chain farming**
  - Native Solana token: no bridge needed
  - Deep pools → low slippage
  - Treasury-backed RWA with transparent asset backing
  - Track via watchlist: add `ONDO` with chain field "solana"

## Red Flags That Override All Other Analysis

Even if a token passes the above checks, these conditions mean ❌ avoid:
1. **Contract upgradable with no timelock** — owner can rug tomorrow
2. **Team tokens >30% of supply** — insiders can dump on LP
3. **No audits or unaudited by reputable firm** → OpenZeppelin, Trail of Bits, Consensys, PeckShield acceptable; "audited by unknown firm" counts as unaudited
4. **TVL/volume ratio < 0.2** — means volume is engineered/fake
5. **Protocol fees > 20% of APR** — sustainability concern; emissions-driven yield will collapse
6. **Token distribution: >50% held by top 10 wallets** — centralization risk
7. **No GitHub or GitHub inactive >90 days** — dead protocol
8. **Recent contract migration without announcement** — potential silent owner change

If any red flag is present, downgrade viability by 2 tiers (e.g., ✅→⚠️, ⚠️→❌).

## Follow-Up Task Templates

### A. Cross-Chain Bridge Cost Research (Delegate to Desmond)
```
Research task: Bridge <TOKEN> from <SOURCE_CHAIN> to <TARGET_CHAIN>

Deliverables:
1. List all available bridges (Wormhole, LayerZero, Celer, Multichain, etc.)
2. Bridge fee schedule (one-way, round-trip)
3. Typical wait time (blocks, minutes)
4. Slippage model on destination DEX (Raydium/Uniswap)
5. Exit strategy feasibility (can we bridge back? any lock-up?)

Output: vault file `03-Strategies/bridge-cost-analysis-<token>-<date>.md`
```

### B. Solana RWA Alternative Scouting
```
Search criteria:
- Category: Real World Assets (RWA)
- Chain: Solana
- Market cap: >$50M (sanity filter)
- TVL/volume ratio: >0.5
- Audit status: at least one reputable audit

Deliverables:
1. Token list with CoinGecko IDs
2. Pool existence on Raydium/Orca (pool address, tick spacing, fee tier)
3. Current APR (real, not including emissions)
4. Risk flags (centralization, custody, legal)

Output: vault file `03-Strategies/solana-rwa-alternatives-<date>.md`
```

### C. Cross-Chain Farming Model (YoYo)
```
Build spreadsheet model:
Inputs:
- Bridge cost (in + out)
- Pool APR (base + rewards)
- Capital amount
- Hold period (days)
- Expected price volatility (historical 30d std dev)
- IL estimate (based on correlation to USDC/SOL)

Outputs:
- Net yield after all friction
- Break-even hold period
- IL-adjusted return
- Risk score (0–10)

Decision rule: Only proceed if (net yield > 15% AND break-even < 60d AND risk < 6/10)
```

## API Rate-Limit Handling Pattern

CoinGecko free tier is aggressive (10–30 calls/min). Use this wrapper:

```python
import time, requests
from functools import wraps

def rate_limited(max_per_second=1):
    """Decorator to limit function calls per second."""
    min_interval = 1.0 / max_per_second
    def decorate(func):
        last_time_called = 0.0
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_time_called
            elapsed = time.time() - last_time_called
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            result = func(*args, **kwargs)
            last_time_called = time.time()
            return result
        return wrapper
    return decorate

@rate_limited(max_per_second=0.5)  # 1 call per 2 seconds → safe for free tier
def fetch_coingecko_coin(coin_id: str):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    resp = requests.get(url, params={"localization": "false", "tickers": "false"})
    if resp.status_code == 429:
        time.sleep(65)  # full minute wait on rate limit
        return fetch_coingecko_coin(coin_id)  # retry once
    resp.raise_for_status()
    return resp.json()
```

**Batch when possible**: Use `/coins/markets` with multiple IDs to fetch price + volume in one call.

## ⚠️ API Reliability from Hermes (Critical Pitfall)

**Bot detection blocks most web sources from the Hermes agent environment.** This session (May 2026) confirmed:

| Source | Result | Failure Mode |
|--------|--------|-------------|
| DeFiLlama API (`api.llama.fi/protocols`) | ✅ **Works** | No auth needed, reliable |
| CoinGecko API (`api.coingecko.com/api/v3`) | ⚠️ **Timeouts** | Frequently times out with `--max-time 10-15`. Use only as fallback |
| DeFiLlama website | ❌ Blocked | Cloudflare challenge |
| CoinGecko website | ❌ Blocked | Cloudflare challenge |
| Google Search | ❌ Blocked | CAPTCHA |
| DuckDuckGo | ❌ Blocked | Bot detection + duck CAPTCHA |
| X/Twitter articles | ❌ Blocked | Login wall |

**Rule**: For ecosystem-wide protocol scanning, use DeFiLlama API directly via `curl | python3`. Do NOT attempt browser-based research — it will waste minutes on CAPTCHAs that never resolve.

**When you need token-specific data** (e.g., platforms/chain presence for a single token), DeFiLlama `/protocol/{slug}` endpoint works. CoinGecko is only needed for token market data not available on DeFiLlama.

## For Broader Ecosystem Mapping

If the task is "what [category] projects exist on [chain]?" rather than "can I farm token X on chain Y?", see `references/chain-ecosystem-scan.md` for the full methodology. The cross-chain farming assessment is for evaluating specific tokens; the ecosystem scan is for mapping entire protocol landscapes.

---

## Vault Entry Template: Cross-Chain Farming Assessment

Use when documenting assessment for a specific token:

```markdown
---
title: Cross-Chain Farming Assessment — <TOKEN>
date: <YYYY-MM-DD>
status: 🟢 Complete / 🟡 In Review / 🔴 Blocked
owner: YoYo
priority: P2
tags: #cross-chain #rwa #farming-assessment
---

## Token Overview
- **Name**: <Protocol Name>
- **Ticker**: <SYMBOL>
- **CoinGecko ID**: <id>
- **Market Cap**: $<X>
- **24h Volume**: $<Y>

## Native Chain Presence
| Chain | Contract Address | Native? |
|-------|-----------------|---------|
| Ethereum | ... | ✅ Primary |
| Solana | ... | ❌ Not listed |
| Base | ... | ✅ via bridge |

## Target Chain Analysis (Solana)
- **Native representation**: ❌ No (wrapped version: not found)
- **Pool on Raydium/Orca**: N/A
- **24h volume on Solana**: N/A
- **Estimated bridge cost**: N/A

## Liquidity Depth Assessment
- **Volume/market cap ratio**: <ratio> → <interpretation>
- **Pool TVL (if native)**: $<value>
- **Depth classification**: [Deep / Moderate / Thin / Illiquid]

## Bridge Friction Calculation (if applicable)
| Cost Item | Amount | Notes |
|-----------|--------|-------|
| Bridge-in fee | $X.XX | via <bridge name> |
| Bridge-out fee | $X.XX | return route |
| Expected entry slippage | X% | on $<capital> |
| Expected exit slippage | X% | on 30-day harvest |
| **Total friction** | **$X.XX** | one-way / round-trip |

## Break-Even Modeling (30-day horizon)
```
Gross yield (@ <APR>% on $<capital>):
  Daily: $<daily_fees>
  30-day total: $<total>

Net yield after bridge-out friction:
  $<total> - $<friction_total> = $<net>

Break-even hold period: <days> days
Verdict: <PROCEED / AVOID / MONITOR>
```

## Risk Flags
- 🚨 <red flag description>
- ⚠️ <concerning pattern>
- 📢 <upgrade risk>

## Final Recommendation
**<VIABILITY STATUS>**: <one-sentence rationale>

**Next action**: <specific next step>

---
Related: <link to related vault files or ongoing work>
```

---

*This reference supplements the `strategies` skill's Cross-Chain Farming Feasibility Assessment pattern. For protocol-level due diligence beyond chain/liq checks, see `protocol-due-diligence-framework.md`.*
