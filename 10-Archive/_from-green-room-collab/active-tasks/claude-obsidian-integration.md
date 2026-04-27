# Claude-Obsidian Integration Research

**Requested by:** Jordan
**Assigned to:** Dmob
**Date:** 2026-04-17

## Task
Research how to integrate [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) into our existing setup while keeping what we already have (Second Brain, green room, mess hall, agent states, nightly maintenance cron).

## What claude-obsidian offers
- Persistent, compounding knowledge base backed by Claude
- Autonomous research → structured Obsidian notes
- Multi-agent support with wiki modes (Academic, GitHub, Business, Research, etc.)
- Automated vault maintenance (broken links, gap filling)
- MCP support — Claude reads/writes directly to local vault
- Visual canvas integration (knowledge graphs)
- 1.5k stars, active dev (last commit Apr 13)

## What we already have
- Group structure: HQ, Strategies, Labs, Entertainment
- Second Brain: green room (perspectives), mess hall (coordination), agent states
- Nightly vault maintenance cron (job 6c44744fb3b8)
- Proactive handoff behavior
- Distinct agent voices

## Key questions
1. Can we install as a Claude Code plugin alongside existing skills?
2. Does their vault maintenance conflict with our cron job?
3. Can wiki modes map to our group structure?
4. Is MCP integration compatible with our Hermes setup?
5. What's the install path — separate vault or merge into existing?

## Repo
- https://github.com/AgriciDaniel/claude-obsidian
- Clone: `git clone https://github.com/AgriciDaniel/claude-obsidian.git`
- Three install options: pre-configured vault, Claude Code plugin, add to existing vault
