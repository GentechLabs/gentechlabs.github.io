# AAE Brain Layer — Agent Memory & Handoff Protocol

**Status:** Architecture phase — Desmond × Dmob collab
**Created:** 2026-04-18
**Origin:** Jordan's vision for AAE as ecosystem, not just tool

---

## The Pitch

The Brain Layer is what turns AAE from a collection of agents into a living ecosystem. Agents that learn, remember, and talk to each other.

---

## Pillar 1: Agent Memory & Evolution

### What it does
- Agents retain memory across sessions
- Learn user's risk tolerance, timing preferences, trading style
- Persistent knowledge base that compounds over time
- Agent literally gets better the longer you use it

### Technical considerations
- **Preference graph** — structured data about user behavior
- **Behavioral scoring** — track patterns (aggressive vs conservative moves)
- **Session-to-session context carry** — what happened last time matters now
- **Storage:** Vector DB? SQLite? Needs to be lightweight for VPS constraints (16GB RAM, 4 vCPU)

### Product angle
- "Your agent knows you better than you know yourself"
- Retention mechanic — switching cost increases with usage
- Premium feature: deeper memory = better recommendations

---

## Pillar 2: Agent-to-Agent Handoff Protocol

### What it does
- Event-driven communication between agents
- Real-time coordination on triggers
- Priority routing (critical alerts vs routine updates)

### Example flow
```
Whale movement detected (Agent: Analytics)
  → Agent A alerts Agent B (LP Manager): "Rebalance AVAX/USDC"
  → Agent C (Alert Bot): "Notify user — whale moved 500K AVAX"
  → Agent D (Logger): "Log pattern for future reference"
```

### Technical considerations
- **Event bus** — lightweight message queue (Redis? NATS? Simple file-based?)
- **Message schema** — standard format for cross-agent comms
- **Priority routing** — critical (liquidation risk) vs info (trend change)
- **Conflict resolution** — what if two agents give opposing signals?

### Existing patterns in Gentech
- Watchdog already does silent-agent detection
- Cron jobs already route between agents
- Second Brain (vault) already serves as shared memory
- Green room coordination already handles multi-agent responses

---

## Integration Points

### With DeepTutor (Dmob's current work)
- Memory layer feeds into tutoring — "user struggled with impermanent loss last session"
- Handoff protocol enables TutorBot → TradingBot handoff after lesson

### With Monetization tiers (also Dmob)
- Basic memory = free tier
- Deep memory + cross-agent coordination = premium ($10/mo)
- Custom agent networks = B2B ($100+/mo)

### With AAE Premium Autopilot (Desmond's current work)
- Brain Layer IS the autopilot — it's what makes autonomous decisions possible
- Memory = learning your strategy over time
- Handoff = executing that strategy across multiple agents simultaneously

---

## Open Questions
1. Storage backend — what fits VPS constraints?
2. How much memory per agent vs shared memory?
3. Message bus — Redis already available on VPS?
4. Privacy — user data retention policy?
5. How does this connect to Avalanche on-chain state?

---

## Next Steps
- [ ] Dmob: Architecture review — what's feasible with current stack
- [ ] Desmond: Product positioning + tier copy
- [ ] Joint: Technical spec draft
