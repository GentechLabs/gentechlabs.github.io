# DCA Preset System — Design Brief

**Date:** 2026-05-28
**Status:** Idea / Architecture
**Author:** Gentech + Jordan

## Vision

A configurable DCA (Dollar-Cost Averaging) system for DeFi LP positions that lets users:
1. Choose from strategy presets OR create custom strategies
2. Set custom buy frequencies (specific days, weekly, bi-weekly)
3. Define price-based trigger zones (200W, 50W, custom levels)
4. Execute autonomously through the agent stack with guard rails

## Core Concept: Strategy Presets

### Preset 1: "Conservative Ladder"
```
Trigger: Price drops 5% from last buy
Amount: 25% of total capital per deployment
Max per week: $50
Floor: Hard stop at $7.80 (configurable)
Resume: When price stabilizes 3 days above floor
```

### Preset 2: "Aggressive Accumulation"
```
Trigger: Price touches 200-week MA or below
Amount: 50-100% of available capital
Max per week: $150
Entry condition: Price below 200W MA
Exit condition: Price crosses above 50W MA
```

### Preset 3: "Mixed Frequency"
```
Trigger: Custom day schedule (e.g., every Tuesday + Friday)
Amount: Fixed $25 per trigger day
Max per week: $50
Price guard: Only deploy if price > $8.00
```

### Preset 4: "Paycheck DCA"
```
Trigger: Every other Friday (payday)
Amount: 10% of paycheck
Allocation: 70% LP, 30% stablecoin reserve
Auto-compound: Yes, threshold $10
```

### Preset 5: "Emergency Bottom Fish"
```
Trigger: Price drops >15% in 24h
Amount: Deploy entire stablecoin reserve
Condition: Must be below $8.50
Post-deploy: Switch to "Conservative Ladder" preset
```

## Config Schema (v2)

```json
{
  "dca_preset_system": {
    "version": "2.0",
    "active_preset": "conservative_ladder",
    "presets": {
      "conservative_ladder": {
        "name": "Conservative Ladder",
        "description": "Gradual entry on dips, avoid catching knives",
        "trigger": {
          "type": "price_drop",
          "percent_drop": 5,
          "cooldown_days": 3
        },
        "amount": {
          "type": "percentage",
          "value": 25,
          "max_usd": 50,
          "max_per_week": 100
        },
        "guards": {
          "floor_price": 7.80,
          "max_weekly_deploy": 100,
          "pause_if_drop_pct": 15,
          "pause_duration_days": 7
        },
        "schedule": {
          "type": "trigger_based",
          "check_interval_hours": 4
        },
        "post_deploy": {
          "compound": true,
          "compound_threshold": 50,
          "rebalance_if_oor": true
        }
      },
      "aggressive_accumulation": {
        "name": "Aggressive Accumulation",
        "description": "Heavy buying at 200W MA, exit at 50W MA",
        "trigger": {
          "type": "ma_cross",
          "buy_below": "200w",
          "sell_above": "50w"
        },
        "amount": {
          "type": "percentage",
          "value": 75,
          "max_usd": 150,
          "max_per_week": 300
        },
        "guards": {
          "floor_price": 6.00,
          "max_weekly_deploy": 300,
          "pause_if_drop_pct": 20,
          "pause_duration_days": 14
        },
        "schedule": {
          "type": "continuous",
          "check_interval_hours": 6
        }
      },
      "mixed_frequency": {
        "name": "Mixed Frequency",
        "description": "Fixed amount on specific days",
        "trigger": {
          "type": "schedule",
          "days": ["tuesday", "friday"]
        },
        "amount": {
          "type": "fixed",
          "value": 25,
          "max_per_week": 50
        },
        "guards": {
          "floor_price": 8.00,
          "max_weekly_deploy": 50,
          "pause_if_drop_pct": 10,
          "pause_duration_days": 5
        },
        "schedule": {
          "type": "cron",
          "cron": "0 12 * * 2,5"
        }
      },
      "paycheck_dca": {
        "name": "Paycheck DCA",
        "description": "Bi-weekly deploy on payday",
        "trigger": {
          "type": "schedule",
          "frequency": "biweekly",
          "day": "friday"
        },
        "amount": {
          "type": "paycheck_pct",
          "value": 10,
          "allocation": {
            "lp": 70,
            "stablecoin_reserve": 30
          }
        },
        "guards": {
          "floor_price": 7.50,
          "max_per_deploy": 200,
          "pause_if_drop_pct": 12,
          "pause_duration_days": 7
        },
        "schedule": {
          "type": "cron",
          "cron": "0 18 */14 * 5"
        }
      },
      "emergency_bottom_fish": {
        "name": "Emergency Bottom Fish",
        "description": "Deploy reserve on major crashes",
        "trigger": {
          "type": "price_crash",
          "drop_pct": 15,
          "timeframe_hours": 24
        },
        "amount": {
          "type": "reserve_full",
          "target_preset": "conservative_ladder"
        },
        "guards": {
          "floor_price": 8.50,
          "max_single_deploy": 500,
          "cooldown_days": 30
        },
        "schedule": {
          "type": "continuous",
          "check_interval_hours": 1
        }
      }
    },
    "global_settings": {
      "default_token": "AVAX",
      "default_pool": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
      "chain": "avalanche",
      "auto_compound": true,
      "compound_threshold": 50,
      "alert_on_deploy": true,
      "alert_channel": "telegram:-1002916759037",
      "require_approval_above": 200,
      "execution_mode": "autonomous",
      "fallback_to_stablecoin": true
    }
  }
}
```

## Guard Rail Architecture

### Financial Guards
1. **Max weekly deploy** — hard cap, cannot be overridden
2. **Floor price** — pause all deployment below this level
3. **Max single deploy** — prevents over-commitment
4. **Paycheck percentage** — never deploy more than X% of income
5. **Stablecoin reserve** — always maintain minimum reserve

