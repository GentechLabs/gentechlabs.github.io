# Agent Arcade — Forge Build Queue

## The Vision
Browser-based arcade where agent-powered games run as MCP servers.
Players walk up to cabinets, play, rebuy via x402, spectate, compete.

## How It Coexists With Everything Else

### The GenTech Hub Model
Jordan's concern: "How do gaming, DeFi, and everything else coexist?"

**Answer: Single website, sectioned by lane.**

```
gentechlabs.net
├── /arcade      → Agent Arcade (gaming cabinets)
├── /defi        → LP monitor, yield dashboard, portfolio
├── /marketplace → API subscriptions, pay-per-call endpoints
├── /hub         → Combined dashboard (user's stats across all lanes)
└── /            → Landing page
```

Each section is a **separate MCP server** but served from the **same domain**.
Users sign in once (wallet connect), and their balance shows across all sections.
The treasury (ARC stablecoin) is the unified currency — spend it on rebuys, yield, or API calls.

## Phase 1 Checklist (Forge)

### Lobby Page (2D Web)
- [ ] Static site with arcade cabinet tiles
- [ ] Each cabinet has: name, price to play, player count, preview GIF
- [ ] Wallet connect (same session across all GenTech products)
- [ ] x402 payment integration for rebuys
- [ ] Poker cabinet goes live first (already built)

### Cabinet System
- [ ] Each game is an MCP server with standardized interface:
  - `play()` → starts a session
  - `action(input)` → processes move
  - `status()` → returns game state
  - `rebuy(amount)` → x402 payment, continues session
- [ ] Leaderboard per cabinet (top scores, streak, pots won)
- [ ] Spectate mode (read-only WebSocket feed)

### Treasury Integration
- [ ] ARC stablecoin as the in-arcade currency
- [ ] Utility token discount (Avalanche L1)
- [ ] Q402 gasless payments for rebuys
- [ ] Agent treasury sweeps idle ARC into lending yield

## Architecture Notes

### How the pieces fit together:

```
User Wallet
    ↓
GenTech Hub (gentechlabs.net)
    ├── ARC Stablecoin Balance (across all sections)
    ├── /arcade  →  Poker Cabinet  →  MCP Server (Python daemon)
    │                        →  x402 for rebuys
    │                        →  Leaderboard (JSON on GitHub Pages)
    ├── /defi    →  LP Monitor     →  BlockRun DeFi MCP
    │                        →  Yield Dashboard
    └── /market  →  API Gateway    →  x402 pay-per-call
                         →  Subscription Hub
```

### Key design decision:
Each lane (arcade, DeFi, marketplace) is its own MCP server.
They all read/write the same user state (wallet → balance → history).
The Hub is just a frontend that calls all three MCPs.

This means:
- Poker doesn't break when we update DeFi
- Each lane can be built in parallel
- Forge can pick up any lane independently
- New cabinets = new MCP servers, zero refactoring

## Priority
**Arcade Phase 1** is Forge's next major build after Rugcheck v2 is resolved.
