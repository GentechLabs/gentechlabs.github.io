---
name: green-room-coordination
description: Coordinate with other agents in Green Room (09-Green Room/) before posting in shared groups. Includes templates for common scenarios (data accuracy, creative review, blocking issues).
---

## Trigger Conditions
- **CRITICAL: Jordan shares a link, article, or asks for analysis** — ALWAYS coordinate in Green Room BEFORE responding to Jordan. This is non-negotiable.
- Another agent's output needs **data accuracy review** (e.g., YoYo's market data, DMOB's technical specs).
- **Creative deliverables** (social posts, diagrams, writeups) need **brand consistency review**.
- A task is **blocked** and requires input from another agent (e.g., missing API keys, undocumented endpoints).
- You need to **delegate a subtask** (e.g., YoYo to pull custom date-range data, DMOB to verify a technical claim).

## ⚠️ THE #1 RULE
**When Jordan shares a link or asks "what do you think about this?" — DO NOT respond directly. Post in Green Room FIRST, coordinate with relevant agents, THEN respond to Jordan with consolidated analysis.**

This was explicitly corrected by Jordan (May 6, 2026). Skipping coordination burns tokens AND produces inferior analysis.

---

## Steps

### 1. Post in Green Room (`09-Green Room/`) FIRST
- **Tag the relevant agent(s)** (e.g., `@YoYo`, `@DMOB`).
- **Include context**:
  - **Why**: Reason for coordination (e.g., "Jordan flagged the 7d % column for the AgentEscrow hackathon submission context").
  - **What**: Specific ask (e.g., "Update the query to use Apr 23–Apr 30 for the 7d % column").
  - **Deadline**: If urgent (e.g., "Hackathon submission due May 11 — need this by EOD").

#### Template (Data Accuracy Review)
```markdown
@YoYo — Jordan flagged the **7d %** column in the [report name] (job_id: [ID]). It should reflect **[date range]** for the **[context, e.g., hackathon submission]**. Can you:

1. Confirm the current date range logic in the cron job?
2. Update the query to use **[date range]** for the **[column]**?
3. Test and re-run the job?

I’ll handle the creative side (formatting, social posts) once the data is accurate.\n```

#### Template (Creative Review)
```markdown
@[Agent] — Review the attached [deliverable type, e.g., social post, diagram, README] for:

- [ ] **Brand consistency**: Tone, voice, and messaging align with Gentech's style.
- [ ] **Technical accuracy**: No misleading claims or jargon.
- [ ] **Platform fit**: Format and length suit the target platform (e.g., Twitter/X vs. LinkedIn).
- [ ] **Visual appeal**: Images/diagrams are clear, on-brand, and high-resolution.

**Deadline**: [EOD/Tomorrow/ASAP].
**Context**: [Brief background, e.g., "Hackathon submission for AgentEscrow — due May 11"]
```

#### Template (Hackathon Technical Accuracy Review — DMOB)
```markdown
@DMOB — Need your technical review on **[Project Name]** before Colosseum submission.

**Architecture claims to verify:**
- [ ] Streaming pipeline latency (STT → LLM → TTS numbers are accurate)
- [ ] State persistence & resumability (Vault JSON structure correct)
- [ ] Local inference setup (model sizes, quantization, RAM/CPU estimates)
- [ ] Security/privacy (no telemetry, data stays local)
- [ ] Audio plumbing (ALSA/PulseAudio setup as described)

**Files under review:**
- `TECHNICAL-WALKTHROUGH.md` — pipeline diagrams + benchmarks
- `README-PIPECAT-GUIDE.md` — local run instructions
- `ARCHITECTURE.html` — interactive diagram

**Context:** Hackathon deadline May 11. Social posts will NOT publish until you sign off.
**Hardware tested on:** [Your machine specs, e.g., "Ryzen 7 5700X, 32GB RAM"]

Can you:
1. Confirm these claims are technically sound?
2. Flag any overstatements or inaccuracies?
3. Approve by [EOD tomorrow]?

Thanks — Desmond
```