### Technical Guards
1. **Cooldown period** — minimum time between deployments
2. **Price crash detection** — auto-pause on >15% drops
3. **Liquidity check** — verify pool has sufficient liquidity before deploy
4. **Gas price check** — pause if gas > threshold (Avalanche-specific)
5. **RPC health check** — fallback to secondary RPC if primary fails

### Execution Guards
1. **Approval threshold** — manual approval for deploys > $200
2. **Daily deploy limit** — max 1 deploy per 24 hours (configurable)
3. **Weekly deploy limit** — max N deploys per week
4. **Emergency stop** — kill switch for all autonomous execution
5. **Audit trail** — every deploy logged to vault

## Integration Points

### Agent Stack Integration
```
┌─────────────────────────────────────────────────────┐
│  Jordan's Input Layer                                │
│  - Telegram commands: /dca preset conservative      │
│  - Screenshot uploads → auto-detect position         │
│  - Voice commands → parse intent                     │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  DCA Orchestrator (YoYo on Maltaqa)                  │
│  - Reads preset config                               │
│  - Checks guard rails                                │
│  - Triggers deployment                               │
│  - Logs to vault                                     │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Execution Layer                                     │
│  - Arsenal API (LFJ integration pending)             │
│  - Direct RPC calls (fallback)                       │
│  - Transaction builder + signer                      │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│  Monitoring Layer                                    │
│  - Position reader (on-chain)                        │
│  - Price oracle (CMC/Pyth)                           │
│  - IL calculator                                     │
│  - Fee tracker                                       │
└─────────────────────────────────────────────────────┘
```

### YoYo's Role (Maltaqa)
- **Execution engine**: Runs the DCA logic on schedule
- **Guard rail enforcer**: Checks all conditions before deploy
- **State manager**: Tracks deploy history, cooldowns, reserves
- **Alert sender**: Notifies Jordan of deploys, pauses, errors

### Maltaqa's Role
- **Isolated execution environment**: No interference from other agents
- **Persistent state**: Maintains deploy history across sessions
- **API key management**: Secure storage for CMC, RPC, wallet keys
- **Resource limits**: Prevents runaway execution

## Missing Pieces (To Build)

### 1. LFJ/Trader Joe DEX Integration
- **Status**: Arsenal API doesn't have LFJ support yet
- **Options**:
  - Direct RPC calls to LFJ pool contracts (we have selectors)
  - Build custom LFJ SDK wrapper
  - Wait for Arsenal to add LFJ
- **Priority**: HIGH — this is the execution bottleneck

### 2. Automated Token Acquisition
- **Challenge**: Need to buy AVAX or USDC before LP deployment
- **Options**:
  - CEX API (Binance, Bybit) for fiat → stablecoin
  - On-chain swap (AVAX → USDC via LFJ/Trader Joe)
  - Hybrid: CEX for fiat on-ramp, DEX for token swaps
- **Priority**: HIGH — can't deploy without tokens

### 3. Wallet Signing
- **Challenge**: Autonomous execution needs wallet access
- **Options**:
  - Hot wallet with limited funds (Jordan controls funding)
  - MPC wallet (threshold signatures)
  - Hardware wallet integration (Ledger/Trezor)
- **Priority**: CRITICAL — security gate

### 4. Price MA Oracle
- **Challenge**: 200W and 50W MAs need historical data
- **Options**:
  - CoinMarketCap historical API
  - On-chain calculation from price history
  - Third-party MA indicator (TradingView API)
- **Priority**: MEDIUM — can use price thresholds as proxy

### 5. Paycheck Detection
- **Challenge**: "Bi-weekly on Friday" needs calendar logic
- **Options**:
  - Manual trigger via Telegram command
  - Calendar integration (Google Calendar)
  - Fixed schedule (every 14 days from start date)
- **Priority**: LOW — manual trigger is fine for v1

## Development Roadmap

### Phase 1: Config System (Week 1)
- [ ] Build preset config schema
- [ ] Create preset manager (load/save/switch)
- [ ] Add guard rail logic
- [ ] Test with mock deployments

### Phase 2: Execution Layer (Week 2-3)
- [ ] Research LFJ direct RPC deployment
- [ ] Build transaction builder
- [ ] Test on Avalanche Fuji testnet
- [ ] Add wallet signing (start with manual)

### Phase 3: Automation (Week 3-4)
- [ ] Build YoYo cron job for DCA execution
- [ ] Add price monitoring triggers
- [ ] Implement cooldown logic
- [ ] Add alert system

### Phase 4: Integration (Week 4+)
- [ ] Connect to Maltaqa environment
- [ ] Add Telegram commands (/dca list, /dca switch, /dca pause)
- [ ] Build audit trail logging
- [ ] Add manual approval flow

## Success Metrics

1. **Deployment success rate**: >95% of triggered deploys complete
2. **Guard rail effectiveness**: 0% of deploys violate guard rails
3. **Alert accuracy**: >90% of alerts are actionable (not noise)
4. **User satisfaction**: Jordan can configure presets in <5 minutes
5. **Autonomous operation**: 7+ days without manual intervention

## Open Questions

1. **Approval flow**: Should all deploys require manual approval, or only above a threshold?
2. **Multi-chain support**: Should this work on Base/Solana too, or Avalanche-only for v1?
3. **Token acquisition**: Do we need CEX integration, or can we start with on-chain swaps only?
4. **Reserve management**: Should the system auto-replenish stablecoin reserves from LP yields?
5. **Tax reporting**: Should we track cost basis for each deploy? (Probably yes)

---

**Next step:** Jordan reviews this design, approves v1 scope, and we start Phase 1 (config system) this week.
