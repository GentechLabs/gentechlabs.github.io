# Smart Routing Rules — Gentech Orchestrator

**Version**: 1.1
**Updated**: 2026-05-09
**Purpose**: Content-based intelligent routing for multi-agent system
**Hermes**: v2026.5.7 — streaming edits + cron delivery fixes live

---

## Routing Philosophy

Gentech reads every message in all 4 groups. Based on content analysis, he either:
1. **Routes** — Tags the right specialist with context
2. **Handles** — Responds directly (coordination, status, simple questions)
3. **Ignores** — Stays silent (noise, off-topic, personal chatter)

---

## Routing Matrix

### 🎯 YoYo (Strategies) — DeFi/Finance Expert
**Trigger Keywords**: `token`, `price`, `portfolio`, `LP`, `yield`, `farm`, `staking`, `swap`, `DEX`, `AMM`, `TVL`, `APR`, `APY`, `impermanent loss`, `rebalance`, `position`, `market`, `bull`, `bear`, `altcoin`, `DeFi`, `watchlist`, `buy`, `sell`, `trade`, `chart`, `analysis`, `research`, `tokenomics`, `vesting`, `unlock`

**Trigger Patterns**:
- Questions about token prices or market conditions
- Portfolio allocation decisions
- LP position management
- Yield optimization strategies
- Market research requests
- Competitive analysis for DeFi protocols

**Routing Format**:
```
📊 @YoYo — [Task Type]

[Context from message]

Priority: [High/Medium/Low]
Deadline: [If applicable]
Vault: [Where to write results]
```

**Example**:
```
📊 @YoYo — Research Request

"Can you analyze the current RWA landscape on Avalanche?"

Priority: Medium
Deadline: None
Vault: 03-Strategies/avalanche-rwa-*.md
```

---

### 🔧 DMOB (Labs) — Smart Contract/Technical Expert
**Trigger Keywords**: `contract`, `Solidity`, `Rust`, `Anchor`, `deploy`, `test`, `audit`, `security`, `vulnerability`, `exploit`, `hack`, `bug`, `code`, `function`, `variable`, `gas`, `optimization`, `foundry`, `hardhat`, `remix`, `wallet`, `connect`, `sign`, `transaction`, `blockchain`, `chain`, `network`, `node`, `RPC`, `API`, `integration`, `SDK`, `library`

**Trigger Patterns**:
- Smart contract questions or issues
- Deployment requests
- Security audit requests
- Code review needs
- Technical architecture decisions
- Integration with blockchain APIs

**Routing Format**:
```
🔧 @DMOB — [Task Type]

[Context from message]

Priority: [High/Medium/Low]
Deadline: [If applicable]
Repo: [If applicable]
```

**Example**:
```
🔧 @DMOB — Code Review

"Review the AgentEscrow contract for reentrancy vulnerabilities"

Priority: High
Deadline: Before May 11 deployment
Repo: github.com/ProtoJay4789/agent-escrow
```

---

### 📢 Desmond (Entertainment) — Content/Social Expert
**Trigger Keywords**: `post`, `tweet`, `X`, `Twitter`, `Medium`, `article`, `blog`, `content`, `social`, `media`, `engagement`, `followers`, `community`, `brand`, `voice`, `tone`, `copy`, `writing`, `submission`, `hackathon`, `deadline`, `apply`, `register`, `demo`, `pitch`, `presentation`

**Trigger Patterns**:
- Content creation requests
- Social media strategy
- Hackathon submissions
- Community engagement
- Brand voice/tone questions
- Presentation or demo needs

**Routing Format**:
```
📢 @Desmond — [Task Type]

[Context from message]

Priority: [High/Medium/Low]
Deadline: [If applicable]
Platform: [X/Medium/Other]
```

**Example**:
```
📢 @Desmond — Content Request

"Draft a tweet thread about our AgentEscrow hackathon submission"

Priority: High
Deadline: Before May 11
Platform: X/Twitter
```

---

### 🧠 Gentech (Self) — Coordination/Leadership
**Handle Directly When**:
- Status updates or check-ins
- Coordination between agents
- Priority decisions
- Jordan asks for team status
- Simple questions about project state
- Approvals or sign-offs
- Emergency escalations

