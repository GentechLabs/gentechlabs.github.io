# Grep Patterns — Quick Discovery Commands

All commands assume vault root `/root/vaults/gentech/`.

## Pending Handoffs
```bash
# Handoff board — pending acknowledgments
grep -E "🚀|⏳" 11-Mess Hall/handoff-board.md

# Unacknowledged (Pending Ack specifically)
grep "🚀 Pending Ack" 11-Mess Hall/handoff-board.md

# Escalated items
grep "ESCALATED" 11-Mess Hall/handoff-board.md
```

## Pending / Awaiting Approval
```bash
# Files with "pending approval" anywhere
grep -r "pending approval" /root/vaults/gentech/ --include="*.md"

# Files with "awaiting Jordan"
grep -r "awaiting Jordan" /root/vaults/gentech/ --include="*.md"

# In 00-HQ/Approvals only
grep -r "status: pending" /root/vaults/gentech/00-HQ/Approvals/ --include="*.md"

# Unchecked checkboxes in Mess Hall
grep -r "\[ \]" /root/vaults/gentech/11-Mess Hall/ --include="*.md"

# Unchecked in Working
grep -r "\[ \]" /root/vaults/gentech/00-Working/ --include="*.md"
```

## Incidents & Blockers
```bash
# Active infrastructure incidents
grep -r "INCIDENT\|ACTIVE" /root/vaults/gentech/00-HQ/Operations/ --include="*.md"

# OAuth / auth issues
grep -r "OAuth\|auth\|token" /root/vaults/gentech/00-HQ/Operations/ --include="*.md"

# Overdue items
grep -r "overdue" /root/vaults/gentech/08-Daily/ --include="*.md"
grep -r "overdue" /root/vaults/gentech/11-Mess Hall/ --include="*.md"

# Debates / unresolved discussions
grep -r "debate\|dispute\|unresolved" /root/vaults/gentech/09-Green Room/ --include="*.md"
```

## Agent Status & Coordination
```bash
# Agent check-in status (coordination board)
grep -A 3 "Agent Session Check-In" /root/vaults/gentech/11-Mess Hall/agent-coordination-board.md

# Agent offline/online markers
grep -r "OFFLINE\|ONLINE" /root/vaults/gentech/11-Mess Hall/ --include="*.md"

# Rotation context
grep -r "Rotation\|check-in" /root/vaults/gentech/11-Mess Hall/agent-coordination-board.md | head -10
```

## Daily Log Specifics
```bash
# Today's daily log (assuming today is 2026-05-03)
cat /root/vaults/gentech/08-Daily/2026-05-03.md

# Extract TL;DR section (lines after ## TL;DR until next ##)
sed -n '/## TL;DR/,/## /p' /root/vaults/gentech/08-Daily/2026-05-03.md | head -15

# Extract blockers table section
sed -n '/## 🔓 Open Items/,/## /p' /root/vaults/gentech/08-Daily/2026-05-03.md

# Extract EOD summary only
sed -n '/## 📎 End Of Day Summary/,/## /p' /root/vaults/gentech/08-Daily/2026-05-03.md

# Extract a specific team section (e.g., Strategies)
sed -n '/## 📈 Strategies/,/## /p' /root/vaults/gentech/08-Daily/2026-05-03.md
```

## File Modification Times (Last 24h)
```bash
# Files modified in last 24h by department
find /root/vaults/gentech/02-Labs -name "*.md" -mtime -1
find /root/vaults/gentech/03-Strategies -name "*.md" -mtime -1
find /root/vaults/gentech/01-Agency -name "*.md" -mtime -1

# Count modifications per team today
echo "Labs: $(find 02-Labs -name '*.md' -mtime -1 | wc -l)"
echo "Strategies: $(find 03-Strategies -name '*.md' -mtime -1 | wc -l)"
echo "Agency: $(find 01-Agency -name '*.md' -mtime -1 | wc -l)"
```

## Handoff Files
```bash
# Active handoffs (last 48h)
find /root/vaults/gentech/09-Green Room/active-handoffs/ -name "*.md" -mtime -2

# Recent completed handoffs
find /root/vaults/gentech/09-Green Room/handoffs/ -name "*.md" -mtime -1 | sort
```

## Priority & Marker Extraction
```bash
# Extract all P0 items from daily log
grep -E "🔴|P0" /root/vaults/gentech/08-Daily/2026-05-03.md

# Extract all lines with rocket emoji (active priority)
grep -r "🚀" /root/vaults/gentech/11-Mess Hall/handoff-board.md

# Extract lines with watch/alert emojis
grep -r "⚠️\|🚨" /root/vaults/gentech/08-Daily/2026-05-03.md
```

## Vault Sweep & Health
```bash
# Vault sweep reports (most recent)
ls -lt /root/vaults/gentech/11-Mess Hall/vault-sweep-*.md | head -3

# Health score mentions
grep -r "health score\|vault health" /root/vaults/gentech/11-Mess Hall/ --include="*.md"
```

## Notes
- Always include `--include="*.md"` to avoid binary files
- Use `grep -r` for recursive, but restrict to specific subfolder when possible (faster)
- For tables, extract by line range with `sed` or `awk` rather than grep
- To preserve color codes in output (for emoji scanning), add `--color=auto`
- Combine patterns: `grep -E "🚀|⏳|🔴"` for all priority states
