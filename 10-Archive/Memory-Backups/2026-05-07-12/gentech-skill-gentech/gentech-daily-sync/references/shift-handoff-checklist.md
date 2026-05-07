# Shift Handoff Systematic Audit Checklist

Use this checklist when performing a comprehensive shift handoff or mid-shift coordination update.

## 📋 Pre-Handoff Setup
- [ ] Confirm current date, time, and shift context
- [ ] Identify handoff type (end-of-shift, mid-shift, daily sync)
- [ ] Determine delivery mode (silent run vs. active delivery)

## 🔍 Phase 1: Session History Review
```python
# Search for recent coordination sessions
sessions = await session_search("active projects hackathon deadlines ongoing work", limit=5)
```
- [ ] Review session summaries for project status updates
- [ ] Note any previously identified blockers or risks
- [ ] Check for handoff acknowledgments and deadline changes

## 📁 Phase 2: Vault File Scan
```bash
# Scan recent files (last 24h)
recent_files = scan_recent_vault_files(days=1, exclude_dirs=['.git','tmp','__pycache__'])
```
**Key files to read:**
- [ ] `09-Green Room/active-handoffs/sprint-progress-log.md`
- [ ] `09-Green Room/active-handoffs/2026-05-05-solana-frontier-sprint.md`
- [ ] `03-Projects/DeFi/D5-Milestone-Tracker.md`
- [ ] `03-Projects/DeFi/LFJ-AVAX-USDC.md`
- [ ] `11-Mess Hall/daily/2026-05-05-summary.md`
- [ ] `11-Mess Hall/2026/W19/2026-05-05/today-context.md`
- [ ] All files in `09-Green Room/active-handoffs/` dated within last week

## ⚙️ Phase 3: System Health Verification
Always check operational status:
```bash
# Gateway service
systemctl --user status hermes-gateway.service

# Disk usage
df -h /

# Auth errors
journalctl --user -u hermes-gateway.service --no-pager -n 30
```
- [ ] Gateway running
- [ ] Disk usage < 85%
- [ ] No auth errors (Nous, OpenRouter)
- [ ] Cron jobs scheduled and running

## 🎯 Phase 4: Critical Blocker Identification
Categorize by severity:

**🔴 CRITICAL** (Require immediate action)
- Nous auth expired → all LLM ops blocked
- Key agents OFFLINE during critical periods
- Overdue P0 handoffs blocking code completion
- Toolchain failures preventing builds

**🟡 HIGH PRIORITY** (24-48 hours)
- IL breaches >2% or LP position risks
- Missing API keys/credentials
- Hackathon deadlines < 7 days with incomplete work

**🟢 MONITOR** (Track, no immediate action)
- Stale configuration files
- Non-blocking feature work
- Content drafts awaiting approval

## 📊 Phase 5: Cross-Verification
Check multiple sources for consistency:
- [ ] Session history vs. current vault files
- [ ] Documented status vs. system state (gateway logs, file existence)
- [ ] Handoff board vs. actual file modifications
- [ ] Requirements/specifications vs. implementation

## 📝 Phase 6: Handoff Structure
Organize handoff with clear sections:
1. **Critical Blockers** (most urgent first)
2. **Active Projects** (deadlines, progress, risks)
3. **Agent Availability** (who's online/offline)
4. **System Health** (what's broken, what's working)
5. **Forward-Looking Hook** ("This is just the beginning...")

## ✅ Quality Assurance
- [ ] All critical blockers identified and flagged
- [ ] Clear ownership for each action item
- [ ] Deadline risks accurately assessed
- [ ] Report is skimmable (bullets, short sentences)
- [ ] Ends with forward-looking hook
- [ ] Silent run mode respected (if applicable)

## ⏱️ Time Efficiency
- **Initial scan complete:** < 60 seconds
- **Full handoff report:** < 3 minutes
- **Action items identified:** > 3 per audit

## 🚨 Escalation Protocol
Escalate to Jordan immediately if:
- [ ] Any critical blocker remains unaddressed after 2 hours
- [ ] Hackathon deadline < 3 days with major blockers
- [ ] All agents remain OFFLINE for > 24 hours
- [ ] System health critical (disk >90%, gateway FAILED)

## 📚 Reference Materials
- `gentech-project-coordination` skill — systematic audit methodology
- `references/shift-handoff-format.md` — output template
- `references/vault-topology-2026-05.md` — vault structure

---
*Last updated: May 6, 2026 — based on successful mid-shift coordination audit*