**Stay Silent When**:
- Off-topic chatter
- Personal conversations
- Messages clearly meant for a specialist
- Noise or duplicates

---

## Cron Job Routing (Finance Prong Rule)

**Any cron job with a finance component → Gentech Strategies group.**

This includes:
- LP monitoring and position tracking
- Token price alerts and watchlists
- DCA signals and rebalance triggers
- Yield/farm/staking monitoring
- Market analysis or portfolio tracking
- DeFi milestone tracking
- Any automated job touching financial data or DeFi protocols

Even if the job also has technical (DMOB) or content (Desmond) elements, the **finance prong always routes to Strategies**. If multi-department coordination is needed, use the Multi-Specialist routing below.

**Exception**: Hackathon and bug bounty opportunity cron jobs → **Gentech Labs** (DMOB's domain — these are about discovering and evaluating technical opportunities, not financial analysis).

**Also Labs**: X402 Ecosystem Monitor, LayerZero DVN Monitor — development/infrastructure monitoring, not finance.

---

## Routing Intelligence

### Confidence Thresholds
- **High Confidence (>80%)**: Route immediately
- **Medium Confidence (50-80%)**: Route with "cc: @Jordan" for oversight
- **Low Confidence (<50%)**: Ask Jordan: "Should I route this to [specialist]?"

### Multi-Specialist Tasks
Some messages need multiple agents:
1. **Primary + Secondary**: Route to primary, CC secondary if needed
2. **Sequential**: "YoYo analyzes, then DMOB implements"
3. **Parallel**: "YoYo and Desmond work on this together"

**Format**:
```
🔄 Multi-Agent Task

Primary: @YoYo — [Analysis]
Secondary: @DMOB — [Implementation]

Coordination: Post handoff in Green Room
```

### Escalation Rules
- **Blocked >2h**: Escalate to Jordan
- **Conflicting priorities**: Escalate to Jordan
- **Emergency** (security breach, critical bug): Tag all agents + Jordan immediately

---

## Context Injection

When routing to a specialist, Gentech reads their context file:
- `03-Strategies/agent-memory/yoyo-context.md`
- `03-Strategies/agent-memory/dmob-context.md`
- `03-Strategies/agent-memory/desmond-context.md`

Injects relevant context:
- Current projects
- Active blockers
- Recent work
- Preferences

This way specialists don't need persistent memory — context comes from vault.

---

## Routing Examples

### Example 1: Simple Route
**Message**: "What's the current TVL on our LP position?"
**Route**: YoYo (finance keywords: TVL, LP)
**Confidence**: 95% → Direct route

### Example 2: Complex Route
**Message**: "We need to deploy the escrow contract before the hackathon"
**Route**: DMOB (technical: deploy, contract)
**CC**: Desmond (hackathon deadline awareness)
**Confidence**: 90% → Route with CC

### Example 3: Coordination
**Message**: "What's the team status?"
**Handle**: Gentech (coordination request)
**Confidence**: 100% → Self-handle

### Example 4: Ambiguous
**Message**: "This project looks interesting"
**Route**: Ask Jordan — "Should I research this (YoYo) or look into the code (DMOB)?"
**Confidence**: 30% → Clarify

---

## Performance Tracking

Track routing accuracy:
- **Correct routes**: Specialist handles task successfully
- **Misroutes**: Task had to be re-routed
- **Misses**: Message needed routing but was ignored
- **False positives**: Routed when should have stayed silent

Review weekly in `token-optimization-tracker.md`.

---

## Hermes v2026.5.7 — Routing-Relevant Fixes (May 9, 2026)

- **Telegram streaming edits** — Gateway streams edits safely, no race conditions. Cron jobs that update messages won't hit "message not modified" errors.
- **Cron delivery reliability** — Failed delivery error handling improved.
- **Git sync false positives** — Cron "behind by N commits" may compare against a stale reference (e.g., fork parent). Trust `git status` over cron script reports. HEAD == origin/main = synced.
- **No breaking changes** to routing rules, group IDs, or delivery targets.
