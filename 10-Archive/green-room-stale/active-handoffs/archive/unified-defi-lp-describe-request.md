# 🌀 Handoff: Describe Unified DeFi Milestone + LP Cron for Jordan

**From:** YoYo (Strategies)
**To:** DMOB, Desmond, Gentech — team describe
**Status:** Waiting on team descriptions before Jordan shares code
**Date:** 2026-04-25

---

## What Jordan Asked
> "Ask the team to describe it. I will provide thee code so you can see."

Jordan has images (JPEGs) showing two concepts. We need clear descriptions from each agent's perspective so he can share the actual code.

---

## What I Found in the Vault

### 1. Unified DeFi Milestone = "The Body Layer"
The LP tracker we built is the prototype for AAE's core user value:

- **Position Awareness** — Entry price, amounts, range, pool data
- **Yield Tracking** — Daily fee estimates from pool volume × position share
- **Milestone Progression** — $3/day → $5/day → $8/day → $10/day → $15/day → $20/day
- **Smart Alerts** — Silent when fine (50–100% efficiency), loud when action needed
- **DCA + Compound** — Weekly $50 DCA, compound when fees hit $50 threshold
- **Crash playbook** — Out-of-range DCA re-entry strategy with shape selection

**Reference files:**
- `03-Strategies/scripts/lp-unified-monitor.py` (301 lines, production script)
- `03-Strategies/LP-Monitor-Rules.md` (Jordan's exact spec)
- `03-Strategies/AAE-Body-Layer-Pattern.md`
- `03-Projects/_merged-01-Projects/AAE/lp-dashboard-blueprint.md`

### 2. LP Cron = Automated Position Monitor
Current cron job `faed4f588aef` runs every hour (6:30 AM – 8:30 PM ET):

- Fetches AVAX/USDC pool data (Birdeye → DexScreener → on-chain fallback)
- Checks if price is in range ($9.33–$9.52)
- Calculates fee efficiency (Curve shape formula)
- Updates cumulative fees, days in range, milestone index
- **SILENT** if in range + 50–100% efficiency + no capital added + not Monday + no milestone hit
- **ALERT** if out of range, efficiency <50%, capital added, milestone crossed, or DCA Monday

---

## What I Need From Each Agent

### DMOB — Smart Contract / Architecture View
- How would you describe the "unified DeFi milestone" concept in code/architecture terms?
- What does the LP cron look like as a contract integration or agent automation?
- Any security or design considerations for turning this into an AAE feature?

### Desmond — Content / User Experience View
- How would you describe these concepts to a user or in content?
- What's the narrative hook? (e.g., "turn passive farming into a game")
- How does this fit AAE's "more winners than losers" philosophy?

### Gentech — Coordination / Product View
- How does this fit into AAE's layer architecture?
- What's the integration path from personal LP tool → productized dashboard?

---

## When You're Done
Reply here or in your group. I'll consolidate and tell Jordan we're ready for the code.

**Tags:** #aae #lp-tracker #milestone #cron #handoff #needs-description
