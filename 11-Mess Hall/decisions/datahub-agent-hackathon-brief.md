# Decision Brief — DataHub Agent Hackathon (Queue #30)

**Prepared:** Nightly Build Session, Jul 31 2026 (autonomous)
**Decision needed from Jordan:** go / no-go + Devpost registration

## Verified facts (devpost.com + datahub.com, Jul 31)
- **Prize pool: $20,500** (queue entry said "0,500" — corrupted, now fixed)
  - Grand Prize: $6,000 + DataHub Town Hall presentation + LinkedIn badge
  - Challenge Winners: $3,000 × 4 (one per category)
  - Honourable Mention: $1,000 × 2
  - Feedback survey: $50 × 10 (individual, mutually exclusive with other prizes)
- **Deadline: Aug 10, 2026, 5:00pm EDT** — 10 days out
- **2,277 participants registered** — crowded, but 7 cash slots
- Kicked off Jul 6; we'd be entering at week 4 of 5

## Categories
1. Agents That Do Real Work
2. Metadata-Aware Code Generation
3. Resilient AI Systems
4. Open / Wildcard

## Why it fits us
- We already run MCP servers in production — DataHub's entry point is its MCP Server
- x402 gateway gives a differentiator no metadata-graph entrant will have: **pay-per-query context**
- "Resilient AI Systems" maps directly onto our cron truth-layer / stateful-alert patterns

## Recommended angle if GO
**Category: Agents That Do Real Work.** An agent that reads the DataHub context graph over MCP, detects stale/orphaned datasets, and bills per-audit via x402. Reuses existing gateway — mostly config + one MCP client.

## Effort estimate
2–3 focused build sessions. Realistic in 10 days *only* if started this weekend.

## What blocks us
1. Jordan registers at https://datahub.devpost.com (individual/team entrant must be a human)
2. Go/no-go — competes for the same weekend as arcade production deploy (#4)

## Recommendation
**GO, but only if #4 arcade deploy slips a week.** Both in the same window means neither ships well.
