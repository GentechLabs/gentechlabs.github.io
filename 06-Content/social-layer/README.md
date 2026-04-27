# Social Layer POC

Agent-driven X/Twitter operations for GenTech Creative.

## Architecture

```
┌─────────────────────────────────────────────┐
│              Social Layer POC               │
├──────────┬──────────────┬───────────────────┤
│ Monitor  │  Engage      │  Publish          │
│ -timeline│  -search     │  -threads         │
│ -mentions│  -like/reply │  -scheduled posts  │
│ -lists   │  -follow     │  -approval flow   │
└──────────┴──────────────┴───────────────────┘
         Powered by xurl + cron jobs
```

## Components

### 1. Daily Briefing (`daily-briefing.sh`)
- Pulls home timeline (last 50 posts)
- Pulls mentions (last 20)
- Pulls bookmarks
- Generates a digest summary for Jordan

### 2. Engagement Scanner (`engage-scanner.sh`)
- Searches for relevant keywords:
  - hackathon, Base, Solana, AI agents, smart contracts
  - hackathon submission, code4rena, audit
- Filters for engagement opportunities
- Outputs candidates for manual or automated reply

### 3. Content Publisher (`publish.sh`)
- Reads drafts from `drafts/` folder
- Posts approved content via xurl
- Supports threads (multi-post)
- Logs all posts to `post-log.csv`

## Prerequisites
- xurl installed + authenticated
- X API app with OAuth 2.0

## Cron Schedule
| Job | Frequency | Description |
|-----|-----------|-------------|
| daily-briefing | Every 6h | Timeline + mentions digest |
| engage-scanner | Every 2h | Find engagement opportunities |
| post-reminders | Daily 9am | Check drafts queue |

## Status
- [x] xurl installed
- [ ] X API auth configured
- [ ] First briefing run
