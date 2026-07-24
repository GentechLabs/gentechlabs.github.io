# 🚀 GenTech Starter Template

> **Bootstrap any Hermes agent with x402 payments, Q402 subscriptions, and GenTech patterns.**
> One command. Full stack. Start earning on day one.

[![CLARITY Act Compliant](https://img.shields.io/badge/CLARITY%20Act-Compliant-00FF00)](https://gentechlabs.net)
[![x402 Ready](https://img.shields.io/badge/x402-Ready-8A2BE2)](https://x402.org)
[![Q402 Ready](https://img.shields.io/badge/Q402-Subscriptions-FF6B35)](https://gentechlabs.net/pricing)

---

## Quick Start

```bash
# 1. Clone the template
git clone https://github.com/ProtoJay4789/gentech-starter-template my-agent
cd my-agent

# 2. One-command setup
bash setup.sh

# 3. Add your API keys
# Edit .env — instructions in the file

# 4. Verify everything works
bash scripts/verify-setup.sh

# 5. Go!
hermes run
```

## What You Get

| Component | Description |
|-----------|-------------|
| **x402 Gateway** | Pay-per-call endpoint protection. Every API call earns USDC. |
| **Q402 Subscriptions** | Recurring billing — $3/$10/$25 tiers with credit allowances. |
| **Model Routing** | Auto-switch to GLM-5.2 for audits, deepseek for daily work. |
| **CLARITY Act Compliance** | Agent identity, security scanning, credit scoring, payment integrity. |
| **Build Patterns** | GenTech's BUILD→AUDIT→VERIFY workflow. Ship fast, ship safe. |

## Structure

```
gentech-starter-template/
├── config.yaml               # Hermes agent config
├── .env.template             # API keys template
├── SOUL.md                   # Agent identity
├── README.md                 # This file
├── setup.sh                  # One-command setup
└── skills/
    ├── x402-gateway/         # x402 pay-per-call integration
    ├── q402-payments/        # Q402 subscription billing
    ├── model-routing/        # Audit-aware model selection
    └── gentech-patterns/     # Core development conventions
```

## Skills in Detail

### 🔌 x402 Gateway
Every endpoint can earn. Wrap any API handler with `withX402()` and callers pay per request. Supports Base, Polygon, and Arbitrum.

### 💳 Q402 Subscriptions
Three tiers ($3/$10/$25) with credit allowances. Users subscribe via a /pay URL, get a Trust Receipt, and the agent verifies it on each call.

### 🧠 Model Routing
Smart model selection: deepseek for daily work, GLM-5.2 for audits, qwen-vl for vision. Never second-guess which model to use.

### ⚡ GenTech Patterns
BUILD→AUDIT→VERIFY workflow, CLARITY Act compliance checks, vault sync protocol, and build queue management.

## Prerequisites

- **Node.js** ≥ 18 (for x402 SDK)
- **Hermes Agent** (for agent runtime)
- **Git** (for vault sync)
- A **Z.AI API key** (for GLM-5.2 audit model)
- An **x402-compatible wallet** (Base, Polygon, or Arbitrum)

## Deploying Your Agent

### Option 1: VPS (recommended for 24/7 agents)
```bash
# On your VPS:
git clone <your-fork>
bash setup.sh
hermes run --daemon
```

### Option 2: Desktop
```bash
# Same steps, runs on your local machine
bash setup.sh
hermes run
```

### Option 3: Cloudflare Workers (serverless)
```bash
npm install -g @x402/cli
x402 init my-agent-worker
# Copy the x402-gateway skill into your worker
x402 deploy
```

## Monetization

Your agent starts earning immediately:

1. **Deploy** — Your agent goes live with x402-protected endpoints
2. **Users pay per call** — Auto-settled in USDC
3. **Or subscribe** — $3/$10/$25 monthly tiers via Q402
4. **Revenue split** — 70% to you, 30% to gateway operator

## CLARITY Act Compliance

Every GenTech-powered agent is CLARITY Act compliant by default:

- ✅ **Identity** — ERC-8004 registered agent
- ✅ **Security** — 5-domain scan (Rugcheck v2)
- ✅ **Credit** — 0-850 agent credit score
- ✅ **Payments** — x402 payment integrity
- ✅ **DeFi Exclusion** — Sec. 309/409 exempt

## Support

- **Docs:** https://gentechlabs.net/docs
- **Pricing:** https://gentechlabs.net/pricing
- **GitHub:** https://github.com/ProtoJay4789/gentech-starter-template
- **x402 Protocol:** https://x402.org

---

**Built with ❤️ by GenTech Labs**
*Tough love for the agent economy.*
