---
type: standard
status: ACTIVE
enforced-by: all-agents
 created: 2026-04-25
---

# ⏰ Cron Job Standards — Human-Readable First

## The Rule

**A cron job must be understandable in 3 seconds by a human reading the registry.**

If the prompt looks like a coding interview or an agent novella, it's wrong.

---

## ✅ Good Examples

| Name | Prompt | Why It's Good |
|------|--------|---------------|
| Brain Backup → GitHub | Run the brain backup script. Report success/failure. | One sentence. Script lives in `scripts/cron/`. |
| Crypto Watchlist | Run `lp-position-tracker` + `crypto-watchlist-monitor` skills. Alert if 3% move or LP out of range. | References skills. Thresholds included because Jordan needs to see them. |
| Vault Nightly Sweep | Run the Vault Manager sweep. Archive stale temp files. | Action + scope. No implementation details. |

## ❌ Bad Examples

| Name | Prompt (condensed) | Why It's Bad |
|------|-------------------|--------------|
| Brain Backup → GitHub | `You are DMOB. Execute: bash /root/repos/hermes-brain/scripts/backup.sh ...` | Raw bash in the prompt. Code belongs in a script file. |
| AAE LP D5 Milestone Monitor | `You are YoYo. Execute this command and capture the JSON...` | Implementation details leaked into the cron definition. |
| Weekly Opportunity Scanner | `You are DMOB, Gentech's opportunity hunter. Scan for new opportunities: 1. Check hackathon platforms...` | Full agent briefing. That belongs in a skill or the agent's memory, not the cron prompt. |

---

## The Three-Layer Architecture

```
┌─────────────────────────────────────┐
│  Layer 1: Cron Registry             │  ← Human reads this
│  - Name, schedule, delivery         │
│  - One-sentence purpose             │
├─────────────────────────────────────┤
│  Layer 2: Skill or Script           │  ← Agent runs this
│  - Detailed instructions            │
│  - Business logic                   │
├─────────────────────────────────────┤
│  Layer 3: Code / CLI / API          │  ← Machine executes this
│  - Bash, Python, curl, etc.         │
│  - Lives in scripts/cron/           │
└─────────────────────────────────────┘
```

---

## Prompt Writing Rules

1. **Max 3 sentences.** If you need more, use a skill.
2. **No code blocks.** No `bash`, `python`, or `curl` in the prompt field.
3. **No agent roleplay.** Don't start with "You are [Agent]." The agent already knows who it is.
4. **Reference scripts by path** or **skills by name.**
5. **Include thresholds / alert logic** only if Jordan needs to see them in the registry.

---

## Script Storage

- **Agent-shared scripts:** `~/.hermes/scripts/cron/`
- **Vault-backed scripts:** `/root/vaults/gentech/12-Skills/scripts/cron/` (symlinked or copied)
- **Skill-embedded scripts:** Inside the skill directory itself

All scripts in `scripts/cron/` must have:
- A header comment with purpose, author, and last updated date
- `--help` flag support
- Exit code 0 on success, non-zero on failure (cron captures this)

---

## Naming Convention

| Pattern | Example | Use For |
|---------|---------|---------|
| `[System] → [Action]` | `Brain Backup → GitHub` | Integration / data flow |
| `[Scope] — [Frequency]` | `Vault — Nightly Sweep` | Maintenance |
| `[Domain] [Action]` | `Crypto Watchlist` | Monitoring |
| `[Trigger] [Action]` | `Security → Content Pipeline` | Event-driven pipeline |

Keep names under 40 characters so they don't truncate in `cronjob list`.

---

## Migration Checklist

When auditing existing cron jobs:

- [ ] Name is human-readable (no agent names unless disambiguation needed)
- [ ] Prompt ≤ 3 sentences
- [ ] No code blocks in prompt
- [ ] No "You are [Agent]" roleplay
- [ ] Script or skill referenced explicitly
- [ ] Documented in `03-Strategies/cron-jobs.md`
- [ ] Delivery target matches routing rules in `12-Skills/cron-routing.md`

---

## Changelog

| Date | Change |
|------|--------|
| 2026-04-25 | Standard created. All future cron jobs must follow. Existing jobs to be migrated incrementally. |
