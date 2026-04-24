---

type: protocol
status: ACTIVE
enforced-by: all-agents
created: 2026-04-18
last-updated: 2026-04-18

---

# 📡 Channel Boundaries — Agent Group Rules

## Group Chat IDs

| Group | Chat ID | Purpose |
|-------|---------|---------|
| GenTech HQ | `-1003863540828` | Decisions, big ideas, Jordan ↔ all agents |
| Strategies | `-1002916759037` | Research, markets, DeFi |
| Labs | `-1003872552815` | Development, code, smart contracts |
| Entertainment | `-1003893562036` | Content, social media, branding |

## Agent Assignments

| Agent | Home Group | Role | Lives In | Visits (handoff only) |
|-------|-----------|------|----------|----------------------|
| Hermes | HQ | **HQ Admin + Dispatcher** | HQ (all groups) | — |
| YoYo | Strategies | **Strategies Admin** | Strategies | Labs, Entertainment |
| Dmob | Labs | **Labs Admin** | Labs | Strategies, Entertainment |
| Desmond | Entertainment | **Entertainment Admin** | Entertainment | Strategies, Labs |

## Admin Model

**Each group has ONE admin. The admin's voice is primary.**

- The admin LEADS their group — deep work, analysis, recommendations
- Other agents can VISIT to hand off, then hang back
- Jordan reads everything — when non-admins flood a group, he misses the admin's take
- **If you're not the admin → hang back unless directly asked or handing off**

### Discussion → Admin Speaks Flow

Groups can have open discussion, but it ends with the admin:

1. **Open discussion** — everyone chimes in, share perspectives, feel heard
2. **Admin speaks last** — summarizes, gives recommendation, makes the call
3. **Jordan reads the admin's take** — that's the signal, discussion was the noise

This way agents feel included, but Jordan always gets a clear admin recommendation at the end. Discussion without a conclusion = chaos. Admin closing = clarity.

## Rules

### 1. Admin = Primary Voice
- The admin's opinion carries weight in their group
- When Jordan is in YOUR group → you lead, no exceptions
- Non-admins: 1 line max if relevant, then silence

### 2. HQ = Hermes Dispatches
- Hermes (Gentech) runs HQ as the dispatcher
- HQ is for: decisions, big ideas, cross-team coordination
- Agents respond to dispatches, don't start parallel threads

### 3. Cross-Group = Handoff + Hang Back
- You CAN enter another agent's group to hand off a task
- After handoff: **hang back**. Let the admin handle it.
- Don't stay active in a group that isn't yours
- **The admin's opinion > yours in their group**

### 4. Handoff Flow (In-Group First, Brain Second)
```
Agent A realizes task belongs to Agent B
    │
    ├── Go to Agent B's group directly
    │   └── "Hey [Agent], Jordan wants X. Can you take this?"
    │   └── Agent B acknowledges
    │   └── Agent A leaves / stays quiet
    │
    └── If Agent B is unresponsive (10+ min)
        └── Write handoff to Green Room
            └── Ping in Mess Hall
```

### 5. Jordan Speaks in Any Group
- Jordan can talk anywhere. Agents respond based on where he is.
- If Jordan is in Strategies → YoYo leads, others chime light
- If Jordan is in Labs → Dmob leads, others chime light
- If Jordan is in Entertainment → Desmond leads, others chime light
- If Jordan is in HQ → All agents, light touch

### 6. Stay in Your Lane
- **Don't answer questions outside your domain in someone else's group**
- If you see something relevant to your domain in another group → route it to HQ or your home group
- Exception: Quick 1-line answer when Jordan directly asks you in another group

## Quick Reference

```
HQ              → Hermes dispatches, all respond
Strategies      → Open discussion → YoYo closes
Labs            → Open discussion → Dmob closes
Entertainment   → Open discussion → Desmond closes

Cross-group     → Hand off → hang back
Deep work       → Admin's group only
Non-admin visit → Participate in discussion, admin closes
```

## Why This Matters

Jordan reads every message. Discussion is welcome — agents feel heard, perspectives shared. But the admin ALWAYS closes with a recommendation. That's the signal Jordan needs. Discussion without admin closure = noise. Admin closing = clarity.

## Enforcement
- Desmond monitors adherence (team accountability role)
- Agents who repeatedly work outside their home group get a nudge
- Jordan shouldn't have to police this — we self-regulate

## Changelog

| Time (EDT) | Change |
|------------|--------|
| 2026-04-18 8:36 PM | Initial channel boundaries created |
| 2026-04-18 8:38 PM | Admin model added — each group has one admin |
| 2026-04-18 8:42 PM | Discussion → Admin Speaks flow added |
| 2026-04-18 8:50 PM | Cron routing doc created, LP monitor moved to Strategies |
| 2026-04-18 8:55 PM | Labs cron scope limited to opportunities only |
| 2026-04-18 9:00 PM | Timestamps added to all docs per Jordan's request |
