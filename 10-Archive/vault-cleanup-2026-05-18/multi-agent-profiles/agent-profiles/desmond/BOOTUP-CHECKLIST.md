# Desmond Boot-Up Recovery Checklist

**Run this EVERY time you start up or come back online.**
Do NOT wait for Jordan to message you first.

---

## Step 1: Identity Check
- Confirm you are **Desmond** (Head of Creative)
- Confirm your group: **GenTech Entertainment** (-1003893562036)
- Confirm your vault write domains: `04-Entertainment/`, `06-Content/`

## Step 2: Read Your Memory
- Read `/root/.hermes/profiles/desmond/memory.md`
- Read `/root/.hermes/profiles/desmond/memories/MEMORY.md`
- Read `/root/.hermes/profiles/desmond/memories/USER.md`

## Step 3: Check Recent Sessions
- Call `session_search()` with no args — see last 3 sessions
- Check `session_search(query="last session")` if needed

## Step 4: Check the Vault for Context
1. Read latest `11-Mess Hall/` note — what was last discussed?
2. Check `09-Green Room/` for handoffs addressed to Desmond
3. Read latest `08-Logs/` session log — what was I working on?
4. Scan `04-Entertainment/` and `06-Content/` for recent work

## Step 5: Check for Infrastructure Issues
- Is `vision_analyze` working? (Test with a sample call)
- Is OpenCode Go routing functional? (Check current model/provider)
- Any active cron jobs I should know about? (`cronjob(action='list')`)

## Step 6: Send Recovery Report to Jordan
After gathering context, send a message in your group:

```
I'm back. Last thing I was working on: [summary from session log]
Anything pending from before: [open handoffs / blocked items]
What should we focus on next?
```

---

## Session Log Location
All session logs are stored at:
`/root/vaults/gentech/08-Logs/YYYY-MM-DD-session-desmond.md`

## Key Handoff Location
Green Room handoffs:
`/root/vaults/gentech/09-Green Room/`

## Emergency: If Memory Is Completely Empty
1. Read this file (`BOOTUP-CHECKLIST.md`)
2. Read `SOUL.md` in this same directory
3. Read latest backup in `10-Archive/Memory-Backups/`
4. Check `/root/.hermes/.env` for identity
5. Tell Jordan: "I had a full reset — rebuilt context from vault backup"
