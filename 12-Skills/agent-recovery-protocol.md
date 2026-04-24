# Agent Recovery Protocol

**Purpose:** When an agent comes back online (after downtime, reinstall, or session reset), this protocol ensures fast context recovery.

**Status:** Active
**Last Updated:** 2026-04-20

---

## 🔄 Recovery Checklist (Execute in Order)

When you boot up after being offline, follow these steps IN ORDER before responding to any user message:

### Step 1: Check Recent Session History
```
Use session_search (no query) to see recent sessions.
Look at what was being worked on last.
```

### Step 2: Read Your Brain
```
Read your memory file:
- /root/.hermes/profiles/[your-name]/memory/

This tells you:
- Who you are
- What your role is
- Key facts and user preferences
- What was happening recently
```

### Step 3: Check the Vault
```
Read:
- /root/vaults/gentech/INDEX.md
- /root/vaults/gentech/09-Green Room/ (active handoffs)
- /root/vaults/gentech/11-Mess Hall/ (recent discussions)
- /root/vaults/gentech/10-Archive/Memory-Backups/ (latest backup)
```

### Step 4: Check GitHub (if applicable)
```
- Is there a hermes-brain-backup repo?
- Any open PRs or issues assigned to you?
- Any commits since you were last online?
```

### Step 5: Check Cron Jobs
```
Use cronjob(action='list') to see what's running.
Did any fail while you were offline?
```

### Step 6: Report to User
After gathering context, send a recovery message like:

> "I'm back online. Here's what I remember:
> - Last task: [what you were working on]
> - Status: [complete/in-progress/blocked]
> - Action items: [what needs attention]
> - What should we focus on next?"
```

---

## 🧠 Memory Queue System

When the user sends messages while you're offline, they naturally queue in Telegram. When you come back:

1. **Read the queue** — your Telegram messages ARE the queue
2. **Process in order** — oldest to newest
3. **Don't skip** — even if a newer message seems more important
4. **Acknowledge** — "I see you asked about X while I was away — here's the answer"

---

## 📋 Agent-Specific Recovery Notes

### Desmond (Content & Creative)
- Check `04-Entertainment/` for active content drafts
- Check `01-Agency/HQ-Working/X-Content/` for posting queue
- Verify cron jobs (memory backup, any content crons)

### YoYo (Investment & Strategy)
- Check `03-Strategies/` for active positions
- Verify LP monitor cron is running
- Check CMC watchlist data freshness

### DMOB (Smart Contracts & Security)
- Check `06-Security/` for active audits
- Check `02-Labs/Bug-Bounties/` for active hunts
- Verify hackathon scout cron

### Gentech (Team Lead)
- Check all Green Room handoffs
- Verify all agent crons are healthy
- Check `08-Daily/` for today's log

---

## 🚨 If Memory Is Lost

If you come back with NO memory at all:

1. Read `/root/vaults/gentech/INDEX.md` — the master index
2. Read latest backup from `10-Archive/Memory-Backups/`
3. Read `/root/vaults/gentech/00-Working-Memory.md` — quick context file
4. Check `/root/.hermes/.env` — confirms agent identities
5. Tell the user: "I had to recover — here's what I've rebuilt from the vault"

---

## Tags
#protocol #recovery #workflow #agents #resilience
