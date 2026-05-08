---
name: gentech-project-coordination
version: 1.0
class: gentech
scope: Systematic project status retrieval, analysis, and coordination
effort: 2
provides: project-status-audit
description: Orchestrates project status checks, gap analysis, and team coordination for Gentech projects
---

# Gentech Project Coordination

Orchestrates project status checks, gap analysis, and team coordination. This skill embeds the workflow for retrieving context from session history, analyzing current file states, identifying discrepancies against requirements, and proposing concrete next actions.

## When to Use

- User asks "Where are we with X?"
- Need to retrieve project context from past sessions
- Assessing current state against a specification or requirements
- Planning next steps after a pause or interruption
- Preparing status updates for stakeholders

## Workflow

### 1. Context Retrieval (Session Search)
```python
# Search for relevant project sessions
search_query = f"{project_keywords}"
sessions = await session_search(search_query, limit=5)
```

### 2. Current State Analysis
- Read relevant files from vault
- Parse structure and content
- Identify key sections and data
- Compare against requirements or spec

### 3. Gap Analysis
- List what's already completed (✅)
- Identify what needs update (🔄)
- Note what's missing or broken (⚠️)
- Flag any inconsistencies

### 4. Action Plan Formulation
- Prioritize updates (critical vs. nice-to-have)
- Identify dependencies (team members, tools)
- Propose concrete next steps
- Estimate effort and blockers

### 5. Coordination & Handoff
- Present findings clearly to user
- Delegate to appropriate team members if needed
- Set up follow-up actions
- Document in vault if appropriate

## Systematic Coordination Audit

When the user requests a comprehensive status check across all active projects, hackathons, and ongoing work (like this session), follow this structured audit methodology:

### 1. **Multi-Source Context Gathering**
```python
# A. Search recent coordination sessions
sessions = await session_search("active projects hackathon deadlines ongoing work", limit=5)

# B. Scan vault for recent activity (last 24-48h)
recent_files = scan_recent_vault_files(days=2, exclude_dirs=['.git','tmp','__pycache__'])

# C. Read key project files
key_files = [
    '/root/vaults/gentech/09-Green Room/active-handoffs/sprint-progress-log.md',
    '/root/vaults/gentech/03-Projects/DeFi/D5-Milestone-Tracker.md',
    '/root/vaults/gentech/03-Projects/DeFi/LFJ-AVAX-USDC.md',
    '/root/vaults/gentech/00-HQ/Usage/*.md'
]
```

### 2. **System Health Verification**
Always check the operational status of the Hermes platform:
```bash
# Gateway service status
systemctl --user status hermes-gateway.service

# Disk usage (critical for file integrity)
df -h /

# Recent auth errors from logs
journalctl --user -u hermes-gateway.service --no-pager -n 30
```

### 3. **Blocker Identification Framework**
Categorize issues by severity and type:

**🔴 CRITICAL** (Immediate action needed)
- Nous authentication expired → all LLM operations blocked
- Key agents OFFLINE during hackathon crunch
- Overdue P0 handoffs blocking code completion
- Toolchain failures (Rust version mismatch, missing devnet SOL)

**🟡 HIGH PRIORITY**
- IL breaches or LP position risks
- Missing API keys (OpenRouter, etc.)
- Deadline < 7 days with incomplete work

**🟢 MONITOR**
- Stale configuration files
- Non-blocking feature work
- Social content drafts awaiting approval

### 4. **Cross-Referencing Technique**
Verify status claims by checking multiple sources:
- **Session history** → what was planned
- **Vault files** → what is documented
- **System state** → what is actually running
- **Handoff board** → task ownership and deadlines

### 5. **Synthesis & Reporting**
Structure the output as a CEO-level briefing:
- Lead with critical blockers and urgent items
- Summarize active projects with clear deadlines
- Highlight agent availability issues
- End with forward-looking hook ("This is just the beginning...")

### Pitfalls to Avoid
- **Don't trust status messages at face value** — verify by reading actual files and checking system state
- **Don't skip system health checks** — auth issues and disk pressure can cripple operations
- **Don't bury the lede** — critical blockers belong at the top
- **Don't forget handoffs** — overdue handoffs are often the hidden blockers

