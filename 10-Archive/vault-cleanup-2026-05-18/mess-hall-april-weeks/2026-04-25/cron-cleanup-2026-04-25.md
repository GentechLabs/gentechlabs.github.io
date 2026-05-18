# Cron Job Cleanup — 2026-04-25

## What Changed

Cleaned up **22 cron jobs** to match the new **Human-Readable First** standard in `01-Agency/cron-job-standards.md`.

## The Standard

- **Name**: Human-readable, no code, no agent novellas
- **Prompt**: Max 2–3 sentences. No code blocks. No "You are [Agent]" roleplay.
- **Scripts**: Raw bash/python lives in `~/.hermes/scripts/cron/` or in skills.

## Jobs Cleaned

| Job | Before | After |
|-----|--------|-------|
| Brain Backup → GitHub | Raw bash in prompt | "Run the brain backup script..." |
| AAE LP D5 Milestone Monitor | "Execute this command and capture JSON..." | "Run the daily LP summary script..." |
| Hermes Agent Daily Sync Check | "You are DMOB... 1. Compare... 2. Report..." | "Check the Hermes fork sync status..." |
| Weekly Opportunity Scanner | "You are DMOB... 1. Check platforms..." | "Scan for new opportunities..." |
| Kite AI Hackathon Check | "You are DMOB... 1. Check Encode Club..." | "Check Encode Club Kite AI page..." |
| Protocol Due Diligence | "You are YoYo... 1. Check vault..." | "Run the protocol due diligence pipeline..." |
| Security → Content Pipeline | "You are Desmond... 1. Check vault..." | "Run the security-to-content pipeline..." |
| Gentech X Content Extractor | "You are Desmond... 1. Search X..." | "Extract and analyze X/Twitter content..." |
| LayerZero DVN Monitor | "You are YoYo... Search the web..." | "Run the LayerZero DVN security monitor..." |
| Master Morning Digest | "You are Gentech's HQ Orchestrator..." | "Deliver the Master Morning Digest..." |
| Vault Maintenance — Weekly | "You are the Vault Manager..." | "Run a systematic audit of the vault..." |
| The Brain Review | "Review the Obsidian vault..." (was okay) | "Review the vault for stale content..." |
| End of Shift Wrap-Up | "You are Gentech's HQ Orchestrator..." | "Run the end-of-shift wrap-up..." |
| Weekly Skills Update Check | "You are YoYo..." | "Run a weekly skills audit..." |
| Vault Manager — Nightly | "You are YoYo running the nightly..." | "Run the nightly Vault Manager sweep..." |
| Gentech Watchdog | "You are the Gentech Watchdog..." | "Run the agent health check..." |
| Mess Hall — Agent Check-in | "Daily agent check-in time..." (was okay) | "Daily agent check-in..." |
| Gentech LLC Reminder | "This is a monthly reminder..." (was okay) | "Monthly reminder: review LLC items..." |
| Crypto Watchlist + LP | "You are YoYo... 1. Pull prices..." | "Run the crypto watchlist + LP monitor skills..." |

## Scripts Created

- `~/.hermes/scripts/cron/brain-backup.sh` → wraps `/root/repos/hermes-brain/scripts/backup.sh`
- `~/.hermes/scripts/cron/daily-lp-summary.sh` → wraps `~/.hermes/scripts/daily-lp-summary.py`

## Remaining Work

- [ ] Convert the most complex workflows (Master Digest, Protocol DD, Opportunity Scanner) into proper skills so the cron prompt can be a single sentence.
- [ ] Audit `03-Strategies/cron-jobs.md` and `12-Skills/cron-routing.md` to sync job IDs and schedules.
- [ ] Add `--help` flags to all scripts in `scripts/cron/`.
