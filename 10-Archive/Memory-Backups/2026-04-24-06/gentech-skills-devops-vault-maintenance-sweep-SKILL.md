---
name: vault-maintenance-sweep
description: Systematic health check and cleanup of the Gentech Obsidian vault, including stale file detection, orphan file scanning, and coordination board auditing.
---

# Vault Maintenance Sweep

## Trigger
Run as a nightly cron job or periodically to ensure vault hygiene and agent coordination.

## Procedure

### 1. Health Scan
Identify files violating the organizational structure or timing rules:
- **Stale Inbox**: Search `00-Inbox/` for files older than 7 days.
- **Stale Temp**: Search `08-Temp/` for files older than 24 hours.
- **Stale Context**: Search `10-Context/` for market data/news older than 3 days.
- **Orphans**: Find all `.md` files in the vault and flag any whose top-level directory is not in the standard list (`00-Inbox`, `01-Agents`, `02-Projects`, `03-Strategies`, `04-Research`, `05-Contracts`, `06-Content`, `07-Admin`, `08-Temp`, `09-Green Room`, `10-Context`, `11-Mess Hall`, `12-Archive`).
- **Empty Files**: Scan for files with a size of 0 bytes.

### 2. Coordination Audit
Check `11-Mess Hall/handoff-board.md` and `11-Mess Hall/agent-coordination-board.md`:
- Identify tasks marked `PENDING` or `ESCALATED` that have passed their ACK deadline.
- Flag overdue items to be reported to HQ.

### 3. Approval Search
Search across the entire vault for:
- `grep -Ei 'TODO: Jordan|needs approval|pending review'`
- Check `02-Labs/Hackathons/` for pending submissions.
- Check `05-Contracts/` for awaiting sign-offs.

### 4. Automated Cleanup (Safe Actions)
- Move `08-Temp/` (stale > 24h) $\rightarrow$ `12-Archive/`.
- Move `00-Inbox/` (stale > 7d) $\rightarrow$ `12-Archive/` or appropriate project folder.
- **Note**: Never delete files; only archive.

### 5. Reporting
Create a report in `11-Mess Hall/vault-sweep-YYYY-MM-DD.md` containing:
1. Files moved/archived.
2. List of pending approvals for Jordan (with paths).
3. Coordination gaps (overdue handoffs).
4. Vault Health Score (1-10).

## Pitfalls & Tips
- **Path Hazards**: Be careful with `os.path.relpath` if the file list contains empty strings or unexpected root paths. Always filter `find` output to remove empty lines.
- **Grep Efficiency**: Use `grep -l` (files with matches) instead of outputting every line to avoid flooding the context window when scanning a large vault.
- **SOP Alignment**: If "Orphaned" files are found in `10-Archive` or `01-News`, prioritize their formal migration to correctly numbered folders to maintain the vault's sorting logic.
