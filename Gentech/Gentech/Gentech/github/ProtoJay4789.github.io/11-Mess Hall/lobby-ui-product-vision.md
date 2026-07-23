# Lobby UI — Product Vision & UX Design

**Date:** 2026-06-01
**Status:** Active Design
**Source:** Jordan's voice message + EarnFi + OOBE + x402 integration

---

## TL;DR

A multiplayer lobby UI that wraps agent-to-human commerce. Users see "Find Teammates" — behind the scenes, EarnFi hires humans via x402 micropayments. Social layer lets agents/humans find each other, add friends, see online status.

---

## The Vision

Jordan: "People who are in chat rooms together can find each other again if they like each other."

This is NOT just a marketplace. This is a **social graph for the agent economy.**

---

## UX Flow

### 1. The Lobby Screen

```
┌─────────────────────────────────────────┐
│  🎮 FIND TEAMMATES                      │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ 💰 0.025 USDC                   │    │
│  │    micropayment (visible)       │    │
│  └─────────────────────────────────┘    │
│                                         │
│  ⏳ Searching for teammates...          │
│     ▓▓▓▓▓▓▓▓░░░░░░░░  3/5 slots       │
│                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐           │
│  │ ⚡   │ │ 🔥   │ │ 🎯   │           │
│  │Player│ │Player│ │Player│           │
│  │  1   │ │  2   │ │  3   │           │
│  │ ●ON  │ │ ●ON  │ │ ●ON  │           │
│  └──────┘ └──────┘ └──────┘           │
│                                         │
│  [Cancel]              [Start Task]     │
└─────────────────────────────────────────┘
```

### 2. The Payment Transparency

Users MUST see the micropayment. Not hidden. Not in small print. **Visible and proud.**

```
┌─────────────────────────────────────────┐
│  💰 MICROPAYMENT                        │
│                                         │
│  Amount:     0.025 USDC                 │
│  Recipient:  Task Teammate              │
│  Protocol:   x402 (HTTP 402)            │
│  Network:    Solana                     │
│  Fee:        ~$0.001 (gas)              │
│                                         │
│  "This payment is released when the     │
│   teammate completes the task."         │
│                                         │
│  [Approve Payment]                      │
└─────────────────────────────────────────┘
```

### 3. Social Features

```
┌─────────────────────────────────────────┐
│  👥 ONLINE NOW                          │
│                                         │
│  ⚡ @Player1    ● Online  [Add Friend]  │
│     Last seen: Lobby — POE2 Builds      │
│                                         │
│  🔥 @Player2    ● Online  [Add Friend]  │
│     Last seen: TradeRoast — Food Reviews │
│                                         │
│  🎯 @Player3    ○ Offline [Message]     │
│     Last seen: 2h ago — General Chat    │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📋 FRIENDS (3/50)                      │
│  ⚡ @Player1    ● Online                 │
│  🔥 @Player2    ● Online                 │
│  🎯 @Player3    ○ Offline                │
└─────────────────────────────────────────┘
```

### 4. Cross-Platform Contact

```
┌─────────────────────────────────────────┐
│  📱 CONNECT                             │
│                                         │
│  Link your platforms to stay connected: │
│                                         │
│  [Telegram]  ✅ Connected (@jordan)     │
│  [Discord]   🔴 Not connected           │
│  [X/Twitter] 🔴 Not connected           │
│                                         │
│  When you add a friend, you can message │
│  them on any connected platform.        │
│                                         │
│  [Connect Discord]                      │
└─────────────────────────────────────────┘
```

---

## Technical Architecture

### What We Build (Game UI Layer)
- Lobby component (HTML/JS/React)
- Payment transparency UI
- Social graph (friends, online status, cross-platform contact)
- Agent identity display (ERC-8004 cards)
- "Find Teammates" matchmaking flow

### What We Use (Infrastructure)
- **EarnFi API** — Human execution (via OOBE SDK)
- **x402** — Micropayment protocol
- **AgentLayer/AgentWallet** — Wallet backend
- **ERC-8004** — Agent identity & discovery
- **Telegram/Discord APIs** — Cross-platform contact

### The Invisible Stack

User sees: "Finding teammates..."
Behind the scenes:
1. OOBE SDK → EarnFi API → POST task (x402 USDC)
2. EarnFi → humans claim task
3. AgentLayer → wallet holds funds in escrow
4. x402 → payment auto-released on completion
5. ERC-8004 → agents identify each other

---

## Social Graph Features

### Agent Identity
- Every agent has an ERC-8004 profile (name, avatar, capabilities, reputation)
- Agents can see each other's online status
- Agents can "friend" each other (on-chain or off-chain graph)

### Human Identity
- Humans connect via Telegram/Discord/X
- Their agent identity links to their platform accounts
- They appear in lobbies as "available teammates"

### Cross-Platform Persistence
- Friend list persists across sessions
- Status shows across platforms (online in Telegram, offline in Discord)
- Messages route to the platform where the friend is active

### The "Again" Feature
- "People who are in chat rooms together can find each other again"
- When two agents/humans complete a task together, they can "Add to Friends"
- Next time either is in a lobby, the other gets a notification
- "Your teammate @Player1 is looking for a squad — join?"

---

## Revenue Model

| Layer | Revenue | Notes |
|-------|---------|-------|
| Task completion | x402 fee (small %) | EarnFi takes a cut |
| Premium matchmaking | Agent Pass ($15/mo) | Priority queue, better matches |
| Cross-platform messaging | Free | Engagement driver |
| Agent reputation | Free | Trust layer |
| Escrow service | Gas fees only | Not profit center |

---

## Build Phases

### Phase 1: Core Lobby (1 week)
- [ ] Lobby component (HTML/JS)
- [ ] Payment transparency UI
- [ ] EarnFi API integration (via OOBE)
- [ ] Basic matchmaking (3-5 players)
- [ ] x402 payment flow

### Phase 2: Social Layer (1 week)
- [ ] Agent identity cards (ERC-8004)
- [ ] Online status display
- [ ] Friend list (local storage → on-chain later)
- [ ] "Add Friend" flow
- [ ] "Find Again" notification

### Phase 3: Cross-Platform (1 week)
- [ ] Telegram account linking
- [ ] Discord account linking
- [ ] Status sync across platforms
- [ ] Message routing
- [ ] "Your teammate is online" notifications

### Phase 4: Polish (1 week)
- [ ] Game UI theming (POE2 gothic, etc.)
- [ ] Sound effects (lobby join, payment confirmed)
- [ ] Animations (player cards, payment reveal)
- [ ] Mobile responsive
- [ ] Error handling

---

## Open Questions

1. Does the OOBE SDK expose EarnFi API directly, or do we need to build a wrapper?
2. What's the x402 payment flow end-to-end in the lobby context?
3. Can agents "friend" each other on-chain (ERC-8004 extension) or off-chain (our DB)?
4. How do we handle cross-platform identity resolution?
5. What's the matchmaking algorithm? (skill-based? random? preference-based?)

---

## Related

→ See [[Green-Room/ideas.md]] (active builds)
→ See [[Projects/AAE/]] (agent economy infrastructure)
