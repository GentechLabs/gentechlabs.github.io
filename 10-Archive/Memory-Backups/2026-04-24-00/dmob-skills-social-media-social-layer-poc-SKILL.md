---
name: social-layer-poc
description: Agent-driven social media intelligence pipeline using xurl. Modular monitoring for feeds, security alerts, and crypto intel with deduplication and cost optimization.
version: 1.0.0
author: DMOB (GenTech Labs)
tags: [twitter, x, social-media, monitoring, xurl, security, defi]
prerequisites:
  commands: [xurl, jq]
metadata:
  hermes:
    tags: [twitter, x, social-media, xurl, monitoring]
---

# Social Layer POC — X API Intelligence Pipeline

Agent-driven social monitoring using `xurl` (official X API CLI). Leverages the new $0.001/call owned-read pricing for near-free continuous monitoring.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Cron Jobs  │────▶│  xurl CLI    │────▶│  Vault (Obsidian)│
│  (Hermes)   │     │  (X API)     │     │  social-layer-poc│
└─────────────┘     └──────────────┘     └─────────────────┘
       │                                        │
       ▼                                        ▼
┌─────────────┐                         ┌─────────────────┐
│  Alerts     │                         │  Agent Analysis  │
│  (Telegram) │                         │  (DMOB/YoYo)     │
└─────────────┘                         └─────────────────┘
```

## Key Design Decisions

1. **Deduplication**: Each module tracks post IDs in `.last_run_ids` / `.alerted_ids` files to avoid duplicate alerts across runs
2. **Rate limiting**: 1-second sleep between API calls to respect X rate limits
3. **Config-driven**: All keywords, accounts, and schedules in `config.sh` — easy to customize without touching scripts
4. **JSON-first**: All xurl output is JSON; use `jq` for parsing throughout
5. **Vault integration**: Results saved as markdown summaries in Obsidian vault for agent analysis

## Modules

### 1. Feed Monitor (`feed-monitor.sh`)
- Pulls home timeline (50 posts) + mentions (20 posts)
- Deduplicates against previous run via state file
- Saves raw JSON + markdown summary
- **Cost**: ~$0.001/call, 12 calls/day = **$0.012/day**

### 2. Security Radar (`security-radar.sh`)
- Searches X for security keywords (exploit, vulnerability, rug pull, etc.)
- Monitors known security researcher timelines (samczsun, ZachXBT, PeckShieldAlert, etc.)
- Deduplicates alerts to avoid spam
- **Cost**: ~$0.008/day

### 3. Crypto Intel (`crypto-intel.sh`)
- Pulls recent posts from DeFi protocol accounts (Aave, Uniswap, Chainlink, etc.)
- Tracks hackathon accounts (ETHGlobal, EthDenver, etc.)
- Runs trending searches (#DeFi, #Solana, etc.)
- **Cost**: ~$0.010/day

### 4. Quick Test (`quick-test.sh`)
- Verifies xurl installation and auth status
- Run before setting up cron jobs

## File Structure

```
social-layer-poc/
├── README.md          # Overview + cost analysis
├── config.sh          # Keywords, accounts, schedules (edit this)
└── scripts/
    ├── feed-monitor.sh
    ├── security-radar.sh
    ├── crypto-intel.sh
    └── quick-test.sh
```

## Setup Steps

### 1. X API Auth (manual — never in agent session)
```bash
# Create app at https://developer.x.com/en/portal/dashboard
# Set redirect URI: http://localhost:8080/callback
xurl auth apps add gentech --client-id YOUR_ID --client-secret YOUR_SECRET
xurl auth oauth2
xurl whoami  # verify
```

### 2. Verify Setup
```bash
bash scripts/quick-test.sh
```

### 3. Run Manually (test)
```bash
bash scripts/feed-monitor.sh
bash scripts/security-radar.sh
bash scripts/crypto-intel.sh
```

### 4. Set Up Cron Jobs
```
Feed monitor:    0 */2 * * *     (every 2 hours)
Security radar:  0 */4 * * *     (every 4 hours)
Crypto intel:    0 9,18 * * *    (9am, 6pm)
```

## Cost Analysis

| Module | Calls/day | Cost/day | Cost/month |
|--------|-----------|----------|------------|
| Feed Monitor | 12 | $0.012 | $0.36 |
| Security Radar | 8 | $0.008 | $0.24 |
| Crypto Intel | 10 | $0.010 | $0.30 |
| **Total** | **30** | **$0.03** | **$0.90** |

**Old pricing equivalent**: $15.00/day → $0.03/day (500x savings)

## Customization

Edit `config.sh` to:
- Add/remove security keywords
- Change monitored researcher accounts
- Adjust protocol tracking list
- Modify cron schedules
- Set alert thresholds

## Pitfalls

1. **Auth must be manual** — xurl secrets are in `~/.xurl` YAML, never expose to agent context
2. **Rate limits** — X API has per-endpoint limits. 429 = wait and retry. Scripts include 1s delays.
3. **Token refresh** — OAuth 2.0 tokens auto-refresh, no action needed
4. **jq required** — All scripts depend on jq for JSON parsing
5. **State files grow** — `.last_run_ids` accumulates; periodically truncate to last 1000 IDs
6. **`--verbose` forbidden** — Never use `xurl -v` in agent sessions, it leaks auth headers

## Extension Ideas

- **Sentiment scoring**: Pipe post text through LLM for sentiment analysis
- **Telegram alerts**: Use `send_message` tool when security radar finds matches
- **YoYo integration**: Forward DeFi intel to Green Room for financial analysis
- **DMO pipeline**: Feed security alerts into audit workflow automatically
- **Multi-account**: Use `--app` flag for separate monitoring vs posting accounts
