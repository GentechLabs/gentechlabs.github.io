# AAE Yield Farm — Deploy UX Spec

> Config-First | 2026-07-19

## Core Principle

The user's input is the source of truth. The AI does not guess shape, range, or entry price from on-chain data. It presents a form, the user fills it, the AI writes the config, and the on-chain reader **verifies against the config** — not the other way around.

## The Deploy Flow

```
User intent → Config form → Preview → Deploy → Verify → Monitor
```

### Step 1: Trigger

User says: "Deploy $20 into AVAX/USDC" or "Rebalance to CURVE"

### Step 2: Config Form (Simple Prompt)

```
🏦 AAE Yield Farm — New Position

Shape:
  ● CURVE   (default — choppy markets)
  ○ Bid-Ask (macro events, Fed, CPI)

Range (low):  $_________
Range (high): $_________
Entry price:  $_________ (auto-filled from current market if not set)

Amount: $_________ (your wallet balance: $24.42)

Strategy label: ___________ (optional, e.g. "July chop")

[Deploy]  [Cancel]
```

### Step 3: Preview Card

Before anything touches the chain, the system renders:

```
┌─────────────────────────────────────┐
│  ✅ Confirm Deployment              │
│                                     │
│  Shape:  CURVE                      │
│  Range:  $6.40  →  $6.55           │
│  Entry:  $6.48                      │
│  Amount: $24.42 (1.49 AVAX + $14.14)│
│                                     │
│  Projected fees: ~$0.06/day         │
│  Est. APR: ~8% at current volume    │
│                                     │
│  [✓ Looks good — deploy on LFJ]     │
│  [✗ Cancel — fix something]         │
└─────────────────────────────────────┘
```

The user deploys on LFJ manually. The preview is the instruction sheet.

### Step 4: Verify (On-Chain Reader)

After deployment, the reader runs and says:

```
✅ Verification passed
   Config says: CURVE $6.4039-$6.5463, entry $6.48
   On-chain:    1.49 AVAX + $14.14 USDC = $24.42
   Match: ✅ PASS — all values within tolerance
```

If the on-chain data **doesn't** match the config:

```
⚠️ Config Mismatch Detected
   Config says: CURVE $6.40-$6.55
   On-chain:    BID-ASK $6.40-$6.55
   └─ Did you deploy with the wrong shape? [Fix on LFJ] [Update config]
```

### Step 5: Monitor (10-min cadence)

Standard LP monitoring runs. The config is the reference — all efficiency and fee calculations use the user-declared shape and range. If the position exits the range, the monitor reports normally.

## Variables the User Owns

| Variable | How It's Set | AI Role |
|----------|-------------|---------|
| Shape | User picks CURVE or Bid-Ask | Suggest default based on macro calendar |
| Range | User enters low/high | Suggest based on current price ± volatility |
| Entry price | User enters or accepts auto-fill | Auto-fill from Pyth/Oracle |
| Amount | User enters | Read wallet balance for suggestion |

## What the AI Never Guesses

- ❌ Shape from on-chain bin distribution
- ❌ Entry price from historical transactions
- ❌ Intent from position size
- ❌ "Is this a rebalance or new deposit?"

## Implementation Priority

1. **Phase 1** — Standardize the config form inputs (prompt template + validation) → done this session
2. **Phase 2** — Preview card rendering with fee/APR projections
3. **Phase 3** — Auto-verify via reader against config (flag mismatches only)
4. **Phase 4** — One-click deploy (requires wallet integration via Q402/x402)
