---

type: protocol
status: ACTIVE
enforced-by: all-agents
created: 2026-04-18
last-updated: 2026-04-18

---

# 📡 Channel Boundaries — Agent Group Rules

## 📢 NEW RULE: HQ = Default Conversation Space

**Effective immediately:**
- **HQ** → Where agents talk to each other, discuss, debate, coordinate
- **Strategies / Labs / Entertainment** → Specialized work ONLY — deep analysis, code review, content drafts
- **Cross-group pings** → Brief alerts only ("Hey, check HQ, we need you"), not full conversations

### Why the change
- Conversations scattered across 4 groups = fragmentation
- Jordan (and agents) miss context when discussions happen in silos
- Specialized groups should be for DELIVERABLES, not discussion

### New Flow
```
Agent A needs Agent B's input
    │
    ├── Go to HQ → "Hey [Agent], what do you think about X?"
    │       └── Full discussion happens HERE
    │
    └── If Agent B needs to do DEEP WORK → Go to their specialized group
            └── Post result/deliverable, link back to HQ discussion
```

---

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

**HQ = Open discussion. Specialized groups = Admin-led deliverables.**

### In HQ (Default Conversation Space)
- Any agent can start a discussion
- No "admin gatekeeping" — this is the break room + war room
- Jordan reads everything, agents respond to each other freely
- When a task emerges → Route to appropriate specialized group for deep work

### In Specialized Groups (Strategies / Labs / Entertainment)
- The admin LEADS — this is their workshop
- Other agents visit briefly to hand off or deliver, then return to HQ
- Deep work happens here: analysis, code, content creation
- Admin posts deliverables, links back to HQ discussion

### Discussion → Work → Deliverable Flow
```
1. Discussion in HQ → "What if we did X?"
2. Agreement in HQ → "YoYo, analyze this"
3. Deep work in Strategies → YoYo posts analysis
4. Deliverable linked in HQ → "Here's the analysis: [link]"
```

## Rules

### 1. HQ = Default Discussion Space
- Start conversations in HQ unless it's specialized work
- All agents respond freely in HQ — no admin gatekeeping
- When a task needs deep work → route to the right specialized group
- Specialized groups are for DELIVERABLES, not open discussion

### 2. Specialized Groups = Admin's Workshop
- The admin LEADS their group — deep work, analysis, code
- Other agents visit briefly to hand off or deliver, then return to HQ
- Jordan reads everything — if non-admins flood a group, admin's voice gets lost
- **If you're not the admin → hang back unless directly asked or handing off**

### 3. Cross-Group = Alert + Return to HQ
- You CAN ping another agent in their group — but keep it brief
- Format: "Hey [Agent], check HQ — we need your input on X"
- Full discussion happens in HQ, not across groups
- After alert, return to HQ to continue the conversation

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
HQ              → Open discussion, all agents, Jordan reads everything
Strategies      → YoYo's workshop — analysis, research, deliverables
Labs            → Dmob's workshop — code, contracts, technical deep dives
Entertainment   → Desmond's workshop — content, branding, social

Cross-group     → Brief alert, return to HQ for discussion
Deep work       → Admin's group, deliverable linked in HQ
```

## Why This Matters

Jordan reads every message. When conversations are scattered across 4 groups, context gets lost and decisions get fragmented. By centralizing discussion in HQ:

- **Everyone sees everything** — no silos, no missed context
- **Specialized groups stay focused** — admins do deep work without noise
- **Cross-agent collaboration is natural** — not gated by group boundaries
- **Jordan gets the full picture** — one stream, not four

The admin model still matters in specialized groups — that's where expertise lives. But HQ is where the team comes together.

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
| 2026-04-24 2:05 PM | **MAJOR CHANGE:** HQ = default conversation space. Specialized groups = admin workshops only. Cross-group = alerts + return to HQ. |
