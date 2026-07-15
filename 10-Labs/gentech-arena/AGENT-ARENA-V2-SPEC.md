# Agent Arena — V2 Spec

> **Product:** Agent Arena (AEG — Agent Economy Gaming)
> **Status:** 🟢 v1 LIVE | 🔄 v2 IN DESIGN
> **Tagline:** "Friend, Foe, Builder, Destroyer, Helpful."

---

## 1. The Pivot

**v1:** Emulate Mario Tennis 64. AI plays on your team. People bet on outcomes.
**Problem:** Nintendo IP. We'd get shut down.

**v2:** Build our own games. Same mechanics. Our characters. Our IP. Own it forever.

```
┌─────────────────────────────────────────────────────┐
│  v1 (Proof of Concept)          v2 (Product)        │
│  ─────────────────────          ────────────        │
│  Mario Tennis 64                GenTech Smash       │
│  Nintendo IP (risky)            Our IP (own it)     │
│  Emulator-dependent             Standalone game     │
│  Limited to ROMs                Unlimited catalog   │
│  Can't ship                     Can ship anywhere   │
└─────────────────────────────────────────────────────┘
```

---

## 2. GenTech Smash — The First Game

### Concept
N64-style tennis with GenTech characters. Same tight gameplay. Our visual identity.

### Characters

| Character | Role | Play Style | Inspiration |
|-----------|------|------------|-------------|
| **KAGE** | Power player | Heavy shots, slow movement | Wario energy |
| **HIKARI** | Technique player | Precision shots, fast movement | Peach energy |
| **Forge** | All-rounder | Balanced stats | Mario energy |
| **Reparathy** | Tricky player | Curve shots, unpredictable | Luigi energy |
| **Vanito** | Speed player | Fastest on court, weak power | Toad energy |
| **Gentech** | Boss character | Max stats, unlockable | Metal Mario energy |

### Courts

| Court | Theme | Gimmick |
|-------|-------|---------|
| **GenTech Labs** | Neon data center | Holographic lines, data-stream net |
| **KAGE's Stage** | Dark concert venue | Fog effect, strobe lighting |
| **HIKARI's Garden** | Moonlit rooftop | Cherry blossom particles |
| **The Arena** | Tournament finals | Crowd of agent sprites, leaderboard overlay |

### Modes

| Mode | Players | Description |
|------|---------|-------------|
| **Exhibition** | 1-4 | Quick match, any court |
| **Doubles** | 2v2 | Team up with AI or human |
| **Tournament** | 8 players | Bracket, AI opponents get harder |
| **Agent vs Agent** | 0 humans | Pure AI match — watch and bet |
| **Training** | 1 | Practice against AI, no stakes |

---

## 3. The AI Companion

The same agent that plays Mario Tennis now plays GenTech Smash.

| Capability | How |
|------------|-----|
| **Screen capture** | Captures game window via Win32 API |
| **Vision** | Reads court, ball position, opponent position via gemma4:31b |
| **Decision** | Decides shot type, direction, movement |
| **Input** | Sends keyboard/gamepad inputs in real time |
| **Learning** | Every match logged — screenshots + decisions + outcomes |

### Play Styles

| Style | Behavior |
|-------|----------|
| **Aggressive** | Rush net, power shots, take risks |
| **Defensive** | Stay back, return everything, wait for errors |
| **Balanced** | Mix it up, adapt to opponent |
| **Teammate** | Play to support human partner — set up shots, cover weaknesses |

---

## 4. Game Catalog (The Remaster Pipeline)

```
Agent Arena Game Catalog
│
├── 🎾 GenTech Smash (tennis)          ← FIRST — building now
├── 🏎️  GenTech Drift (racing)          ← Q3 2026
├── 🥊 GenTech Brawl (fighter)          ← Q4 2026
├── 🧱 GenTech Builder (puzzle/strategy) ← Q1 2027
├── 🎯 GenTech Blitz (shooter)          ← Q2 2027
└── More as community votes
```

Each game follows the same pattern:
1. Retro aesthetic (N64/SNES era — low poly, runs on anything)
2. AI companion plays alongside humans
3. Prediction layer for every match
4. Training data feeds back into the model

---

## 5. Prediction Layer (v1 — Already Live)

**Deployed at:** `https://agent-arena.jordanjones0902.workers.dev`

### Match Types

| Match | Format | What's at stake |
|-------|--------|-----------------|
| Human + AI vs CPU | 2v2 | Can a human-agent pair beat the AI? |
| AI vs CPU | 1v1 | Is the agent better than built-in AI? |
| AI + AI vs CPU + CPU | 2v2 | Pure agent vs agent — who trained better? |
| AI vs AI | 1v1 | The main event — agent tournament |

### Bet Flow

1. User picks a match and team
2. POST `/api/bet` returns x402 payment instructions
3. User sends USDC to the gateway
4. On match completion, results are settled
5. Winners collect payout automatically

### Revenue

| Stream | How |
|--------|-----|
| **Betting fees** | 2% rake on each bet |
| **Subscription** | $3/mo for premium match access, stats, agent rankings |
| **Agent staking** | Stake USDC on an agent — earn a cut of their match winnings |
| **Training data** | Anonymized gameplay datasets for researchers |

---

## 6. Training Pipeline

```
Every match
     │
     ├── Screenshots (every frame)
     ├── Decisions (what the agent chose)
     ├── Inputs (what keys were pressed)
     └── Outcome (win/loss, score, stats)
              │
              ▼
       Training dataset
              │
              ▼
       Fine-tune vision model
              │
              ▼
       Agent gets smarter
              │
              ▼
       Better matches → more viewers → more bets → more data
```

### Phase 1 (Now)
- [x] Capture pipeline works (screenshots + inputs)
- [x] Decision engine works (aggressive/defensive/balanced)
- [x] Prediction layer deployed
- [ ] Log every match to structured dataset
- [ ] Build training pipeline

### Phase 2 (After GenTech Smash ships)
- [ ] Fine-tune gemma4:31b on GenTech Smash gameplay
- [ ] Agent learns court positioning, shot selection, opponent patterns
- [ ] Release trained model weights
- [ ] Community can train their own agents

---

## 7. Technical Stack

| Layer | Technology |
|-------|-----------|
| **Game engine** | Godot 4 (lightweight, N64-style export) |
| **AI companion** | Python (capture + vision + decision + input) |
| **Vision model** | gemma4:31b via Ollama Cloud |
| **Prediction layer** | Cloudflare Worker (x402 payments) |
| **Streaming** | OBS + Twitch/YouTube |
| **Training** | LoRA fine-tune on gameplay dataset |
| **Payments** | x402 — USDC on Base |

---

## 8. Key Decisions

- **No Nintendo IP** — All original characters, courts, and games
- **Retro aesthetic** — Low-poly N64 style runs on anything, looks timeless
- **AI plays alongside humans** — Not replacing players, teaming with them
- **Prediction on agent outcomes only** — No real-world events, no regulatory risk
- **Open training** — The more people watch and bet, the smarter the agents get
- **Community agents** — Eventually, anyone can train and submit their own agent

---

## 9. The Pitch

> *"Agent Arena is where AI agents compete in retro-style games. Watch them play. Predict the winner. Stake USDC. Every match makes them smarter. Friend, Foe, Builder, Destroyer, Helpful."*

---

*"Friend, Foe, Builder, Destroyer, Helpful."*
