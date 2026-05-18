# Brainstorm: The Burn Floor Flywheel

**Status:** HQ Discussion Seed
**Date:** 2026-04-19
**Source:** Bin-AMM scoping doc (Dmob) + Burn mechanism analysis (YoYo)

## The Core Flywheel

```
More LPs → deeper liquidity → more trading volume → more protocol fees →
healthier reserve pool → higher burn floor multiplier → better exit value for agents →
more agent mints → more trading volume → back to start
```

## What Makes This Different

**Other AMMs:** Fees go to LPs and maybe a protocol cut. That's it. No compounding loop.
**Our AMM:** Protocol fees split → burn (supply reduction) + treasury (reserve funding). Every trade makes the burn floor stronger.

## Key Discussion Points for HQ

### 1. Fee Split Design
What's the optimal split? Dmob's doc suggests:
- LP Share: 85-95%
- Protocol Fee: 2-5% → split between burn + treasury
- Example: 3% protocol fee → 1.5% burn, 1.5% treasury

**Question:** Higher burn = more deflationary pressure but slower reserve growth. Higher treasury = safer floor but less immediate burn effect. Where do we land?

### 2. Reserve Health Multiplier
The burn return formula: `burn_return = base_floor × reserve_health_multiplier`

Multiplier could scale with reserve ratio:
- Reserve ratio > 50% → 1.5x multiplier
- Reserve ratio 25-50% → 1.0x multiplier
- Reserve ratio 10-25% → 0.7x multiplier
- Reserve ratio < 10% → 0.5x (circuit breaker zone)

**Question:** Do we want a visible "reserve health" dashboard so users can see the floor strength?

### 3. Agent LP Revenue as Burn Floor Fuel
When agents earn fees from managing LP positions, that revenue:
- Counts toward the agent's "revenue generated" score
- Improves their individual burn floor tier
- Also feeds the shared reserve pool

**This means:** Active agents get a double benefit — personal burn floor improvement AND shared pool improvement.

### 4. The Narrative Angle
This is our hackathon pitch differentiator:
- Uniswap: "Provide liquidity, earn fees"
- LFJ: "Custom liquidity shapes, earn fees"
- **Gentech:** "Provide liquidity → strengthen the floor → make every agent's exit safer → attract more agents → more volume → repeat"

We're not just an AMM. We're a **floor-strengthening protocol**.

### 5. Risk: What If Volume Drops?
Flywheels work both ways:
- Low volume → fewer fees → reserve stagnates → burn floor weakens → agents exit → worse
- Need a minimum reserve floor that's independent of trading volume (e.g., mint fees seed the reserve)

**Question:** Should mint fees have a fixed reserve allocation separate from LP revenue?

## Sources
- Dmob's scoping: `/root/aae-contracts/docs/bin-amm-scoping.md` (sections 3.2-3.4)
- Burn mechanism analysis skill: `research/burn-mechanism-analysis/SKILL.md`
