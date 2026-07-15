# Dry Powder Mode — AAE Stop-Loss Agent

**Date:** 2026-07-14
**Status:** 🟡 Draft — Initial build in night session
**Priority:** HIGH — Protects capital during Jordan's 12hr Amazon shifts
**Source:** Jordan voice message, 2026-06-19 — Iran peace talks collapsed → AVAX dumped $6.11→$5.72 while Jordan was at work

## Problem

Jordan works 12-hour Amazon shifts. He can't watch markets. During that window:
- A crash can destroy LP positions (impermanent loss + price decay)
- Rebalancing opportunities are missed
- Capital that should be in stables bleeds in volatile pairs

## Solution

**Dry Powder Mode** — An agent that monitors market conditions and automatically:
1. **Detects crashes** via price action, funding rates, and volatility
2. **Withdraws liquidity** from LFJ pools when thresholds are breached
3. **Converts to stables** (USDC) to preserve capital
4. **Identifies recovery** signals (RSI, volume cooldown, news)
5. **Auto-redeploys** when conditions normalize
6. **Notifies** Jordan on every action

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Market Feeds                    │
│  CMC API · DexScreener · BlockRun Price · News  │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│           Crash Detection Engine                 │
│  • Price action thresholds                      │
│  • Volatility tracking (ATR-based)              │
│  • Funding rate monitor                         │
│  • News sentiment trigger                       │
│  → Outputs: Signal (SAFE / WATCH / CRASH)      │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│             Decision Engine                      │
│  Mode: ADVISORY (suggest → Jordan OK)           │
│  Mode: AUTO (execute at threshold)              │
│  • What to withdraw?                            │
│  • How much to stable?                          │
│  • When to re-enter?                            │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              Action Layer                        │
│  • Withdraw from LFJ pools                      │
│  • Swap to USDC via DEX                         │
│  • Redeploy to LP                               │
│  • Notifications (Telegram)                     │
└─────────────────────────────────────────────────┘
```

## Tech Stack

- **Language:** Python (reuses defi-master-cron.py patterns)
- **Data sources:** CMC API, DexScreener (via BlockRun), BlockRun Price
- **LP operations:** LFJ V2.2 (AVAX/USDC pool)
- **Storage:** JSON state file at `/root/.hermes/state/dry-powder-state.json`
- **Config:** JSON config at `03-Strategies/config/dry-powder-config.json`

## Crash Detection Signals

| Signal | Source | Threshold | Weight |
|--------|--------|-----------|--------|
| Price drop (5min) | DexScreener | ≤-3% in 5min | 30 |
| Price drop (1h) | DexScreener | ≤-8% in 1h | 25 |
| Volatility spike | ATR | ≥2× normal | 20 |
| Funding rate | DEX | < -0.01% | 15 |
| News sentiment | RSS/News | Negative | 10 |

**Output:** Weighted score 0-100
- 0-20: SAFE — normal operation
- 21-50: WATCH — increase monitoring frequency, send advisory
- 51-100: CRASH — trigger dry powder action (mode-dependent)

## Recovery Signals

| Signal | Threshold | Weight |
|--------|-----------|--------|
| RSI crosses above | 30→35 (after crash) | 35 |
| Price stabilizes | <2% range in 1h | 25 |
| Volume normalizes | <1.5× baseline | 20 |
| News turns neutral | No negative in 2h | 20 |

**Output:** Weighted score 0-100
- 0-30: STILL_CRASHED — hold in stables
- 31-60: RECOVERING — watch, prepare to redeploy
- 61-100: SAFE_TO_REDEPLOY — begin re-entry

## Modes

### Advisory Mode (default)
- Engine runs, detects signals, sends Telegram recommendation
- Jordan approves or rejects via Telegram
- No automatic capital movement

### Auto Mode
- Engine runs, detects CRASH threshold → auto-withdraws + converts
- Recovery detected → auto-redeploys
- Jordan is notified after every action

## Config File Structure

```json
{
  "mode": "advisory",
  "crash_threshold": 50,
  "recovery_threshold": 60,
  "min_withdraw_usd": 50,
  "max_withdraw_pct": 100,
  "stable_target": "USDC",
  "pool_address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
  "chain": "avalanche",
  "notification_channel": "telegram_hq",
  "poll_interval_seconds": 300,
  "watch_poll_interval_seconds": 60
}
```

## State File Structure

```json
{
  "version": 1,
  "mode": "advisory",
  "status": "monitoring",
  "last_signal": "SAFE",
  "last_signal_score": 12,
  "last_checked": "2026-07-14T...",
  "triggers_today": 0,
  "total_withdrawn_usd": 0,
  "total_redeployed_usd": 0,
  "position_before_crash": null,
  "current_stable_holdings": 0
}
```

## Files

| File | Purpose |
|------|---------|
| `03-Strategies/scripts/dry-powder-engine.py` | Main crash detection + decision engine |
| `03-Strategies/config/dry-powder-config.json` | Configuration |
| `/root/.hermes/state/dry-powder-state.json` | Runtime state (auto-created) |
| `09-Green Room/designs/dry-powder-mode.md` | This design doc |

## Remaining Work

- [x] Phase 1: Crash detection engine (Done — night session Jul 14)
- [x] Phase 1a: Test suite (18 tests — night session Jul 15)
- [ ] Phase 2: LP withdrawal integration
- [ ] Phase 3: Swap to stables
- [ ] Phase 4: Recovery detection
- [ ] Phase 5: Auto-redeploy
- [ ] Phase 6: Telegram notifications
- [ ] Phase 7: Advisory mode wiring
- [ ] Phase 8: Auto mode wiring
- [ ] Phase 9: Production testing
- [ ] Phase 10: Add to Agent Kit plugin

## Security Notes

- **Advisory mode first** — auto mode only after Jordan explicit approval
- **Config has max withdrawal cap** — prevents total liquidation on false positive
- **State is disk-backed** — survives restart, atomic writes
- **Circuit breaker** — 5 crash triggers in 24h → auto-disable (prevents oscillation)
