# AAE Premium — Safety Features & Best Practices

**Owner:** Dmob (Labs) + YoYo (Strategies)
**Status:** Draft — Ready for Implementation Planning
**Date:** Apr 19, 2026

---

## Architecture: Enforcement as Access Control

Think of enforcement like Solidity modifiers:

```
🧠 Brain (intelligence)     → Which model decides
🎭 Personality (style)       → Aggressive vs conservative demeanor  
📋 Strategy (playbook)       → What actions to take
🛡️ Enforcement (guardrails)  → What actions are ALLOWED
```

The enforcement layer is your **access control + validation**. It intercepts every proposed action and runs it through the rule set before execution.

---

## Tier 1: Basic Safety (All Users)

### 1.1 Stop Loss Mechanisms

| Type | Trigger | Action | Configurable? |
|------|---------|--------|---------------|
| **Price Stop** | Token price drops X% below entry | Exit LP position | ✅ User sets % |
| **IL Stop** | Impermanent loss exceeds X% | Exit + convert to single asset | ✅ User sets % |
| **Time Stop** | Position open for X days without profit | Review + suggest exit | ✅ User sets days |
| **Portfolio Stop** | Total portfolio drops X% | Pause all trading, alert user | ✅ User sets % |

**Implementation notes:**
- Price stops use oracle data (Chainlink) + DEX price — require both to agree within 2% to avoid oracle manipulation
- IL calculated from entry ratio vs current ratio using standard IL formula
- Time stop is advisory — prompts user for decision, doesn't auto-exit

### 1.2 Position Sizing

| Rule | Default | User Range |
|------|---------|------------|
| Max single position (% of portfolio) | 20% | 5-50% |
| Max correlated positions | 2 | 1-5 |
| Min position size | 1% | 0.1-5% |
| Max positions per pool type | 3 | 1-10 |

### 1.3 Slippage Protection

- Max slippage: 0.5% (beginner), 1% (experienced), 3% (pro)
- Transaction simulation before execution
- Reject if expected output < simulated output - slippage tolerance

### 1.4 Token Whitelist/Blacklist

- Default whitelist: Top 200 by MC + liquidity > $1M
- Default blacklist: Known scams, unaudited contracts, honeypots
- User can add/remove from both lists
- Agent blocks any action on blacklisted tokens

---

## Tier 2: Advanced Safety (Premium+)

### 2.1 Dynamic/Volatility-Adjusted Stops

- Stop loss widens during high volatility (prevents wick-outs)
- Uses ATR (Average True Range) to calculate dynamic stops
- Formula: `stop_distance = base_stop + (ATR_14 × multiplier)`
- Example: 5% base + (3% ATR × 1.5) = 9.5% dynamic stop

### 2.2 Correlation-Based Circuit Breakers

- If BTC drops >5% in 1h → pause all altcoin LP positions
- If DXY (dollar index) spikes >2% → reduce exposure by 50%
- If stablecoin depeg detected → exit all stablecoin pairs immediately
- If funding rates extreme (>0.1%/8h) → reduce leverage exposure

### 2.3 Liquidity Depth Monitoring

- Monitor pool depth at 2% price impact level
- If depth drops >30% in 24h → alert + suggest exit
- If pool becomes illiquid (depth < $100K) → mandatory exit for beginner tier
- Track LP token holder count — declining = red flag

### 2.4 Smart Contract Risk Scoring

| Check | Weight | Source |
|-------|--------|--------|
| Audit status (yes/no, auditor reputation) | 30% | CertiK, Trail of Bits, OpenZeppelin |
| Timelock on admin functions | 20% | Contract analysis |
| Multisig on treasury/owner | 15% | Etherscan/Snowtrace |
| Contract age (>6 months = safer) | 10% | Block explorer |
| Open source verified | 10% | Block explorer |
| Bug bounty active | 10% | Immunefi, HackerOne |
| No critical findings in last 90 days | 5% | Audit reports |

**Risk tiers:**
- Green (80+): Auto-approve
- Yellow (50-79): Advisory — requires user confirmation
- Red (<50): Block + alert

### 2.5 MEV Protection

- Route through private RPC (Flashbots, etc.) for transactions > $10K
- Simulate transaction before broadcast
- Reject if sandwich attack probability > threshold
- Use limit orders instead of market orders for large positions

### 2.6 Multi-Sig / Time-Delayed Execution

- For moves > X% of portfolio: require time delay (1-24h configurable)
- User receives alert with proposed action + can veto
- Emergency override: user can instantly cancel any pending action
- Audit log of all actions, proposed and executed

---

## Tier 3: Portfolio-Level Safety

### 3.1 Drawdown Management

| Metric | Beginner | Experienced | Pro |
|--------|----------|-------------|-----|
| Max daily loss | 3% | 5% | 10% |
| Max weekly loss | 7% | 12% | 20% |
| Max drawdown (peak-to-trough) | 15% | 25% | 40% |
| Recovery mode threshold | 10% DD | 20% DD | 30% DD |

**Recovery mode:** When drawdown threshold hit → switch to conservative strategy, reduce position sizes by 50%, require manual approval for all new positions.

### 3.2 Diversification Rules

- Max exposure to single asset class: 40%
- Max exposure to single chain: 60%
- Min number of uncorrelated positions: 3
- Stablecoin floor: 10% of portfolio always in stables

### 3.3 Stress Testing

- Weekly portfolio stress test against historical scenarios:
  - BTC -30% in 48h (March 2020 style)
  - Stablecoin depeg (UST scenario)
  - Major exchange hack/FTX collapse
  - Protocol exploit ($100M+)
- Report shows projected loss and which positions would be hit first
- If projected loss > user's max drawdown → suggest rebalancing

---

## Implementation Priority

| Phase | Features | Timeline |
|-------|----------|----------|
| Phase 1 (MVP) | Basic stops, position sizing, slippage, whitelist | Week 1-2 |
| Phase 2 | Dynamic stops, correlation breakers, contract scoring | Week 3-4 |
| Phase 3 | MEV protection, time-delayed execution, stress testing | Week 5-6 |
| Phase 4 | Portfolio-level diversification, recovery mode | Week 7-8 |

---

## Edge Cases & Gotchas

1. **Flash crashes:** Price drops 30% and recovers in 5 minutes. Static stops get wrecked. → Use dynamic stops + require price to stay below threshold for X blocks.
2. **Oracle manipulation:** Attacker manipulates oracle to trigger stops. → Require consensus between multiple oracles.
3. **Gas spikes:** During crashes, gas goes to 500+ gwei. Agent might fail to execute stops. → Pre-fund gas wallet, use priority fees, have fallback RPC.
4. **Liquidity traps:** Pool has no depth, can't exit without 50%+ slippage. → Monitor depth proactively, exit before it becomes critical.
5. **Regulatory black swans:** SEC enforcement action, chain sanctions. → Have geo-fencing, chain blacklist, emergency pause button.

---

## User Experience

- **Onboarding quiz:** Determines risk tier (beginner/experienced/pro)
- **Safety dashboard:** Visual overview of all active rules, current status
- **Alert system:** Telegram/Discord notifications for rule triggers
- **Override flow:** User can temporarily disable specific rules (with confirmation)
- **Audit trail:** Every action logged — proposed, approved, executed, or blocked
