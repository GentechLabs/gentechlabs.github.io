# The Workshop

Where the agent grabs its tools each morning.

## Workflow

```
09-Green Room/     → Ideas (unvalidated, exploratory)
11-Mess Hall/      → Considerations (validated, pending decision)
10-Workshop/       → Daily action items delivered by agent
```

## How It Works

Every morning at 7 AM, the agent reviews the Green Room and Mess Hall, then delivers a build list to the Labs channel. The list separates:

- **Autonomous tasks** — things the agent can do right now, no human needed
- **Blocked tasks** — things waiting on Jordan's decision or action
- **Recent progress** — what got done in recent sessions

## Cron Job

- **Schedule:** `0 7 * * *` (7 AM daily)
- **Channel:** Gentech Labs
- **Skill:** `the-workshop` (gentech-ops category)

## For Agent Kit Builders

This workflow is portable. Any Hermes agent with a vault and cron can adopt it:

1. Create your Green Room (ideas backlog) and Mess Hall (decisions backlog)
2. Set up the Workshop cron job (see `the-workshop` skill)
3. Keep your vault files current — the Workshop only works if the backlog is fresh

The name comes from the physical metaphor: you ideate in the green room, debate in the mess hall, then build in the workshop.
