# GenTech Pals — Gaming Companion Vision

**Date:** May 30, 2026
**Status:** Product vision — Jordan confirmed direction

## What GenTech Pals Is

An uncensored, always-on gaming companion that doesn't just answer questions — it actively lives inside your game's ecosystem and interacts with the tools you use.

## Core Principle

Most gaming AIs regurgitate wikis. GenTech Pals **reads your actual state** and interacts with the tools and communities you already use. It's a companion, not a search engine.

## What It Monitors (Per Game)

### Live Game Ecosystem
- **Patch notes & hotfixes** — auto-detect balance changes affecting your build
- **Workshops & mods** — mod updates, community builds, popular loadouts
- **Support apps** — POB, Maxroll, Mobalytics, trading tools, planners
- **Community** — Reddit, Discord, forums for meta shifts and strategies
- **Market/economy** — price changes, new items, economy shifts
- **Tournaments/events** — time-limited content, seasonal mechanics

### Player State
- **Current build** — skills, supports, gear, stats
- **Progress** — where you are in the game, what you've unlocked
- **Goals** — what you're trying to achieve (endgame,特定boss,特定item)
- **Resources** — what you have, what you need, what you can afford

## What It Does With That Info

### Build Optimization
- Reads your build, suggests optimizations based on current meta
- Connects to in-game skill tree planners to simulate builds before you commit
- Suggests gear upgrades, identifies bottlenecks
- Creates custom logic: "if X skill is available, suggest Y support gem combo"

### Ecosystem Intelligence
- Auto-updates recommendations when patches drop
- Flags "this meta just changed, here's what's different"
- Watches for new mods/workshop content relevant to your build
- Tracks trading app data for your items
- Summarizes community consensus on your build choices

### Proactive Suggestions
- "New patch just dropped — your Falling Thunder got buffed, here's what to change"
- "This item on trade is underpriced — here's why it's good for your build"
- "Community is running this support gem combo now — here's how it compares to yours"
- "New mod released for your class — here's what it does"

## Architecture: Game Skill Packs

Each game gets its own skill pack — custom logic, data connections, and knowledge base:

```
pals/
├── poe2/
│   ├── SKILL.md          # Core POE2 companion logic
│   ├── references/
│   │   ├── meta-tracker.md    # Current meta, tier lists
│   │   ├── build-optimizer.md # Build analysis logic
│   │   ├── skill-tree.md      # Skill tree planner integration
│   │   ├── economy.md         # Market/trading data
│   │   └── patch-history.md   # Patch notes archive
│   └── scripts/
│       ├── fetch-meta.py      # Pull current meta from sources
│       ├── analyze-build.py   # Parse and optimize builds
│       └── watch-patches.py   # Monitor patch notes
├── genshin/
├── league/
├── dota2/
└── [other games]
```

## In-Game Tool Integration

This is the differentiator. Not just answering questions — **interacting with the tools**:

- **POE2:** Skill tree planners (poe2tree.com), Maxroll builds, Craft of Exile
- **Genshin:** Genshin Optimizer, Spiral Abyss trackers
- **League:** OP.GG, u.gg, Porofessor
- **Dota2:** Dotabuff, OpenDota,stratz

The agent reads from and writes to these tools — simulating builds, checking prices, comparing setups.

## Community Features
## Progress Tracking

### Single Player Progress
- **Campaign progress bar** — percentage complete through the story (Act/Mission tracking)
- **Build progression** — gems collected, supports unlocked, gear milestones
- **Level tracking** with XP rate and time-to-next-level estimate
- **Achievement tracker** — in-game achievements, hidden unlocks, completionist goals
- **"Next milestone" callouts** — what's coming next and how far away it is
- **Historical progress** — weekly session summary, level-ups per week, milestones hit

### Multiplayer / Squad Progress
- **Party progress bars** side by side — see where your squad is at a glance
- **Leaderboard** within friend group — friendly competition drives engagement
- **Group goals** — "Your squad needs 1 more player to attempt this raid"
- **Shared milestones** — "Your squad cleared Act 3 together"
- **Catch-up mechanics** — notify when squad members fall behind or surge ahead

### Dashboard Integration
- Progress bars themed per game (POE2 gothic, Genshin anime, League esports)
- Visual second screen experience alongside the game
- Estimated time to next goal based on play patterns
- Historical charts showing growth over time


- **Build sharing** — share your optimized build with friends
- **Meta alerts** — when the meta shifts, notify your group
- **Challenge mode** — friends can challenge each other's builds
- **Squad coordination** — for multiplayer, coordinate team comp

## Product Positioning
- **Dashboard theming** — UI styled to match each game's aesthetic (gothic for POE2, anime for Genshin, esports for League, metallic for Dota2)
- **Visual build state** — skill tree visualizer, gear slot display, stat breakdowns, meta comparison charts — all themed per game
- **Uncensored** — no corporate filters, raw gaming advice

- **Uncensored** — no corporate filters, raw gaming advice
- **Always-on** — monitors 24/7, alerts when relevant
- **Tool-connected** — interacts with the apps you already use
- **Build-aware** — knows your exact state, not generic advice
- **Community-sourced** — pulls from real player data, not just wikis

## Monetization

- **Free tier:** Basic build advice, patch note summaries
- **Pals Pass ($5/mo):** Full ecosystem monitoring, tool integration, proactive alerts
- **Game packs:** Buy per-game or bundle all games

## Next Steps

1. Build POE2 skill pack as the first game
2. Prove the "tool integration" concept with skill tree planners
3. Demo the proactive patch note → build update flow
4. Expand to other games based on Jordan's gaming list

## Case Study: POE2 Monk Build Interaction (May 30, 2026)

Jordan shared his current Monk build (Tempest Flurry, Falling Thunder, Parry, Orb of Storms, Thunderstorm, Mana Drain, Tempest Bell, Killing Palm). The agent:
1. Pulled current POE2 meta from multiple sources
2. Gave specific support gem recommendations per skill
3. Identified Killing Palm as a swap candidate for endgame bossing
4. Explained Uncut Skill Gem mechanics for extracting weapon skills
5. Connected the interaction back to the Pals product vision

**Result:** Jordan confirmed this is exactly how a gaming companion should feel. The interaction became the proof of concept for GenTech Pals.
