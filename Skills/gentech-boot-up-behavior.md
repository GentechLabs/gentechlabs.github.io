# Gentech Boot-Up Behavior Spec
**Purpose:** Ensure all agents pick up where they left off after restart/session reset.
**Status:** Active
**Last Updated:** 2026-04-26

---

## Boot-Up Sequence (Execute IN ORDER)

### Step 1: Self-Identify
```
Read /root/.hermes/profiles/[agent-name]/memory/
Confirm: who you are, your role, Jordan's preferences.
```

### Step 2: Session Search
```
Use session_search (no query) to see recent sessions.
Identify what was being worked on LAST.
```

### Step 3: Read the Brain (Vault)
```
1. Read /root/vaults/gentech/INDEX.md
2. Read latest session state save in Green-Room/ (if exists)
3. Check 01-Agency/Approvals/ for pending Jordan decisions
4. Check Green-Room/ for active handoffs
5. Check Mess-Hall/ for recent discussions
```

### Step 4: Check System Health
```
- cronjob(action='list') → verify all jobs running
- Check agent gateway status (if applicable)
- Verify provider connectivity (OpenCode Go / Ollama Cloud)
```

### Step 5: Report to Jordan (CONSOLIDATED)
```
"HQ is online. Current active workstreams:
- [Task 1]: status
- [Task 2]: status
- Blockers: [if any]
Standing by for routing."
```

---

## Agent-Specific Boot Priorities

### Gentech (HQ)
- Read Green-Room/ for all active handoffs
- Check which specialists have pending work
- Verify model switching bug status (OpenCode Go / Ollama)
- Deliver ONE consolidated status to Jordan

### YoYo (Strategies)
- Check Strategies/ for active positions/LP data
- Verify LP monitor cron is healthy
- Check if any market alerts fired while offline

### DMOB (Labs)
- Check Labs/ for active audits/hackathons
- Verify OpenCode Go subscription + API keys
- Check config.yaml for model fallback issues

### Desmond (Entertainment)
- Check Content/ for active drafts
- Check 01-Agency/HQ-Working/X-Content/ for posting queue
- Verify any scheduled content went out

---

## Recovery Priority Rules
1. **Never respond to old messages blindly** — always check context first
2. **Never start new work before finishing queued items** — process oldest first
3. **Always acknowledge gaps** — "I had to recover, here's what I found..."
4. **One consolidated answer** — no walls of text, keep it scannable

---

Tags: #boot-up #recovery #protocol #restart #agent-behavior
