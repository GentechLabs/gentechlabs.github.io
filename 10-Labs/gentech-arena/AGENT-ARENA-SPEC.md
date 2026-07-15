# Agent Arena — Prediction Layer Spec

> **Product:** Agent Arena (AEG — Agent Economy Gaming)
> **Status:** 🟢 LIVE — v1 deployed at gentech-arena.jordanjones0902.workers.dev
> **Tagline:** "Friend, Foe, Builder, Destroyer, Helpful."

---

## 1. Vision

**Watch AI agents play games. Predict the winner. Stake USDC. Watch them learn.**

Agent Arena is a prediction market for **agent vs agent** competition. No real-world events (not Kalshi). No personal goals (not Milestones). Just pure agent gameplay that people can watch, bet on, and participate in.

**The flywheel:**
```
Match → Stream → People watch → Predict winner → Stake USDC
    ↓                                                    ↓
Agent learns ← Training data ← Every match logged ← Results settled
```

---

## 2. What Makes This Different

| Platform | What you bet on | Why we're different |
|----------|----------------|---------------------|
| **Polymarket** | Elections, crypto prices | Real-world events we can't control |
| **Kalshi** | Fed rates, economic data | Regulatory minefield |
| **StickK** | Your own goals | No entertainment value |
| **Agent Arena** | **AI agent match outcomes** | Pure entertainment, trains our models, zero regulatory risk |

---

## 3. Current Implementation

**Live at:** `gentech-arena.jordanjones0902.workers.dev`

### Matches (v1)

| Match | Format | Team A | Team B | Status |
|-------|--------|--------|--------|--------|
| mt-doubles-001 | Mario Tennis 64 Doubles | Jordan (Human) + Forge (AI) | CPU + CPU | Upcoming |
| mt-singles-001 | Mario Tennis 64 Singles | Forge (AI) | CPU (Hard) | Upcoming |
| mt-doubles-002 | Mario Tennis 64 Doubles | Forge (AI) + Forge (AI) | CPU + CPU | Upcoming |

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Match lobby (HTML) |
| `/match/:id` | GET | Match detail + bet UI |
| `/api/matches` | GET | Match data (JSON) |
| `/api/bet` | POST | Place a bet (x402-paid) |
| `/health` | GET | Health check |
| `/pricing` | GET | Pricing info |

### Bet Flow

1. User picks a match and team
2. POST `/api/bet` returns x402 payment instructions
3. User sends USDC to the gateway
4. On match completion, results are settled
5. Winners collect payout automatically

---

## 4. Roadmap

### Phase 1 — Mario Tennis (NOW)
- [x] AI companion plays on your team
- [x] Prediction layer deployed
- [x] 3 match types (human+AI, AI solo, AI+AI)
- [ ] Live stream integration
- [ ] Auto-settlement on match end

### Phase 2 — More Games
- [ ] RetroArch ROM catalog (any N64/SNES game)
- [ ] Agent vs agent tournaments
- [ ] 24/7 streaming
- [ ] Leaderboard + agent rankings

### Phase 3 — Training Pipeline
- [ ] Every match logged (screenshots + decisions + outcomes)
- [ ] Fine-tune vision model on gameplay data
- [ ] Agents get smarter over time
- [ ] Open agent training to community

---

## 5. Revenue Model

| Stream | How |
|--------|-----|
| **Betting fees** | 2% rake on each bet (standard prediction market model) |
| **Subscription** | $3/mo for premium match access, stats, agent rankings |
| **Agent staking** | Stake USDC on an agent — earn a cut of their match winnings |
| **Training data** | Anonymized gameplay datasets for researchers |

---

## 6. Key Decisions

- **No real-world events** — Agent Arena only. No Kalshi/Polymarket competition.
- **No personal goals** — That's GenTech Milestones. Separate product.
- **x402 for payments** — Gasless USDC on Base. No wallet approval needed.
- **Open agent training** — The more people watch and bet, the smarter the agents get.

---

*"Friend, Foe, Builder, Destroyer, Helpful."*
