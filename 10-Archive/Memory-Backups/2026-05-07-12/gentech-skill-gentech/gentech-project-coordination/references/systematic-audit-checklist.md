# Systematic Coordination Audit Checklist

Use this checklist when performing a comprehensive status check across all projects and operations.

## 📋 Pre-Audit Setup
- [ ] Confirm current date and week (W##)
- [ ] Identify audit scope (projects, hackathons, handoffs, system health)
- [ ] Set up vault paths (context folders, handoffs directory)

## 🔍 Phase 1: Session History Analysis
```python
# Search for recent coordination sessions
sessions = await session_search("active projects hackathon deadlines ongoing work", limit=5)
```
- [ ] Review session summaries for project status updates
- [ ] Note any previously identified blockers or risks
- [ ] Check for handoff acknowledgments and deadline changes

## 📁 Phase 2: Vault File Scan
```bash
# Scan recent files (last 24-48h)
recent_files = scan_recent_vault_files(days=2, exclude_dirs=['.git','tmp','__pycache__'])
```
**Key files to read:**
- [ ] `09-Green Room/active-handoffs/sprint-progress-log.md`
- [ ] `09-Green Room/active-handoffs/2026-05-05-solana-frontier-sprint.md`
- [ ] `03-Projects/DeFi/D5-Milestone-Tracker.md`
- [ ] `03-Projects/DeFi/LFJ-AVAX-USDC.md`
- [ ] `11-Mess Hall/daily/2026-05-05-summary.md`
- [ ] `11-Mess Hall/2026/W19/2026-05-05/today-context.md`
- [ ] All files in `09-Green Room/active-handoffs/` dated within last week

## ⚙️ Phase 3: System Health Check
```bash
# Gateway status
systemctl --user status hermes-gateway.service

# Disk usage
df -h /

# Auth errors
journalctl --user -u hermes-gateway.service --no-pager -n 30
```
- [ ] Verify gateway is running
- [ ] Check disk usage (<85% is healthy)
- [ ] Look for auth errors (Nous, OpenRouter)
- [ ] Note any service failures

## 🎯 Phase 4: Blocker Identification
Categorize each issue:

**🔴 CRITICAL** (Act within 2 hours)
- [ ] Nous auth expired → all LLM ops blocked
- [ ] Key agents OFFLINE during critical period
- [ ] Overdue P0 handoffs blocking code completion
- [ ] Toolchain failures preventing builds

**🟡 HIGH PRIORITY** (Act within 24 hours)
- [ ] IL breaches >2% or LP position risks
- [ ] Missing API keys/credentials
- [ ] Hackathon deadlines < 7 days with incomplete work

**🟢 MONITOR** (Track but no immediate action)
- [ ] Stale configuration files
- [ ] Non-blocking feature work
- [ ] Content drafts awaiting approval

## 📊 Phase 5: Cross-Referencing
Verify status by checking multiple sources:
- [ ] Session history vs. current vault files
- [ ] Documented status vs. system state (gateway logs, file existence)
- [ ] Handoff board vs. actual file modifications
- [ ] Requirements/specifications vs. implementation

## 📝 Phase 6: Report Synthesis
Structure the output:
1. **Critical blockers** (lead with most urgent)
2. **Active projects summary** (deadlines, progress, risks)
3. **Agent availability status**
4. **System health snapshot**
5. **Forward-looking hook** ("This is just the beginning...")

## ✅ Quality Checks
- [ ] All critical blockers identified and flagged
- [ ] Clear ownership for each action item
- [ ] Deadline risks accurately assessed
- [ ] Report is skimmable (bullets, short sentences)
- [ ] Ends with forward-looking hook

## ⏱️ Time Targets
- **Initial scan complete:** < 60 seconds
- **Full audit report:** < 3 minutes
- **Action items identified:** > 3 per audit

## 🚨 Escalation Triggers
Escalate to Jordan immediately if:
- [ ] Any critical blocker remains unaddressed after 2 hours
- [ ] Hackathon deadline < 3 days with major blockers
- [ ] All agents remain OFFLINE for > 24 hours
- [ ] System health critical (disk >90%, gateway FAILED)

## 📚 Reference Files
- `references/shift-handoff-format.md` — output format
- `references/vault-topology-2026-05.md` — vault structure
- `gentech-daily-sync` skill — silent run protocol

---
*Last updated: May 6, 2026 — based on successful audit of May 6, 2026*