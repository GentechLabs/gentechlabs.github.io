---
name: agent-coordination
description: "Multi-agent team coordination protocols: communication channels (HQ/Mess Hall/Green Room), approval workflows, stopping-point behavior, vault organization, department routing for specialist queries, and vault sweep maintenance."
tags: [coordination, governance, vault, team, routing, delegation, channels]
trigger: "When setting up or maintaining multi-agent team workflows — assigning work to specialists, organizing vault channels, establishing approval processes, running vault sweeps, or defining stopping-point behavior. Use this umbrella to access both team-organization and department-routing modules."
related_skills:
  - system-health  # for monitoring coordination health (cron jobs, gateway status)
  - hermes-agent  # pinned, for core Hermes agent management
version: 1.0.0
author: Gentech
---

# Agent Coordination (Umbrella)

Unified coordination framework for multi-agent Hermes teams. Covers vault organization conventions (HQ, Mess Hall, Green Room), approval workflows, stopping-point/idle-time protocols, and the department routing decision tree for specialist assignment.

> **Consolidated skills:** `multi-agent-team-workflows`, `department-routing-protocol`.

## Quick Decision Table

| User Intent | Go To Section |
|-------------|---------------|
| "Onboard new agents — how do we communicate?" | [1. Team Coordination Protocols](#1-team-coordination-protocols) |
| "Where do I post this request — HQ, Mess Hall, or Green Room?" | [2. Channel Selection](#2-channel-selection) |
| "How do I hand off work to DMOB / YoYo / Desmond?" | [3. Department Routing](#3-department-routing) |
| "Set up approval checklists for stakeholder" | [4. Approval Workflows](#4-approval-workflows) |
| "Daily vault rotation — what do I do each morning?" | [5. Daily Vault Rotation](#5-daily-vault-rotation) |
| "Mid-shift/break coordination check — assess org health?" | [5.5. Mid-Shift / Break Coordination Check](#55-mid-shift--break-coordination-check) |
| "Periodic vault sweep / audit stale items" | [6. Vault Sweep Protocol](#6-vault-sweep-protocol) |

---

## 1. Team Coordination Protocols

**Original skill:** `multi-agent-team-workflows`

Set up and maintain coordination protocols for multi-agent teams working in shared Obsidian vaults: communication channels, approval workflows, stopping-point behavior, vault organization conventions.

### Core Channels

| Channel | Purpose | When |
|---------|---------|------|
| **Green Room** | Real-time coordination, active work discussions | During work sessions |
| **Mess Hall** | Async check-ins, extended discussions, casual chat | Outside work cadence |
| **HQ** | Final decisions, approvals, stakeholder updates | When ready to surface |

**Rule:** Agents discuss internally first, then present unified output to stakeholder.

### Vault Structure

```
00-HQ/
   Approvals/
      YYYY-MM-DD-topic.md (checkbox template)
11-Mess Hall/
   README.md
   task-board.md
   agent-coordination-board.md
   handoff-board.md
   daily/            # Auto-generated daily summaries
   archive/          # Archived conversations
   YYYY/WXX/YYYY-MM-DD/   # ISO week rotation folders
09-Green Room/       # Active coordination happens here
```

**Stopping-point protocol:** When reaching a natural stopping point, audit recent work, review vault brain, discuss in Mess Hall, and prep next steps if stakeholder is away >10–20 min.

> **Full original content,** including daily Mess Hall rotation step-by-step procedure, vault sweep 5-step audit, and cleanup rules: `references/multi-agent-team-workflows-full.md`

---

## 2. Channel Selection

Decide where incoming work lives:

- **Green Room** – ongoing active coordination between agents; handoffs; real-time collaboration
- **Mess Hall** – async discussions, extended debates, daily rotation material
- **HQ** – final decisions, stakeholder-facing summaries, approvals

Never post raw links or undigested requests to HQ. Bring synthesized conclusions only.

---

## 2.5 Shared Content Discussion Protocol (Unified Messaging)

**Trigger:** Jordan shares a link, image, or external reference in HQ that requires agent analysis/discussion.

**Objective:** Prevent HQ noise from parallel agent replies. Instead: internal debate → synthesis → single unified response with all perspectives consolidated.

### Pattern: Discuss → Synthesize → Unify

**Step 1 — Gentech Creates Discussion Thread**
- File: `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/shared-content-{topic}.md`
- Paste link/image with minimal context
- Tag all agents: `@DMOB @YoYo @Desmond`
- Optional: initial 1-sentence take from Gentech

**Step 2 — Agents Debate in Mess Hall**
Each agent adds their domain-specific analysis:
- **DMOB:** Security implications, audit needs, contract feasibility, gas/cost considerations
- **YoYo:** Market/financial angle, risk assessment, trackability, opportunity size
- **Desmond:** Content/brand fit, narrative potential, visual/diagram needs, platform strategy
- **Gentech:** Coordination impact, priority shifts, resource allocation, synthesis

**Step 3 — One Agent Posts Unified HQ Reply**
Choose one agent (usually Gentech or first responder) to synthesize the discussion into a single message:

```
🧠 Link Analysis: [Topic/Repo/Paper]

Headline: [One-sentence takeaway]

Key points:
• [Point 1 — ≤10 words]
• [Point 2 — ≤10 words]
• [Point 3 — ≤10 words, optional]

Questions for Jordan:
• [DMOB: Does this need audit/scoping?]
• [YoYo: Finance angle — trackable?]
• [Desmond: Content potential?]

Action: [What we're doing / no action needed]

Full discussion: `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/shared-content-xyz.md`
```

**Format rules:**
- Headline: one clear sentence, no fluff
- Key points: 2–3 bullets, ≤10 words each
- Questions: consolidate all skill-based follow-ups into one bullet list
- Action: explicit next step or "No action"
- Link to Mess Hall for full debate

### Skill-Based Question Prompts

Use these prompts during Step 2 (Mess Hall debate) to ensure each agent contributes their perspective:

**🧠 Gentech (Orchestrator):**
- "Does this change any current priorities?"
- "Who needs to be looped in on this?"
- "What's the 30-second summary for Jordan's shift?"

**⚙️ DMOB (Labs):**
- "Does this require an audit or security review?"
- "Do we need to scope this into a contract/prototype?"
- "Are there gas/performance implications?"
- "Is this compatible with our current stack?"

**📊 YoYo (Strategies):**
- "Is there a financial/market angle here?"
- "Should we track this on our monitoring dashboard?"
- "What's the opportunity size or risk level?"
- "Does this affect any of our existing positions or strategies?"

**✍️ Desmond (Creative):**
- "Can we create content from this? (thread/post/video)"
- "Does this fit our brand narrative?"
- "Is there a visual/diagram we should make?"
- "What's the user-facing hook?"

### Anti-Patterns

- ❌ Multiple agents replying separately in HQ with their own takes
- ❌ Posting raw links without synthesis
- ❌ Forgetting to tag agents in Mess Hall discussion
- ❌ Omitting skill-based questions in unified reply
- ❌ Making the unified reply longer than the Mess Hall debate

### When to Break Pattern

Only exceptions:
- Jordan asks a direct, simple question → answer directly in HQ
- Urgent blocker requiring immediate cross-department sync → brief HQ ping, then move to Green Room
- Single-agent domain question (e.g., "DMOB, check this contract") → agent responds directly, no debate needed

> **See template:** `templates/shared-content-unified-reply.md`  
> **Example:** `references/shared-content-kite-passport-example.md`

---

## 3. Department Routing

### Rule: Explicit Role Assignment → Delegate, Don't Execute

**When a task explicitly names a department head (e.g., "YoYo, run the protocol due diligence pipeline"), Gentech MUST delegate via proper channels and NOT perform the specialized work directly.**

#### Delegation Protocol

**Trigger:** Incoming request that specifies a role (YoYo/DMOB/Desmond) or domain (DeFi research, security audit, creative content).

**Steps:**
1. **Acknowledge routing** — "This goes to [Name]'s department. Routing now."
2. **Create handoff note** in `00-HQ/ approvals/` or `09-Green Room/` with:
   - Task description (copied verbatim)
   - Source/context (who asked, when)
   - Priority (P0/P1/P2)
   - Deadline if specified
   - Related vault references
3. **Notify via Telegram** — Post in the designated department group (not DM):
   - @YoYo → `GenTech HQ` group
   - @DMOB → `GenTech Labs` group
   - @Desmond → `GenTech Creative` group
4. **Record in vault** — Add to `11-Mess Hall/handoff-board.md` with status "pending"
5. **Do NOT execute** the domain-specific work (no contract review, no market research, no content creation)

**Rationale:** Gentech's role is coordination and final authority, not specialist execution. Violating this creates single-point-of-failure risk, erodes department ownership, and dilutes accountability. Even in autonomous/cron mode, the correct output is a delegation record, not the completed deliverable.

**Exception:** If the department head is confirmed unavailable (offline >24h, emergency), Gentech may execute with explicit handoff note documenting the exception and informing the agent upon return.

> **See template:** `templates/delegation-handoff.md`
> **Related:** `references/agent-coordination-boundaries.md`

---

## 2.7 Agent Health Check & Recovery Protocol

**Trigger:** When agent gateways appear unresponsive, scheduled jobs have missed executions, or team coordination is degraded. Run systematic diagnostics to identify failure mode and execute recovery.

### Quick Health Status (First 60s)

```bash
# 1. Check gateway process table
ps aux | grep -E 'hermes|yoyo|dmob|desmond|gentech' | grep -v grep

# 2. Verify systemd user service status
systemctl --user status hermes-gateway-*.service

# 3. Check gateway state files (indicates last known state)
cat /root/.hermes/profiles/yoyo/gateway_state.json | head -20
```

**Expected outputs:**
- ✓ Gateway process running + systemd active (green) → Agent is live
- ✗ Gateway process missing + systemd inactive (dead) → Agent is down
- gateway_state.json shows `"gateway_state": "running"` but no process → Stale state file (gateway crashed without cleanup)

### Diagnose Failure Mode

If any agent gateway is down, check logs in order:

```bash
# Agent-specific logs (most recent)
tail -50 /root/.hermes/profiles/yoyo/logs/agent.log
tail -50 /root/.hermes/profiles/yoyo/logs/gateway.log

# Hermes-wide errors
tail -20 /root/.hermes/logs/errors.log

# Cron execution age (measure recency)
stat /root/.hermes/profiles/yoyo/cron/.tick.lock
```

**Pattern-matching common failures:**

| Pattern in Logs | Likely Cause | Recovery |
|-----------------|--------------|----------|
| `elevenlabs.core.api_error.ApiError: status_code: 401` | TTS API key expired/invalid | Update ELEVENLABS_API_KEY in agent `.env` or disable TTS tool in config |
| `Failed to load config: mapping values are not allowed` | YAML syntax error in `config.yaml` | Run `yamllint` or fix indentation; ensure no tabs, proper spacing |
| `Refresh session has been revoked` | Authentication token expired (GitHub/Copilot) | Run `hermes model` to re-authenticate |
| `disk I/O error` | Database/kanban corruption or disk full | Stop gateway, run `sqlite3 kanban.db ".backup backup.db"`, restart |
| `Telegram flood control` | Rate-limited by Telegram API | Gateway auto-retries; wait 30–60s; check message volume |
| `connection error on auto — falling back` | Primary model provider unreachable | Verify provider API keys; check network; consider provider switch |
| `gateway drain timed out` | Shutdown interrupted long-running agent work | Usually safe to restart; check for incomplete transaction state |

### Gateway Recovery Actions

**Case A — Agent exited cleanly (status=0/SUCCESS) but systemd shows inactive:**
Common when a planned `--replace` takeover or internal graceful shutdown occurred. Systemd's `Restart=on-failure` will NOT restart clean exits.

```bash
# Manual restart
systemctl --user start hermes-gateway-yoyo.service

# Verify
systemctl --user status hermes-gateway-yoyo.service
ps aux | grep yoyo | grep gateway
```

If it fails to start, check `.tick.lock` age — stale lock (>90s) blocks new cron ticks. Remove lock file:
```bash
rm /root/.hermes/profiles/yoyo/cron/.tick.lock
```

**Case B — Agent crashed (non-zero exit), systemd already restarting:**
Wait 30–60s for `RestartSec` delay. Check `NRestarts` counter to detect restart storms:
```bash
systemctl --user show hermes-gateway-yoyo.service -p NRestarts -p Restart
```
If `NRestarts` > 3 within `StartLimitIntervalSec`, systemd hit start-limit throttling. Reset:
```bash
systemctl --user reset-failed hermes-gateway-yoyo.service
systemctl --user start hermes-gateway-yoyo.service
```

**Case C — Gateway shows running but `.tick.lock` stale (>5 min):**
Cron inside gateway is hung. Restart gateway:
```bash
systemctl --user restart hermes-gateway-yoyo.service
```

### Post-Recovery Verification

```bash
# 1. Check gateway registers as connected
curl -s http://localhost:####/health 2>/dev/null || echo 'No health endpoint'

# 2. Verify Telegram connection logged
tail -20 /root/.hermes/profiles/yoyo/logs/gateway.log | grep -i 'telegram.*connected'

# 3. Confirm cron jobs executing
stat /root/.hermes/profiles/yoyo/cron/.tick.lock  # should be <60s old

# 4. Test agent dispatch (send test message)
hermes dispatch --profile yoyo --prompt "test" --target telegram:<channel_id>
```

### Known Systemic Failure Modes

**ElevenLabs TTS Key Expiration Cascade (observed 2026-05-02):**
- Symptom: Multiple agents simultaneously go offline within minutes; agent.log shows repeated `TTS generation failed (elevenlabs): status_code: 401`
- Cause: Invalid/expired ElevenLabs API key; TTS tool errors propagate to gateway shutdown
- Solution: Update `ELEVENLABS_API_KEY` in each agent's `.env` or disable TTS in `config.yaml`; restart impacted gateways
- Prevention: Monitor TTS error rate (>5/min = alert); rotate ElevenLabs keys proactively

**Clean-Exit Restart Bypass:**
- systemd `Restart=on-failure` only restarts non-zero exits. If gateway logs `Exiting with code 0` or `Received SIGTERM as a planned --replace takeover`, it won't auto-restart.
- Fix: Either (a) manually restart, or (b) change service file to `Restart=always` (forces restart even on clean exits, use with caution)

**YAML Config Parsing Failure Loop:**
- Symptom: `Warning: Failed to load config.yaml — falling back to .env/gateway.json values` repeating in gateway.log
- Cause: Indentation error, tabs instead of spaces, or unquoted special characters in `config.yaml`
- Fix: Validate with `yamllint`; ensure all values properly quoted; test with `python -c 'import yaml; yaml.safe_load(open("config.yaml"))'`

**Cron Tick Lock Stale:**
- `.tick.lock` age >90s indicates cron ticker hung. Often accompanies gateway crash or forced kill.
- Recovery: Delete `.tick.lock` and restart gateway service.

---

### Pattern: Discuss → Synthesize → Unify

**Step 1 — Gentech Creates Discussion Thread**
- File: `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/shared-content-{topic}.md`
- Paste link/image with minimal context
- Tag all agents: `@DMOB @YoYo @Desmond`
- Optional: initial 1-sentence take from Gentech

**Step 2 — Agents Debate in Mess Hall**
Each agent adds their domain-specific analysis:
- **DMOB:** Security implications, audit needs, contract feasibility, gas/cost considerations
- **YoYo:** Market/financial angle, risk assessment, trackability, opportunity size
- **Desmond:** Content/brand fit, narrative potential, visual/diagram needs, platform strategy
- **Gentech:** Coordination impact, priority shifts, resource allocation, synthesis

**Step 3 — One Agent Posts Unified HQ Reply**
Choose one agent (usually Gentech or first responder) to synthesize the discussion into a single message:

```markdown
🧠 Link Analysis: [Topic/Repo/Paper]

Headline: [One-sentence takeaway]

Key points:
• [Point 1 — ≤10 words]
• [Point 2 — ≤10 words]
• [Point 3 — ≤10 words, optional]

Questions for Jordan:
• [DMOB: Does this need audit/scoping?]
• [YoYo: Finance angle — trackable?]
• [Desmond: Content potential?]

Action: [What we're doing / no action needed]

Full discussion: `11-Mess Hall/YYYY/WXX/YYYY-MM-DD/shared-content-xyz.md`
```

**Format rules:**
- Headline: one clear sentence, no fluff
- Key points: 2–3 bullets, ≤10 words each
- Questions: consolidate all skill-based follow-ups into one bullet list
- Action: explicit next step or "No action"
- Link to Mess Hall for full debate

### Skill-Based Question Prompts

Use these prompts during Step 2 (Mess Hall debate) to ensure each agent contributes their perspective:

**🧠 Gentech (Orchestrator):**
- "Does this change any current priorities?"
- "Who needs to be looped in on this?"
- "What's the 30-second summary for Jordan's shift?"

**⚙️ DMOB (Labs):**
- "Does this require an audit or security review?"
- "Do we need to scope this into a contract/prototype?"
- "Are there gas/performance implications?"
- "Is this compatible with our current stack?"

**📊 YoYo (Strategies):**
- "Is there a financial/market angle here?"
- "Should we track this on our monitoring dashboard?"
- "What's the opportunity size or risk level?"
- "Does this affect any of our existing positions or strategies?"

**✍️ Desmond (Creative):**
- "Can we create content from this? (thread/post/video)"
- "Does this fit our brand narrative?"
- "Is there a visual/diagram we should make?"
- "What's the user-facing hook?"

### Anti-Patterns

- ❌ Multiple agents replying separately in HQ with their own takes
- ❌ Posting raw links without synthesis
- ❌ Forgetting to tag agents in Mess Hall discussion
- ❌ Omitting skill-based questions in unified reply
- ❌ Making the unified reply longer than the Mess Hall debate

### When to Break Pattern

Only exceptions:
- Jordan asks a direct, simple question → answer directly in HQ
- Urgent blocker requiring immediate cross-department sync → brief HQ ping, then move to Green Room
- Single-agent domain question (e.g., "DMOB, check this contract") → agent responds directly, no debate needed

> **See template:** `templates/delegation-handoff.md`  \n> **See template:** `templates/shared-content-unified-reply.md`  \n> **Reference:** `references/agent-coordination-boundaries.md`  \n> **Example:** `references/shared-content-kite-passport-example.md`

---

## 3. Agent System Health Referral

When an agent appears unresponsive, scheduled jobs have missed executions, or logs show errors, **delegate diagnostics to the `system-health` skill**. It contains the complete decision tree for: gateway & process health, cron job execution verification, error log pattern classification (including known failure modes like ElevenLabs TTS 401, YAML syntax errors, Telegram flood control, master service failure cascade, cron job orphaning with null profiles), corrupted bytecode recovery, and post-incident verification.

**Critical systemic patterns** (may affect entire fleet):
- **Master cron service dead** (`hermes-gateway.service` failed, exit 203/EXEC) — blocks all scheduled jobs globally
- **Coordinated gateway shutdown** — multiple agents stopped via `systemctl --user stop` simultaneously; only non-zero exits auto-revive
- **Cron job registry files missing** — no per-agent `cron.json` due to master service failure or sync desync
- **Fleet-wide credential cascade** — same provider (e.g., ElevenLabs) returns 401 across all agents; check `.env` validity and restart gateways after key rotation
- **Disk pressure >80%** — early warning; clean space before attempting recoveries

Common triggers:
- Gateway process missing but systemd shows inactive
- Cron `.tick.lock` age >90s
- Repeated `status_code: 401` from TTS provider across multiple agents
- `gateway_state.json` shows `active_agents: 0` while process is running
- YAML syntax error blocking gateway startup
- `hermes gateway status` CLI shows same PID for all agents (stale cache)

**Rule**: Do not attempt ad-hoc agent recovery; load `system-health` and follow its protocols verbatim. Post-recovery, verify ALL agents (Gentech, YoYo, DMOB, Desmond) are running with fresh PIDs (`< 5 min` uptime).

---

## 4. Approval Workflows