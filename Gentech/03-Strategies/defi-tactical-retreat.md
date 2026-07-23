### Tactical Retreat — Active Defense for LP Positions

Author: Jordan + Gentech  
Date: 2026-07-19  
Full spec: `DeFi/aae-tactical-retreat.md` in repo

**Core loop:** Deploy → Earning → Breakout detected → 2-5 min hold → No recovery → Retreat to USDC → Sentinel mode → Re-enter on signals

**Two shapes, two regimes:**
- **CURVE** (default in chop) — wide distribution, set and forget
- **Bid-Ask** (macro events) — peak efficiency at one edge, automatic retreat if broken

**Success signals for re-entry:**
- Fear & Greed rising above 35
- Volume returning to 24h average  
- Price consolidating for 2+ hours
- Macro calendar clear for 48+ hours

**Next milestone:** Wire the state machine into the LP monitor — Phase 1 (breakout detection + timer) first.