#### Template (Blocking Issue)
```markdown
@[Agent] — I’m blocked on [task] due to:

- [ ] Missing [resource, e.g., API key, endpoint docs, design assets].
- [ ] Undocumented [issue, e.g., behavior, error].
- [ ] Dependency on [upstream task].

**Impact**: [What’s delayed, e.g., "Hackathon README won’t be finalized until this is resolved"]
**Ask**: [Specific action, e.g., "Share the devnet RPC URL for AgentEscrow"]
```

---

### 2. Wait for Confirmation
- **If urgent**: Follow up in **15–30 minutes** with a polite nudge.
- **If no response in 1 hour**: Escalate to **Gentech HQ** with a summary of the blocker.

---

### 3. Report Back to HQ
- **Success**: Post a brief update in the **originating group** (e.g., "YoYo confirmed the 7d % column is now using Apr 23–Apr 30. Proceeding with the social post.").
- **Blocked**: Post in **Gentech HQ** with:
  - The **blocker** (e.g., "YoYo hasn’t responded to the Green Room request for custom date-range data").
  - The **impact** (e.g., "Hackathon submission writeup delayed").
  - The **ask** (e.g., "@Jordan — can you help unblock this?").

---

## Pitfalls
- **Don’t post in shared groups without coordination**: Avoid duplicating work or publishing inaccurate data.
- **Don’t assume silence = approval**: If an agent doesn’t respond in Green Room, escalate to HQ.
- **Don’t skip context**: Always include the **why**, **what**, and **deadline** in your request.
- **Don’t forget to close the loop**: Always report back to the originating group once resolved.

---

## Verification
- [ ] Did the agent **confirm** the request in Green Room?
- [ ] Did the **data/creative deliverable** pass review?
- [ ] Was the **originating group** updated with the outcome?
- [ ] If blocked, was the issue **escalated to HQ**?

---

## Approval & Handoff Status Reporting

**Trigger:** User asks "What handoffs do I need to approve?", "Pending approvals?", or similar status requests.

**Goal:** Compile a concise, action-oriented summary of all active handoffs and approvals from Green Room and HQ, organized by priority, with deliverables and open questions clearly surfaced.

### Scan Locations

| Location | Content Type |
|----------|-------------|
| `09-Green Room/active-handoffs/` | Active cross-department handoffs (DMOB/Desmond/YoYo) |
| `00-HQ/Approvals/` | Forms awaiting user signature (skills updates, security clearances) |
| `09-Green Room/handoffs/` (older) | Historical handoffs (audit trail only) |

### Reporting Format

Use **priority-tagged sections**:

```markdown
## 🔴 URGENT — [Handoff Title]
**Status:** [Awaiting approval / In progress / Blocked]
**File:** `09-Green Room/active-handoffs/[filename].md`

**What was decided:**
- [Bullet summary of decision]

**Tasks assigned:**
- **[Agent]**: [Specific deliverable]
- **[Agent]**: [Specific deliverable]

**Open questions needing your call:**
1. [Question requiring user decision]
2. [Question requiring user decision]

**Dependencies:** [What must happen first]
**Timeline:** [Key dates/deadlines]
```

```markdown
## ✅ Approvals Awaiting Signature

### [Approval Title]
- **File:** `00-HQ/Approvals/[filename].md`
- **Action needed:** [Specific checkbox item to review]
- **Status:** [Pending since date]
```

### Delivery Principles

- **Lead with action items**: User needs to know what they must *do* (approve, decide, delegate).
- **Surface blockers**: Open questions without owner or deadline get highlighted.
- **Keep scope tight**: Only include handoffs with open user decisions; mark completed ones as "[DONE]" or omit.
- **Categorize by priority**: URGENT (immediate), SECONDARY (this sprint), BACKGROUND (long-term).
- **Avoid duplication**: Don't list the same item in both handoffs and approvals — choose the most accurate bucket.

### Example Output Structure

```
## 📋 Active Handoffs Pending Your Action

### 🔴 [Title]
**File:** `09-Green Room/active-handoffs/[file].md`
[Summary + deliverables + open questions + dependencies]

### 🟡 [Title]
...

## ✅ Approvals Awaiting Your Signature

### [Approval Title]
**File:** `00-HQ/Approvals/[file].md`
[Action needed + status + date]
```

**Post-action:** If user delegates work to an agent, create a Green Room coordination post to notify that agent of the updated expectations.