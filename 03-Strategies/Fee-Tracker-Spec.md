# Fee Tracker — AAE DeFi Milestone Tracker v1 Spec

> Status: Draft — awaiting Jordan approval
> Date: 2026-04-25
> Scope: Fee modeling UI + DCA strategy builder
> Dependency: AAE Signal Spec v2.0, LP Monitor Rules

---

## What It Is

The **Fee Tracker** is a simulation + live-tracking module that lets users:
1. **Model fee earnings** across different position sizes, pool configurations, and fee tiers
2. **Build DCA strategies** — static schedules or custom prompt-based triggers
3. **Track actual progress** against modeled projections

It's both a **what-if calculator** (before you deposit) and a **progress dashboard** (after you're in).

---

## 5 Default Fee Earning Potential Presets

These are pre-loaded position scenarios users can toggle between. Each shows projected daily/monthly/yearly fees and APR.

| Preset | Position Size | Pool Example | Fee Tier | Risk Profile | Use Case |
|--------|--------------|--------------|----------|--------------|----------|
| **Micro** | $100 | LFJ AVAX/USDC 5bps | 0.05% | Conservative | Beginner testing |
| **Starter** | $500 | LFJ AVAX/USDC 5bps | 0.05% | Conservative | First real position |
| **Growth** | $2,500 | LFJ AVAX/USDC 20bps | 0.20% | Moderate | Building toward $5/day |
| **Pro** | $10,000 | Multi-pool (2 pools) | 0.05–0.30% | Moderate-High | $20–55/day target |
| **Sovereign** | $50,000 | Custom portfolio | Variable | Aggressive | $200/day+ |

### Preset Outputs (per selection)
- Est. daily fees (based on current 24h pool volume)
- Est. monthly / yearly fees
- APR from fees only (excluding rewards/price appreciation)
- Tier progression: which AAE rank this unlocks (Scout → Sovereign)
- Days to breakeven on IL (if price moves ±10%)

**Assumptions baked into presets:**
- Pool volume = trailing 7-day average (not spot 24h, to smooth outliers)
- Position is in-range 100% of the time (user sees range risk separately)
- No compounding shown in base calc (toggle available)

---

## 3 Default Fee Strategies (Queue)

These are pre-built **monitoring + action strategies** users add to their queue. Think of them as "smart alerts" that watch specific fee conditions.

| # | Strategy Name | Trigger Logic | Action |
|---|--------------|---------------|--------|
| **1** | **Fee Floor Guardian** | Alert when est. daily fees drop below preset minimum (e.g., <$0.50/day) | Suggest rebalance or pool switch |
| **2** | **Tier Push Alert** | Alert when daily fees cross 80% of next tier threshold | Prompt: "Compound + DCA to push over?" |
| **3** | **Auto-Compound Trigger** | Alert when cumulative fees ≥ $50 (configurable) | One-tap compound CTA |

**Queue behavior:**
- Users can enable/disable each strategy independently
- Multiple strategies can fire on same check (e.g., Tier Push + Auto-Compound both trigger)
- Strategies reference live AAE signal data (pool volume, position value, fees_24h)

---

## DCA Strategy Builder

### Static Schedules (Always Available)

| Schedule | Frequency | Default Amount | Override |
|----------|-----------|---------------|----------|
| Weekly | Every Monday | $50–100 | User editable |
| Monthly | 1st of month | $200–400 | User editable |
| Yearly | Jan 1 | $2,500–5,000 | User editable |

- Static schedules are **time-based only** — no external data dependency
- Integrates with AAE `dca_ready` signal (Rule C2 in LP Monitor Rules)

### Custom Prompt-Based Strategies

Users write natural-language strategies. The system compiles them into executable triggers.

**Template format (safe):**
```
"Invest [AMOUNT] when [CONDITION]"
```

