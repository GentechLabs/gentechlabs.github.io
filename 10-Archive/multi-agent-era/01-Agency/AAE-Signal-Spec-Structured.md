# AAE Signal Spec — Structured Fields (Dashboard → Product)
**Date:** 2026-04-25
**Source:** Jordan confirmed all dashboard elements from LFJ/Trader Joe yield farm tracker
**Status:** Ready for implementation

---

## 1. POSITION SIGNALS (Identity & State)

| Field | Type | Source | Alert Trigger |
|-------|------|--------|---------------|
| `pool_address` | Address (EVM/Solana) | User input / Contract registry | — |
| `token_pair` | Tuple[TokenA, TokenB] | Pool metadata | — |
| `chain_id` | String | Pool metadata | — |
| `position_id` | String/NFT ID | LP position NFT | — |
| `position_value_usd` | Float | On-chain balances × oracle price | — |
| `token_split` | Dict{token: pct} | On-chain reserves | Rebalance suggestion if >80% single-sided |
| `entry_price` | Float | Position creation snapshot | — |
| `current_price` | Float | Oracle / DEX pool | Out-of-range alert |
| `price_delta_pct` | Float | (current - entry) / entry | > ±10% → volatility note |

---

## 2. RANGE & STRATEGY SIGNALS (Health)

| Field | Type | Source | Alert Trigger |
|-------|------|--------|---------------|
| `range_min` | Float | Position config | — |
| `range_max` | Float | Position config | — |
| `range_width_pct` | Float | (max - min) / mid | — |
| `active_bin` | Float | Current pool price | — |
| `in_range` | Boolean | current_price ∈ [min, max] | FALSE → 🚨 URGENT |
| `range_efficiency_pct` | Float | Volume captured / total volume | < 50% → rebalance suggestion |
| `strategy_shape` | Enum[CURVE, SPOT, BIDIRECTIONAL, CUSTOM] | User selection | — |
| `bin_count` | Int | Position config | — |
| `fee_tier_bps` | Int | Pool config | — |

---

## 3. YIELD & FEE SIGNALS (Revenue)

| Field | Type | Source | Alert Trigger |
|-------|------|--------|---------------|
| `fees_24h_usd` | Float | Pool volume × position_share × fee_tier | — |
| `fees_since_deposit_usd` | Float | Cumulative from position creation | — |
| `fee_efficiency_pct` | Float | fees_24h / position_value × 365 | < 75% + in_range → ⚠️ consider rebalancing |
| `rewards_apr_pct` | Float | Emission rate × price / TVL | Extreme changes (> ±50% day-over-day) |
| `claimable_rewards_usd` | Float | Reward contract balance | > threshold → compound suggestion |
| `claimable_rewards_breakdown` | Dict{token: amount} | Reward contract | — |
| `gas_cost_estimate_usd` | Float | Gas oracle × tx complexity | > claimable_rewards_usd → warn |

---

## 4. MILESTONE SIGNALS (Progression)

| Field | Type | Source | Alert Trigger |
|-------|------|--------|---------------|
| `current_daily_yield_usd` | Float | fees_24h + rewards_24h | — |
| `milestone_index` | Int | floor(yield / milestone_step) | Increments → rank up celebration |
| `next_milestone_usd` | Float | milestones[milestone_index + 1] | — |
| `progress_to_next_pct` | Float | current / next | — |
| `milestones_hit` | List[Float] | Historical crossings | New entry → notification + shareable card |
| `days_in_range` | Int | Counter since last out-of-range | — |
| `total_days_deployed` | Int | Position age | — |

