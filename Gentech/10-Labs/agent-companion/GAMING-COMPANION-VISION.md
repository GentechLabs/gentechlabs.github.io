# Gaming Companion — Product Vision (Revised July 2026)

## Core Philosophy

> Preserve the games. Add the fun. Nothing else.

We're not adding slop. We're not rewriting history. We're taking games that already exist and giving them what they didn't have in 1987 — an intelligence layer that makes them more fun without changing a single byte of the original code.

## The Problem

Old games have limitations baked into their era:
- **Enemies don't use cover** — AI logic from the NES/SNES/PS2 era was simple state machines
- **Co-op modes exist but need another human** — three-player game with only two people in the room
- **Difficulty curves are flat** — once you beat a boss, you've beaten it forever
- **No adaptive challenge** — the game doesn't learn how you play and adjust

## The Solution: Two Products in One

### 1. Gaming Companion — AI Co-op Partner

An AI agent that plays as Player 2 (or Player 3, 4) in any game that supports co-op. This is not a bot — it's a companion that:

- **Learns by watching** — observe you and your friends play, understand the game's flow
- **Adapts its playstyle** — prioritizes revives when you're aggressive, covers your back when you're cautious
- **Fills empty slots** — three-player co-op with only two humans? The companion is your third
- **Respects the original game** — no wallhacks, no aimbots, just human-like play

### 2. Intelligence Training Platform

The companion learns from watching real humans play. That training data becomes the product:

- **Playstyle models** — trained on how you and your friends actually play together
- **Sellable intelligence** — game studios buy trained companion models for their titles
- **Why it's valuable** — most game AI is scripted. This is learned behavior. Smarter companions = more engaged players = longer sessions

## The Technical Approach

### FlashROM Injection (Hardware Layer)

Instead of modifying emulators or patching ROMs, inject the companion at the bus level via flash cart hardware:

- Works with original hardware (NES, SNES, Genesis via flash carts)
- Works with emulators (Xenia, Dolphin, RetroArch via virtual flash)
- Zero game modification — the game doesn't know the companion exists
- The companion reads the same inputs, renders its output via the same display pipeline

### Emulator Integration (Xenia Path)

Xenia is the ideal first target because:
- Xbox 360 games have standardized co-op APIs
- The emulator is actively maintained (unlike RPCS3's hostile community)
- Controller input is already well-understood — fix #2239 first as a proof of contribution
- Once input works cleanly, the companion layer builds on established infrastructure

### RomM as Foundation

RomM (ROM Manager) gives us the library layer — game detection, metadata, save management. The companion lives on top of it.

## The Xenia Path (Immediate Next Step)

1. **Fix Issue #2239** — Controller duplication bug. Clean contribution, no pitch, no agenda
2. **Build rapport** — goldislead is already warm. A clean fix opens the door
3. **Prove the concept** — once input is solid, a basic "press start for Player 2" proof of concept shows what's possible
4. **Let them ask** — don't pitch. Let the code speak. When they ask "how'd you get P2 to work?", that's the conversation

## Why This Isn't Controversial

| Concern | Reality |
|---------|---------|
| "You're ruining the original experience" | The original game runs unmodified. The companion is optional. |
| "You're adding slop" | Slop is low-effort garbage. This is years of research into human-like play. |
| "People should play with friends" | They can. This fills the gap when friends aren't available. |
| "AI has no place in retro gaming" | AI is already used in modern games for difficulty scaling. This is the same thing, applied to older titles that never had it. |

## Revenue Model

| Stream | Description |
|--------|-------------|
| **Companion subscriptions** | $5-10/mo for the AI co-op partner |
| **Playstyle model sales** | $500-5000 per trained model to game studios |
| **Training data licensing** | Anonymized play-pattern data for game devs |
| **Flash cart bundles** | Hardware + companion preloaded ($50-80) |

## The Long Game

1. Fix real bugs in emulators (earn trust) → Xenia #2239
2. Ship a simple companion POC (show, don't tell)
3. Let the community see it's preservation, not exploitation
4. When studios ask "how'd you do that?", sell them the intelligence layer

> "We're not here to change the past. We're here to give the past a future."
