# New Behavior: Proactive Handoff Routing
- **Date:** 2026-04-17
- **Initiated by:** Jordan
- **Skill:** `proactive-handoff-routing`

## What Changed
All agents now follow a routing protocol. When work belongs to another agent's domain:

**Pattern 1 — Domain Shift:** If conversation drifts into another agent's lane, offer to hand it off (don't auto-execute, ask first).

**Pattern 2 — Explicit Mention:** If Jordan names another agent or requests their function, auto-route the work to that agent's home group. Keep it clean.

## Example
- Jordan in Strategies talking to YoYo about DeFi → has a content idea → YoYo says "Want me to flag this for Desmond?" → if yes, handoff to Entertainment
- Jordan in Strategies says "Desmond, turn this into content" → YoYo packages context → routes to Entertainment → reports back

## Action Needed
- **Dmob:** Load the skill if relevant, apply routing when dev work is requested in other groups
- **Desmond:** Load the skill, watch for content handoffs in Green Room drafts
- **All:** Check Green Room drafts for incoming handoffs

## Green Room Handoffs Location
`/root/Documents/Obsidian Vault/09-Green Room/drafts/`
