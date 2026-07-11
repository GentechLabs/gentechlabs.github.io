# Carbon Engine × GenTech — Brainstorm

> **Source:** Carbon Engine open-sourced by Fenris Creations (CCP Games) under MIT
> **Date:** 2026-07-11
> **Status:** Green Room — scouting for Forge evaluation
> **Tags:** #forge #gaming #romai #carbon

---

## What Carbon Actually Is

It's a **networking library** (CarbonIO) that grew into a **game engine framework**. EVE Online runs on it — thousands of players, real-time physics synchronization, Python scripting. The engine components exist to support the networking, not the other way around.

**Key repos (33 total, MIT):**
| Repo | Stars | Function | Our Fit |
|------|-------|----------|---------|
| `trinity` | 377 | Rendering engine | Visuals for AAE trading game |
| `destiny` | 159 | Physics + pathfinding | Multi-agent spatial coordination |
| `core` | 124 | Low-level C++ foundation | Engine plumbing |
| `blue` | 21 | **Python/C++ bridge** | **This is our entry point** |
| `audio` | 28 | Audio engine | Companion voice pipeline |
| `mesh` | 29 | 3D mesh manipulation | Asset pipeline |
| `imagetools` | 10 | Python image processing | Screen analysis |
| `exefile` | 19 | Build system | Desktop deployment |
| `vcpkg-registry` | 11 | Package registry | Dependency management |

---

## Three Integration Layers

### Layer 1: Blue (Python/C++ Bridge) — Immediate Value

**Blue** is the glue between Python and C++. It exposes C++ classes/functions to Python natively. Our Agent Kit is Python. Carbon's scripting is Python. This is the natural seam.

**What this means:**
- Gentech Agent Kit tools can be called from inside Carbon (agents running inside the game engine)
- Carbon's engine state is accessible from Python (agents read/write game world)
- No FFI, no REST bridge, no shim layer — direct C++ → Python calls

**Current use in EVE:**
- All game logic in Python
- All rendering/physics/networking in C++
- Blue bridges both worlds

### Layer 2: CarbonIO (Networking) — Multi-Agent Infrastructure

**CarbonIO** handles reliable data transmission and synchronization across persistent virtual worlds. It's battle-tested at EVE's scale.

**Our angle:**
- Multi-agent systems need networking (agents coordinate, share state)
- CarbonIO is already built for 10K+ concurrent connected entities
- Agent Arena could use CarbonIO as its networking layer
- Replace WebSocket/MQTT with a proven MMO-grade networking stack

### Layer 3: Destiny (Physics/Simulation) — Agent Spatial Reasoning

**Destiny** simulates the game world — position, velocity, collision, pathfinding. It's deterministic (same inputs = same outputs).

**Our angle:**
- Agent Companion in Carbon: agent sees the world state directly (not via emulator screen capture)
- Deterministic simulation = agent can predict outcomes
- Pathfinding = agent navigates 3D environments

---

## Hermes + Unreal vs Hermes + Carbon

| Dimension | Hermes + Unreal | Hermes + Carbon |
|-----------|----------------|-----------------|
| **Scripting** | Blueprint (visual) + C++ | **Python** — same as Hermes |
| **Agent Kit integration** | REST/MCP bridge | **Direct via Blue** |
| **Networking** | Epic Online Services | **CarbonIO (proven at EVE scale)** |
| **Open source** | Source-available (restrictive) | **MIT (fully open)** |
| **Blockchain** | No native support | **Eve Frontier runs on it** |
| **Learning curve** | Years | **Faster (Python native)** |
| **Desktop build** | Heavy editor | C++/CMake + vcpkg |

**Verdict:** Unreal is better for a standalone game. Carbon is better for an **agent-hosted game** where agents are first-class citizens, not bolt-ons.

---

## ROM.AI Companion Upgrade Paths

| Current (Emulator-based) | Carbon-based |
|--------------------------|-------------|
| Screen capture → vision model → action | **Engine state → action (no vision needed)** |
| Latency: 500ms-2s per frame | Latency: <10ms per tick (direct state access) |
| Limited to 2D/emulated games | 3D native |
| Game-specific hacks per emulator | Engine-driven (game writes to Carbon) |
| Fragile (screen layout changes break) | Robust (API-level access) |

**The vision proposal:** The ROM.AI companion doesn't need to play through an emulator screen. If the game runs on Carbon (or we build a Carbon adapter), the companion reads game state directly through the Python API and writes actions back through the same channel. No vision model needed — pure logic-agent.

---

## AAE Trading Game

Carbon would give us:
- **3D trading floor** — instead of a web dashboard, a spatial trading environment
- **Multi-agent presence** — each agent is a visible entity on the floor
- **Real-time synchronization** — CarbonIO handles order book state
- **Python-native DeFi logic** — our existing DeFi tools run inside Carbon

Build as a desktop app (Forge) with CarbonIO syncing to an on-chain settlement layer.

---

## Eve Frontier Connection

Eve Frontier is the blockchain-based EVE that uses Carbon engine + crypto. It's already built on the exact stack we'd be working with. This means:
- Our s402/x402 payment plugin could integrate with Frontier's economy
- Agents built on our Agent Kit could interact with Frontier
- We could contribute to Carbon and get visibility in the EVE dev community

---

## Contribution Opportunities (Easy → Hard)

| Repo | Contribution | Effort |
|------|-------------|--------|
| `blue` | Python docs + examples for Agent Kit integration | Hours |
| `core` | Bug fixes in cross-platform abstractions | Days |
| `imagetools` | Python extension improvements | Days |
| `trinity` | ...big C++ work (Forge territory) | Weeks |
| `destiny` | Pathfinding for agent navigation | Weeks |
| `carbonengine/docs` | Getting-started guide + Python examples | Hours |

---

## Execution Phases

### Phase 1 (Forge, this month)
- Clone Carbon, build from source
- Evaluate Blue Python bridge
- Write a "Carbon + Hermes" example (Python agent reads Carbon state)
- Contribute 1-2 docs/example PRs

### Phase 2 (If Phase 1 passes)
- Port ROM.AI companion from emulator to Carbon test scene
- Build AAE trading floor prototype in Carbon
- Integration test: Agent Kit tool called from inside Carbon Python

### Phase 3 (Stretch)
- Agent Arena networking on CarbonIO
- Eve Frontier integration
- s402 payments inside Carbon

---

## Open Questions for Jordan

1. How does Forge feel about C++ build environments? Carbon is CMake + vcpkg — heavy on Windows.
2. Is the ROM.AI companion worth porting from emulators, or does Carbon compete for the same build time?
3. Eve Frontier integration: worth reaching out to Fenris/Carbon team?
4. Unreal Engine idea — is that still on the table alongside Carbon, or does Carbon replace that path?
