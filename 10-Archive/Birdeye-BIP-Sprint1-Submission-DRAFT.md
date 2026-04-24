# Birdeye Token Safety Radar — BIP Competition Submission

> **Birdeye Data 4-Week BIP Competition — Sprint 1**
> Deadline: April 25, 2026
> Prize: 500 USDC + Premium Plus Plan ($1,000 value)

---

## The Problem

New Solana tokens launch every minute. Most are scams.

Rug pulls, honeypots, and mint-and-dump schemes cost traders millions every week. Existing tools either require expensive subscriptions or don't exist as autonomous agents — they're dashboards that need a human watching.

**The agentic economy needs autonomous safety scanners.**

## The Solution

**Birdeye Token Safety Radar** — an AI agent that autonomously monitors new Solana token listings and scores their safety in real-time.

### How It Works

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│  Birdeye API    │────▶│  Radar Agent │────▶│  Telegram Bot   │
│  /new_listing   │     │              │     │  Alert Channel  │
│  /token_security│     │ Score: 0-100 │     │                 │
└─────────────────┘     └──────────────┘     └─────────────────┘
        ▲                     │
        │                     ▼
   x402 Payment         Risk Analysis
   $0.003/req           • Mintable?
                         • LP Locked?
                         • Top Holder %
                         • Holder Count
```

1. **Poll** — Agent checks Birdeye `/v2/tokens/new_listing` every 60 seconds
2. **Enrich** — Each new token hits `/defi/token_security` for safety data
3. **Score** — Risk engine computes 0-100 score with specific flags
4. **Alert** — Telegram bot delivers formatted alerts for risky tokens
5. **Deduplicate** — Tracks seen tokens to avoid spam

### Safety Scoring Engine

| Flag | Penalty | Why It Matters |
|------|---------|----------------|
| Mintable | -30 | Deployer can inflate supply at will |
| Freezable | -20 | Transfers can be blocked (honeypot) |
| LP Not Locked | -25 | Liquidity can be pulled (rug pull) |
| Top Holder > 20% | -15 | One wallet can dump on everyone |
| Holders < 50 | -10 | Too early / no organic adoption |

**Risk Levels:**
- 🟢 **LOW** (80-100): Looks safe
- 🟡 **MEDIUM** (60-79): Review carefully
- 🟠 **HIGH** (40-59): Multiple red flags
- 🔴 **CRITICAL** (0-39): Likely scam

## Why Birdeye x402?

This agent uses Birdeye's **x402 pay-per-request API** — no subscription needed.

- **$0.003 per request** — full REST API access
- **USDC settlement** via Coinbase CDP (Base) or PayAI (Solana)
- **No API key management** — payment IS the authentication
- **Autonomous** — the agent pays from its own wallet, no human in the loop

This is the agentic economy in action: an autonomous bot that discovers, pays for, and uses data services at machine speed.

## Why This Matters

Birdeye powers **Phantom, Backpack, Raydium, and Bybit**. Their data is the gold standard for Solana DeFi.

But today, that data lives behind subscription walls or requires human-operated dashboards. An autonomous safety radar agent changes the game:

- **Traders** get real-time scam alerts without watching charts
- **DeFi protocols** can gate interactions based on token safety scores
- **AI agents** can autonomously avoid risky tokens before executing trades

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Agent Runtime | Python | Polling, scoring, alerting |
| Token Data | Birdeye `/new_listing` | New Solana token discovery |
| Security Data | Birdeye `/token_security` | Risk flags and holder analysis |
| Payment | x402 Protocol | Pay-per-request at $0.003 |
| Alerts | Telegram Bot API | Real-time notifications |
| Deduplication | Local JSON | Prevent alert spam |

## Metrics (Minimum 50 API Calls)

Each poll cycle uses:
- 1 call to `/v2/tokens/new_listing` (lists ~20 tokens)
- 1-20 calls to `/defi/token_security` (one per new token)

**At 60-second intervals, we hit 50+ API calls within the first hour of running.**

## Live Demo

The agent runs continuously, polling every 60 seconds. Sample alert:

```
🟢 Token Safety Radar
━━━━━━━━━━━━━━━━━━━━

**DogeMoon** ($DOGE)
`7xKXt...9mPq`

Safety Score: 85/100 (LOW)
Liquidity: $125,000
Volume 24h: $45,000
Holders: 1,234

Security Flags:
• Mintable: No ✅
• Freezable: No ✅
• LP Locked: Yes ✅
• Top Holder: 3.2%

Verdict: ✅ LOOKS SAFE
```

## Links

- **GitHub:** github.com/ProtoJay4789/birdeye-token-radar
- **Birdeye Data:** bds.birdeye.so
- **x402 Protocol:** x402.org

---

## Team

**Gentech** — Building the Autonomous Agent Economy

| Agent | Role |
|-------|------|
| Jordan | Strategy, security, project lead |
| YoYo | Market research, data analysis |
| DMOB | Smart contracts, backend |
| Desmond | Content, pitch, documentation |

---

## Judging Alignment

| Criterion (25% each) | How We Score |
|----------------------|--------------|
| **Technical Depth** | x402 pay-per-request integration, real-time API chaining, risk scoring engine |
| **Product Utility** | Solves real problem — scam detection for new Solana tokens |
| **Presentation** | Clean README, demo video, formatted Telegram alerts |
| **Community** | Build-in-public X thread, open-source code, tagging @birdeye_data |

---

*Built by Gentech for the Birdeye BIP Competition — Sprint 1, April 2026*
