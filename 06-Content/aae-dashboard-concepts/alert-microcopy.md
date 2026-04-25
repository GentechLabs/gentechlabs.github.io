# AAE Alert Microcopy

> In-app notifications, push messages, and Telegram bot responses for Squad Treasury + Progression.
> Tone: Confident, concise, action-oriented. No panic. No FUD.

---

## Severity Levels

### 🟢 SILENT → No notification
_Internal log only. User sees routine update in dashboard._

### ✅ OK → Informative notification
```
Squad Treasury Update
🟩 In Range — $0.33 earned today
Rank: Scout → Raider (6.6%)
```

### ⚠️ ALERT → Action suggested
```
Position Alert
🟥 AVAX/USDC out of range
Efficiency: 0% — Vote on rebalancing strategy
```

### 🚨 CRITICAL → Urgent action
```
URGENT: Position at Risk
Efficiency dropped to 12%
Suggest: Tighten range or shift to Spot shape
```

---

## Position Status Messages

### In Range
- "🟩 In Range — Your squad is earning."
- "Fees flowing. $0.33 today, $12.45 since deposit."
- "Position healthy. Continue earning."

### Out of Range
- "🟥 Out of Range — Squad vote required on rebalancing."
- "Price left the range. No fees until rebalance."
- "You're holding 100% AVAX. DCA opportunity?"

### Low Efficiency
- "Efficiency at 42% — Consider tightening range."
- "Price drifting toward edge. Rebalance recommended."

### Recovery
- "🎉 Back in range! Earning resumed."
- "Recovery confirmed. Fees flowing again."

---

## Milestone / Rank Messages

### Tier Promotion
- "🏆 SQUAD PROMOTED: Scout → Raider!"
- "New unlock: SPOT + BIDIRECTIONAL shapes now available."
- "$20/day achieved. Your squad is leveling up."

### Progress Update
- "Scout → Raider: 34% complete"
- "$6.80/day — $13.20 to go until Raider"
- "14 days in range. Steady progress."

### Max Tier
- "👑 Sovereign achieved. Custom strategies unlocked."
- "You’ve reached the top. Time to build your own playbook."

---

## Compound / DCA Messages

### Compound Ready
- "🔄 Compound ready: $52.30 in fees. Reinvest + DCA?"
- "Fee threshold hit. Time to grow the position."

### DCA Day
- "💰 Monday DCA: $50 ready to deploy."
- "Weekly DCA scheduled. Add to position?"

### Compound Complete
- "✅ Compounded: +0.45 AVAX / +$28 USDC added"
- "Position grown. New APR: 5,247%"

---

## Empty / Onboarding States

### No Position
- "No active positions. Time to deploy some capital, Scout."
- "Your squad treasury is empty. Start with a CURVE position on AVAX/USDC."

### First Deposit
- "🎯 First position deployed! Welcome to the squad."
- "Tracking started. Milestone: $5/day (Scout)."

### Waiting for Squad
- "Solo mode active. Invite squad members to pool capital."
- "More contributors = larger positions = better fee efficiency."

---

## Shape-Specific Messages

### CURVE
- "Curve shape active — capturing volatility both ways."
- "Best for: Chop, sideways markets."

### SPOT
- "Spot shape active — uniform fee capture."
- "Best for: Stable ranges, predictable volume."

### BIDIRECTIONAL
- "Bidirectional shape — earning at the edges."
- "Best for: Breakout plays, range expansion."

---

## Error / Fallback Messages

### Data Source Fallback
- "DexScreener data loaded. (Birdeye temporarily unavailable)"
- "Using on-chain fallback. Volume data may be delayed."

### All Sources Down
- "Data sources reconnecting. Last known price: $9.45"
- "Network hiccup. Your position is safe — checking again in 15 min."

---

## Telegram Bot Responses

### /status command
```
AVAX/USDC — Scout (Tier 1)
🟩 In Range | $83.92 | 73.7% efficiency
24H: $0.33 | Total: $12.45
Next: Raider ($20/day) — 6.6%
Action: HOLD
```

### /compound command
```
Claimable: $1.13 AVAX
Threshold: $50
Status: Not yet — $48.87 to go
Est. time: 4 days at current rate
```

### /rank command
```
Rank: Scout 🥈
Daily: $5.00 target
Current: $0.33/day
Progress: 6.6%
Days in range: 14
```

---

## Voice / TTS Variants (Longer, conversational)

### Position Update
> "Your AVAX-USDC squad position is in range and earning. You've pulled in 33 cents today, bringing your total to twelve dollars and forty-five cents. You're still a Scout, working toward Raider status at twenty dollars a day. Current progress: six point six percent. Keep stacking."

### Out of Range Alert
> "Heads up — AVAX just moved outside your squad's range. You're not earning fees right now, but you're holding AVAX. Consider voting on a rebalance strategy with your squad."

### Milestone Hit
> "Big win — your squad just promoted to Raider! That means twenty dollars a day in estimated fees. You've unlocked SPOT and bidirectional strategies. Time to expand the playbook."

---

**Tags:** #aae #microcopy #ux #alerts #content
