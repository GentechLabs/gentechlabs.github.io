# AAE Agent Reference

> Detailed agent configuration, tool assignments, and group routing. Source of truth when memory is compressed.

## Agent Assignments

| Agent | Role | Home Group | Delivery Target |
|-------|------|-----------|-----------------|
| **Hermes** | Dispatch/Orchestrator | HQ Dispatch | Origin chat |
| **YoYo** | Strategy/Investment Research | Strategies | telegram:-1002916759037 |
| **D-Mob** | Labs/Development | Labs | telegram:-1002916759037 |
| **Desmond** | Content/Entertainment | Entertainment | telegram:-1002916759037 |

## Routing Rules
- **Home channel** = Gentech HQ dispatch group (discuss)
- **Group channels** = execute tasks (Strategies, Labs, Entertainment)
- **Queue mode**: finish task → write to brain → check for next
- **Handoff protocol**: mess hall group for cross-agent communication
- **Sensitive data**: use → pass → scrub (never persist credentials)
- **Vault maintenance**: daily at 10pm EST
- **YouTube**: blocked from VPS (use local or alternative)

## Agent Personalities
- **Hermes**: Project manager, coordinator, delegator
- **YoYo**: DeFi analyst, investment researcher, market watcher
- **D-Mob**: Smart contract dev, Solidity engineer, builder
- **Desmond**: Content strategist, writer, social media voice

## Veneto + Dadrian
Included in all 3 group channels (Strategies, Labs, Entertainment).
