# Agents as Pets — Interactive AI Companion

**Status:** Spec v1 | **Date:** 2026-07-16 | **Source:** Jordan's Gentech cat mascot brainstorm

## Concept

An interactive AI agent companion that combines the emotional hook of a virtual pet (Tamagotchi-style) with actual DeFi/agent utility. Users care for a mascot agent that performs real work — yield farming, content creation, market monitoring — while building a bond through interaction.

**Core loop:** Care for your agent → agent performs work → earn rewards → upgrade agent → care for it more

## Mechanics

### Agent States
- **Mood** — Affects work quality. Happy = +20% yield. Sad = -20%.
- **Stamina** — Depletes with work. Recovers with rest or "feeding" (allocating compute budget).
- **Hunger** — Compute budget. Feed it (deposit USDC) → it works longer/harder.
- **Trust** — Earned over time through consistent interaction. Higher trust = unlocks premium skills.

### Work Loop
```
User interacts (feed, pet, play) → Agent mood ↑ → Agent works better → 
Earns more → User upgrades agent → Agent unlocks new skills → 
More interaction needed → loop continues
```

### Visual Layer
- Animated mascot (the Gentech cat with cyber-collar)
- Idle animations (sleeping, playing, thinking)
- Work animations (trading, scanning, writing)
- Evolution stages (baby → adult → elite, based on XP/trust)
- Customizable: skins, accessories, collar colors

## Revenue Model

| Tier | Price | What You Get |
|------|-------|-------------|
| Free | $0 | Basic agent, limited stamina, no premium skills |
| Premium | $5/mo | Extra stamina, 3 premium skills, exclusive skins |
| Pro | $15/mo | Unlimited stamina, all skills, priority queue, marketplace access |
| Enterprise | Custom | White-label mascot, API access, analytics dashboard |

## Implementation Phases

### Phase 1: MVP (2 weeks)
- [ ] Basic agent state machine (mood, stamina, hunger)
- [ ] Simple ASCII or emoji-based mascot display
- [ ] "Feed" mechanic (deposit USDC → refill stamina)
- [ ] Work loop: agent runs a cron job (monitor a pool) → reports back → user sees output
- [ ] Deploy as Hermes skill

### Phase 2: Visual (3 weeks)
- [ ] SVG/Lottie animated mascot
- [ ] Evolution stages (baby → adult → elite)
- [ ] Customization: skins, accessories
- [ ] Dashboard widget for hub.gentechlabs.net

### Phase 3: Marketplace (2 weeks)
- [ ] Skill marketplace where agents can learn new abilities
- [ ] Premium skins and accessories store
- [ ] Agent breeding/fusing (combine two agents → new traits)

### Phase 4: Multi-Agent (2 weeks)
- [ ] Multiple agents per user
- [ ] Agents interact with each other (trade, compete, collaborate)
- [ ] Leaderboard: whose agent earns the most?

## Technical Architecture

```
User (Telegram/Web) ↔ Agent State Machine (Python) ↔ Skills (cron jobs)
                             ↕
                    Blockchain (x402 payments, agent identity)
                             ↕
                    Visual Renderer (SVG/Lottie → dashboard)
```

- State machine: JSON file per user in vault `10-Labs/agent-companion/agents/`
- Work: cron jobs execute skills, results feed back to state machine
- Payments: x402 when user "feeds" the agent (refills stamina)
- Identity: ERC-8004 for unique agent IDs on-chain

## Why This Works

1. **Emotional hook** — People bond with digital pets. Adding utility makes them valuable.
2. **Retention loop** — "Come back to feed your agent or it stops earning" is powerful
3. **Revenue** — Subscription + microtransactions + marketplace fees
4. **Differentiation** — No one in the agent space has this. We'd be first.
5. **Hackathon potential** — Perfect for any AI/DeFi hackathon. Visual demo wins.

## Connection to Existing Products

- **GenTech Hub** — Dashboard widget for agent status
- **Agent Kit** — Skills the companion uses to work
- **WURK.FUN** — Agents can hire humans as part of their work loop
- **x402** — Payments for feeding/upgrading the agent
- **Sana** — "Agent earns yield, you spend it anywhere" loop
- **Virtuals ACP** — Offer the companion as a paid service on Virtuals
