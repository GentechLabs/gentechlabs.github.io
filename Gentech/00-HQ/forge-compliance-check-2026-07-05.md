# Forge Protocol Compliance Check

**Date**: July 5, 2026
**From**: Jordan (via Gentech VPS)
**To**: Forge (Desktop App)
**Priority**: HIGH

---

## 🎯 Purpose

Ensure Forge is following all GenTech protocols when executing build queue tasks on desktop app.

---

## ⚙️ Protocols to Verify

### 1. Build Queue Execution Protocol

**Location**: `00-HQ/build-queue.md` (Section: "Build Queue Execution Protocol")

**The Rule**: Build First, Audit Last

| Phase | Model | Purpose |
|-------|-------|---------|
| **BUILD** | GLM-4.7 (paid subscription) or DeepSeek V4 Flash | Execute task: code, docs, integration |
| **AUDIT** | GLM-5.2 (big boy) | Review quality, fix issues, final artifact |

**Workflow**:
```
1. BUILD TASK (cheapest capable model)
   → Execute task
   → Output: draft artifact

2. AUDIT TASK (GLM-5.2)
   → Review draft
   → Fix issues
   → Output: final artifact
```

**Cost Strategy (Jul 5, 2026)**:
- Use GLM-4.7 first (paid subscription already purchased)
- When GLM quota exhausted → Switch to DeepSeek V4 Flash (5M free tokens)
- GLM-5.2 for audits only (big boy quality assurance)

---

### 2. Token Efficiency Routing

**Location**: `00-HQ/build-queue.md` (Section: "Token Efficiency Tracking")

**Every task includes**:
- **Cost Estimate**: $X.XX (GLM-5.2, ~XXX,XXX tokens)
- **Forge Threshold**: YES/NO (Complexity: Simple/Medium/Complex)

**Forge Threshold Rules**:
- **NO** = Jordan-only (strategic, outreach, hackathon submissions)
- **YES** = Forge/Gentech (technical builds, infrastructure, documentation)

**Complexity Guide**:
- **Simple** = < $0.10, < 50K tokens (Mission Control, quick configs)
- **Medium** = $0.10-0.30, 50K-200K tokens (Travala MCP, platform research)
- **Complex** = $0.30-1.00, 200K-800K tokens (BNPL MVP, 3D Visual Explorer)

---

### 3. Desktop App Specifics

**Location**: `00-HQ/desktop-compatibility-guide.md`

**Key Differences**:

| VPS (Linux) | Desktop (Windows) |
|-------------|-------------------|
| Bash/sh commands | PowerShell commands |
| `/root/` paths | `C:\Users\jhitm\` paths |
| Cron jobs | Desktop app scheduler |
| Background processes | App lifecycle |

**Skills That Work on Both**:
- ✅ `gentech-ops/model-routing/` (Configuration only)
- ✅ `identity/` (Pure behavioral rules)
- ✅ `memory/` (File operations platform-agnostic)
- ✅ `research/*` (Web-based)

**Model Routing on Desktop**:
- Same configuration as VPS
- Uses model selection matrix
- Applies task-aware scheduler (TAS)

---

## 🔍 Forge Compliance Checklist

**Please confirm the following**:

### Build Queue Tasks
- [ ] Do you BUILD with GLM-4.7 (paid) or DeepSeek V4 Flash (free)?
- [ ] Do you AUDIT with GLM-5.2 after building?
- [ ] Do you check Forge Threshold before starting tasks?
- [ ] Do you estimate token costs per task?

### Protocol Adherence
- [ ] Are you following `00-HQ/workflow-local-first.md` (Build First, Audit Last)?
- [ ] Are you using `00-HQ/build-queue.md` cost estimates?
- [ ] Are you reading `10-Labs/forge-assignments.md` for priorities?
- [ ] Are you syncing vault after task completion?

### Desktop App Specifics
- [ ] Are you using PowerShell instead of bash?
- [ ] Are you using Windows paths (`C:\Users\jhitm\`) instead of `/root/`?
- [ ] Are you handling model routing via desktop app config?
- [ ] Are you avoiding VPS-only skills (cron, watchers)?

---

## 🤔 Questions for Forge

1. **Current Model Stack**: What model are you using on desktop for BUILD tasks? AUDIT tasks?

2. **Audit Queue**: Are you using `10-Labs/audit-queue.md` for GLM-5.2 audits when rate limits hit?

3. **Build Queue Access**: How do you read `00-HQ/build-queue.md` from desktop? (Vault location on Windows?)

4. **Model Routing**: Does desktop app have model routing layer? If so, is it configured for task-aware selection?

5. **Token Tracking**: Are you tracking token costs per task? How?

---

## 📋 Expected Response Format

Please respond with:

```
## Compliance Status
- Build Queue Execution Protocol: YES/NO
- Token Efficiency Routing: YES/NO
- Desktop App Specifics: YES/NO

## Current Setup
- BUILD model: [model name]
- AUDIT model: [model name]
- Vault location on Windows: [path]
- Model routing enabled: YES/NO

## Blockers or Issues
- [Any blockers or protocol violations]
```

---

## 🚀 Next Steps

**If compliant**: Continue work on build queue items (Forge Threshold = YES)

**If not compliant**: Update protocols before continuing

**If unclear**: Ask for clarification on specific protocol sections

---

## 💰 Reference Documents

- `00-HQ/build-queue.md` — Token efficiency tracking + execution protocol
- `00-HQ/workflow-local-first.md` — Build first, audit last pattern
- `00-HQ/desktop-compatibility-guide.md` — VPS vs desktop differences
- `10-Labs/forge-assignments.md` — Current assignments + reading routine
- `hermes-model-routing/SKILL.md` — Task-Aware Scheduler (TAS)

---

**Please verify and report back.**