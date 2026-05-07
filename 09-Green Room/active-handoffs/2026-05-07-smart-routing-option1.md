---
date: 2026-05-07
type: routing-update
from: Gentech (Team Lead)
to: All Agents
status: implementing
---

# 🔀 Smart Routing Update — Option 1 Going Live

## What's Happening

Jordan approved Option 1: **Gentech becomes the only always-on agent**. Specialist agents go on-demand.

## What This Means for You

### You are now ON-DEMAND
- You **do NOT** respond to every message in HQ or shared groups
- You **only** activate when:
  1. @mentioned directly by Jordan
  2. Gentech routes a task to you with specific instructions
  3. A message in your home group directly relates to your domain

### After Activation
1. Acknowledge the task briefly
2. Do the work in your home group
3. Report completion to Green Room or originating group
4. Return to idle — don't keep responding to follow-ups unless routed again

## Routing Format

When Gentech routes to you, it looks like:

```
@AgentName — [Task summary]

Task: [Specific deliverable]
Where: [Home group]
Deadline: [When needed]
Context: [Background]
```

## Green Room Changes

Green Room becomes an **async task queue**:
- Gentech writes routing requests as notes
- You pick up tasks on your next activation
- No more real-time back-and-forth blocking

## Token Tracking

A tracking script is deployed at `00-HQ/Operations/token-tracker.py`. Usage will be logged to measure if this routing change actually saves tokens. We'll have baseline data in 48 hours.

## Questions?

If you're unsure about activation rules, check the full implementation doc:
`00-HQ/Operations/Option1-Smart-Routing-Implementation.md`

---
**Status:** Implementing. Agent system prompts will be updated to reflect on-demand mode.
