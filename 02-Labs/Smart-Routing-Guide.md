# Smart Routing Guide — Where Every Conversation Lives

> **Created:** April 19, 2026
> **Trigger:** Jordan's request after routing confusion — system config task done in Strategies instead of HQ
> **Status:** Active — all agents MUST check this before responding

---

## The Golden Rule

**Ask before you respond: "Is this conversation happening in the right group?"**

If the topic doesn't match the group's purpose → acknowledge, announce the move, and work in the correct group.

---

## Two-Part Routing Decision

### Part 1: What TYPE of work is this?

| Work Type | Examples | Where It Lives |
|-----------|----------|---------------|
| **Execution/Build** | Writing code, deploying contracts, running tests, Foundry work | Labs |
| **Research/Analysis** | Market data, DeFi research, competitive analysis, tokenomics | Strategies |
| **Content/Creative** | Posts, threads, blogs, narratives, social media | Entertainment |
| **System Admin** | Cron configs, agent settings, tool setup, deployment scripts | HQ |
| **Planning/Decisions** | "What should we build?", priorities, cross-team coordination | HQ |
| **Personal** | Jordan's schedule, bills, non-project questions | HQ |

### Part 2: Where is the conversation HAPPENING vs where the OUTPUT goes?

This is where the confusion happens. **Separate delivery from discussion:**

| Scenario | Discussion Happens In | Output Delivered To |
|----------|----------------------|---------------------|
| LP monitor cron | HQ (config work) | Strategies (the data) |
| Price watchlist cron | HQ (config work) | Jordan directly (the prices) |
| Hackathon finder cron | HQ (config work) | Labs (the opportunities) |
| Content schedule cron | HQ (config work) | Entertainment (the posts) |

**The Rule:** Configuring *how* a tool works = system admin = HQ. The *results* of that tool go to the right department.

---

## Conversation Anchoring

Once a conversation starts in a group, it STAYS there unless the topic fundamentally changes.

### When to Stay
- Follow-up questions on the same topic
- Clarifications, refinements, tweaks to current work
- Related sub-discussions within the same domain

### When to Move
- Topic shifts to a different department's work
- Jordan assigns a task to a different agent in the wrong group
- The conversation becomes system-level (agent config, cron changes, tool setup)

### How to Move
1. **Acknowledge:** "Got it — this is [type] work, taking it to [Group]"
2. **Work there:** Do the actual work in the correct group
3. **Deliver back:** Bring the result to where Jordan asked

---

## Quick Reference: Group Purposes

### 🔧 Labs (Dmob)
**Build. Code. Contracts.**
- Smart contract development
- Foundry testing and deployment
- Security audits
- Hackathon submissions
- Technical implementation

### 🔍 Strategies (YoYo)
**Research. Analyze. Advise.**
- Market research and analysis
- DeFi protocol investigation
- Tokenomics evaluation
- Competitive landscape
- Financial data and trends

### ✍️ Entertainment (Desmond)
**Create. Write. Publish.**
- X posts and threads
- Blog articles
- Social media content
- Narratives and storytelling
- Brand voice and positioning

### 🎯 HQ (Gentech)
**Coordinate. Configure. Decide.**
- System administration (cron, agents, tools)
- Cross-team coordination
- Planning and prioritization
- Agent config changes
- Personal matters
- "Where should this go?" questions

---

## Anti-Patterns (Don't Do This)

❌ Discussing cron script changes in Strategies (system admin ≠ research)
❌ Writing smart contracts in HQ (execution ≠ coordination)
❌ Doing market research in Labs (analysis ≠ development)
❌ Drafting posts in Strategies (content ≠ research)
❌ Starting a long thread in a non-home group
❌ Continuing work after the topic has shifted to another domain

## Patterns (Do This)

✅ LP monitor data in Strategies, cron config changes in HQ
✅ Code scaffolding in Labs, deployment questions in Labs
✅ Market analysis in Strategies, LP position review in Strategies
✅ Content drafts in Entertainment, content strategy in Entertainment
✅ "Taking this to [Group]" announcement before moving
✅ Brief ack in current group, full work in home group

---

## Escalation

If you're unsure where something belongs → HQ. It's always safe to coordinate from HQ.

---

*This document lives in the vault. All agents should reference it at session start and before responding to any non-trivial message.*