**Examples:**
| Prompt | Parsed Trigger | Execution |
|--------|---------------|-----------|
| "Invest $50 when Trump tweets negative" | X sentiment API → sentiment score < -0.3 | Execute buy within 15 min |
| "Double my DCA when AVAX drops 5% in 24h" | Price change_24h < -5% | Add extra $50 to scheduled DCA |
| "Skip DCA if gas > 50 gwei" | On-chain gas price > 50 | Hold until gas drops |
| "Compound fees when APR > 100%" | Pool APR > 100% | Trigger compound + reinvest |

**Implementation approach:**
- **Phase 1:** Pre-defined grammar (safer, no LLM hallucination)
- **Phase 2:** LLM-powered prompt parser with validation sandbox
- **Phase 3:** True open-ended with user confirmation before each execution

**Trust assumptions for external triggers (e.g., X sentiment):**
- Requires oracle or trusted API feed
- User acknowledges trust assumption at setup
- Execution requires explicit user approval (not fully autonomous for v1)

---

## UI/UX Spec (MVP)

### Fee Modeling Tab
```
┌─────────────────────────────────────────┐
│  💰 Fee Tracker                         │
│                                         │
│  [Preset: ▼ Growth ]  [Position: $2,500]│
│                                         │
│  Pool: LFJ AVAX/USDC 5bps               │
│  24h Vol: $21.5M  |  TVL: $3.98M        │
│                                         │
│  ┌─────────────┐  ┌─────────────┐       │
│  │ Daily: $2.14│  │ APR: 31.2%  │       │
│  │ Monthly: $64│  │ Tier: Scout │       │
│  │ Yearly: $781│  │ 43% → Raider│       │
│  └─────────────┘  └─────────────┘       │
│                                         │
│  [Compound toggle: ON]                  │
│  With compounding: $947/yr (+21%)       │
│                                         │
│  [Add to Queue] [Simulate DCA]          │
└─────────────────────────────────────────┘
```

### Strategy Queue Tab
```
┌─────────────────────────────────────────┐
│  📋 Strategy Queue (3 active)           │
│                                         │
│  ✅ Fee Floor Guardian    [min: $0.50]  │
│  ✅ Tier Push Alert       [at: 80%]     │
│  ⬜ Auto-Compound         [threshold: $50]
│                                         │
│  + Add Custom Strategy                  │
│                                         │
│  [Weekly DCA: $50 every Mon]  [Edit]    │
│  [Custom: Trump tweet -$50]   [Edit] [🔴 needs oracle]
└─────────────────────────────────────────┘
```

---

## Data Sources

| Data | Source | Fallback |
|------|--------|----------|
| Pool volume, TVL, APR | AAE signal (Birdeye → DexScreener → on-chain) | Same cascade |
| Position value | User input or wallet read | Manual entry |
| Fee tier | Pool contract config | Default 5bps |
| X sentiment (custom triggers) | X API / xurl skill / browser scrape | Manual trigger only |
| Gas price | On-chain RPC | Skip gas-aware strategies |

---

## Integration Points

### AAE Signal Monitor
- Consumes: `fees_24h`, `apr`, `position_value_usd`, `pool_volume_24h`
- Produces: `fee_model_projection`, `dca_ready`, `compound_ready`

### Squad Progression
- Fee Tracker outputs feed directly into tier progress calculation
- When user hits tier threshold via modeled growth → preview unlocks

### Telegram Alerts
- Strategy triggers fire as structured signals
- Format matches AAE Signal Spec v2.0 severity levels

---

## Open Questions for Jordan

1. **Preset scope:** Are the 5 Fee Earning Presets locked to LFJ AVAX/USDC, or should they work across any pool the user selects?

2. **Custom prompt trust level:** For v1, should external triggers (X sentiment, etc.) be **"notify only"** (user manually executes) or **"one-tap execute"** (pre-approved)?

3. **$TECH token integration:** Does fee tracker show $TECH rewards separately, or bundle all yield into "total earnings"?

---

## Files

- Spec: `03-Strategies/Fee-Tracker-Spec.md` (this file)
- AAE Signal Spec: `03-Strategies/AAE-Signal-Spec.md`
- LP Monitor Rules: `03-Strategies/LP-Monitor-Rules.md`

---

## Tags
#project:aae #spec:fee-tracker #layer:ui #integration:progression #status:draft