**Milestone Ladder (Jordan's Path → AAE Ranks):**
| Level | Daily Yield | AAE Rank |
|-------|-------------|----------|
| 1 | $3/day | Scout |
| 2 | $5/day | Scout+ |
| 3 | $8/day | Raider |
| 4 | $10/day | Raider+ |
| 5 | $15/day | Warlord |
| 6 | $20/day | Warlord+ |
| 7 | $55/day | Sovereign |
| 8 | $200/day | Freedom |

---

## 5. DCA & CAPITAL FLOW SIGNALS (Input)

| Field | Type | Source | Alert Trigger |
|-------|------|--------|---------------|
| `dca_schedule` | Enum[WEEKLY, MONTHLY, YEARLY, CUSTOM] | User config | — |
| `dca_amount_usd` | Float | User config | — |
| `dca_funding_source` | String | User note | — |
| `last_deposit_at` | ISO timestamp | On-chain event | > 7 days since schedule → missed DCA alert |
| `capital_added_since_last_report` | Boolean | Deposit event detection | TRUE → report capital addition |
| `wallet_ready_balance` | Dict{token: amount} | Wallet balances | Sufficient for next DCA? |

---

## 6. POOL HEALTH SIGNALS (Context)

| Field | Type | Source | Alert Trigger |
|-------|------|--------|---------------|
| `pool_tvl_usd` | Float | DEX API / on-chain | Major TVL drops (> -30%) |
| `pool_volume_24h_usd` | Float | DEX API | — |
| `pool_apr_pct` | Float | DEX API | — |
| `pool_dominant_pair` | Boolean | Is this the highest-liquidity pair? | FALSE → suggest better pair |
| `tvl_trend_7d` | Float | TVL change over 7 days | Negative → pool decay warning |

---

## 7. ALERT MATRIX (Silent vs Loud)

| Condition | Severity | Message |
|-----------|----------|---------|
| In range + efficiency ≥ 75% + no capital added + no milestone | 🤐 SILENT | — |
| In range + efficiency < 75% | ⚠️ LOW | "Consider rebalancing — efficiency at {pct}%" |
| Out of range | 🚨 HIGH | "OUT OF RANGE — Price {current} vs range [{min}, {max}]" |
| Milestone crossed | 🎉 CELEBRATE | "Promoted to {rank}! New strategies unlocked." |
| Capital added | 📥 INFO | "Capital added: ${amount} — position updated." |
| Missed DCA (>{schedule}) | ⏰ REMINDER | "DCA due — {source} ready?" |
| Gas > claimable rewards | ⚠️ LOW | "Gas (${gas}) exceeds claimable (${rewards}) — wait to compound." |
| Pool TVL drop > 30% | 🚨 HIGH | "Pool TVL collapsing — consider exit." |

---

## 8. API / CONTRACT INTEGRATION MAP

| Signal Group | Primary Source | Fallback | On-Chain Fallback |
|--------------|---------------|----------|-------------------|
| Price, TVL, Volume | DexScreener API | CoinGecko | Direct RPC call |
| Position balances | LP NFT contract | Subgraph | RPC `balanceOf` |
| Fees accrued | Pool contract (getSwapOut/getReserves) | Subgraph | Manual calculation |
| Rewards | Rewarder contract | Subgraph | — |
| Gas estimates | Gas oracle (e.g., Etherscan) | Hardcoded buffer | — |

---

## 9. AAE PRODUCT MAPPING

| Signal Field | AAE Feature |
|--------------|-------------|
| position_value_usd + token_split | **Squad Treasury** — shared capital view |
| fees_24h + fees_since_deposit | **Revenue Stream** — squad income dashboard |
| rewards_apr + claimable_rewards | **Incentives Engine** — auto-compound triggers |
| in_range + range_efficiency | **Health Monitor** — range status + alerts |
| milestone_index + progress_to_next | **Rank System** — progression + unlocks |
| dca_schedule + capital_added | **Capital Flow** — DCA tracking + reminders |
| pool_tvl + volume + trend | **Pool Intelligence** — strategy recommendations |
| strategy_shape + bin_count | **Strategy Selector** — risk-labeled presets |

---

## Next Steps
1. **DMOB** — Scaffold contract structs for Signal schema (Position, Range, Yield, Milestone)
2. **YoYo** — Optimize cron to fetch all structured fields; update alert logic to use new matrix
3. **Desmond** — UX copy for each alert severity + rank-up celebrations
4. **Gentech** — Sync this spec to Green Room for cross-agent handoff

**Tags:** #aae #signal-spec #lp-tracking #milestone #dashboard #product
