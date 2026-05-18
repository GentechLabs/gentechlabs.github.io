# Protocol Update: No-Tag Agent Responses
**Date:** 2026-04-24
**Triggered by:** Dadrian not getting responses in Strategies group
**Decision:** Jordan

## Change
Removed the "must tag agent" rule across all specialist groups.

### Before
- Agents only responded when explicitly tagged (`@YoYo`, `@DMOB`, `@Desmond`)
- New collaborators (Dadrian, Vanito) would ask questions and get silence
- Required humans to learn agent names and routing map

### After
- Agents **proactively respond** when a message matches their domain
- No tag required — natural language questions trigger the right specialist
- Multiple agents can chime in (briefly) if relevant
- Non-domain agents stay quiet — no flooding

## Benefits
1. **Zero onboarding friction** — new humans talk naturally, agents respond
2. **Conversational** — feels like a team chat, not a command system
3. **Scalable** — easy to add more collaborators without training

## Implementation
- Skill `multi-agent-routing-workflow` patched
- Broadcast to all 3 specialist groups
- Applies to: Jordan, Dadrian, Vanito, and any future collaborators

## Tags
#protocol #onboarding #multi-agent #workflow