### Success Metrics
- Time from request to comprehensive report < 3 minutes
- All critical blockers identified and flagged
- Clear ownership for each action item
- Accurate assessment of deadline risk
```

### 1. Structural Scan
```bash
# Map vault top-level folders
find /root/vaults/gentech -maxdepth 2 -type d | grep -v '.git' | grep -v 'Archive' | sort
# Find key files in each domain
find /root/vaults/gentech/00-HQ -name "*.md"
find /root/vaults/gentech/03-Projects -name "*.md" -maxdepth 2
find /root/vaults/gentech/02-Labs/Hackathons -name "*.md"
```

### 2. Read These Files (Priority Order)
- `03-Projects/HACKATHON-ROSTER-2026.md` — active hackathon status
- `03-Projects/DeFi/D5-Milestone-Tracker.md` — LP position health
- `03-Projects/AAE/agent-economy-vision.md` — strategic thesis
- `00-HQ/Competitive-Landscape-AgentPayments.md` — competitive positioning
- `11-Mess Hall/2026/W<current>/today-context.md` — today's flags and agenda
- `02-Labs/Hackathons/Active/*.md` — hackathon submission status

### 3. Synthesis Format (CEO Briefing)
Use this structure — it's conversational, not a status report:

```
## The Big Picture
[1-2 sentences: where we are in the timeline]

## 🔥 [Domain 1]
[What matters, what's at risk, what's working]

## 💡 What I'm Most Excited About
[Strategic insight or thesis that's strong]

## 🔧 Infrastructure & Ops
[Broken things, quick wins, blockers]

## 💡 My Recommendations
[Prioritized, actionable, numbered]
```

### 4. Tone Rules
- **"We're building"** not "They're building" — CEO wants to feel the team
- **Be honest about gaps** — don't sugarcoat out-of-range positions or overdue handoffs
- **End with forward-looking hooks** — "This is just the beginning..."
- **Match the user's energy** — "chop it up" = casual warmth, not corporate deck

### Pitfalls
- **Don't just list files** — synthesize. The CEO can read the vault; they want your analysis.
- **Don't skip the bad news** — out-of-range LP positions, overdue handoffs, offline agents. Surface them.
- **Don't make it too long** — 3-5 sections max. Scannable. Bold headers.

---

## Key Techniques

### Session Search Optimization
- Use specific keywords related to the project
- Limit to recent sessions (last 2-4 weeks for active projects)
- Filter by source (telegram, cli, cron) based on context needed

### File Analysis Patterns
- Read header sections first (metadata, configuration)
- Check for JSON/data files that drive dynamic content
- Look for TODO comments or FIXME markers
- Verify file paths and dependencies

### Gap Analysis Framework
```
✅ Already Done: [list completed items]
🔄 Needs Update: [items to modify]
⚠️  Missing: [items not implemented]
```

## Pitfalls to Avoid

### ❌ Don't Assume Continuity
- Always verify current state; don't rely on memory
- Check for multiple versions of files
- Verify which branch or deployment is live

### ❌ Don't Trust Status Messages at Face Value
When someone reports "X is partially built" or "we have 1 program," **verify before planning.** A status message from a previous session may be stale. Concrete verification:
```bash
# List actual files to confirm what exists
find <project-path> -name "*.rs" -o -name "*.ts" -o -name "*.py" | wc -l
# Check if handlers are implemented, not just declared
grep -r "pub fn handler" <project-path> | wc -l
```
This session discovered a status message claiming "1 partially built program" when the vault actually contained 4 complete programs with 18 instruction handlers. The planning would have been completely wrong if we'd trusted the status without checking.

### ❌ Don't Skip Documentation
- Always reference the project spec or requirements
- Check for update logs or CHANGELOGs
- Review any GitHub issues or PRs

### ❌ Don't Overlook Dependencies
- Check if external services need updating
- Verify API keys and credentials are current
- Ensure team members are aware of changes

## Quality Checks

Before marking project as "coordinated":

- [ ] All relevant sessions retrieved and summarized
- [ ] Current file state verified against live deployment if applicable
- [ ] Requirements/specifications cross-referenced
- [ ] Action items are specific and assignable
- [ ] Dependencies identified and acknowledged
- [ ] Next steps include clear ownership and timeline

## Example Output Format

```
## Project Status: [Project Name]

**✅ Already Done:**
- [list]

**🔄 Needs Update:**
- [items]

**⚠️  Missing/Broken:**
- [issues]

**Next Steps:**
1. [action] - Owner: [name] - ETA: [date]
2. [action] - Owner: [name] - ETA: [date]

**Dependencies:**
- [list]
```

## Integration Points

- Works with `session_search` for context retrieval
- Uses `read_file` for file analysis
- Integrates with `delegate_task` for team coordination
- Can trigger `github-pr-workflow` for code changes
- Supports `plan` mode for complex projects

## Success Metrics

- Time from "where are we?" to clear status report < 2 minutes
- Accuracy of gap analysis (vs. actual work needed)
- Actionability of proposed next steps
- Reduction in user follow-up questions about project status

## Maintenance

Update this skill when:
- New coordination patterns emerge
- User provides feedback on status report format
- Tooling changes (new file locations, different search patterns)
- Team structure changes (new roles, new tools)