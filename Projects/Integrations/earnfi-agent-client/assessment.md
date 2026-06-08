# EarnFi Agent Client — Integration Assessment

**Date:** 2026-06-02
**Source:** https://x.com/EarnFidotfun/status/2061778451560894718
**Status:** Ready to integrate

---

## What It Is

Official TypeScript SDK + CLI for the EarnFi Agent API. Lets agents hire verified humans via x402 USDC payments on Solana.

## Quick Facts

- **Package:** `@earn-fi/agent-client`
- **Version:** 2.0.1 (6 versions shipped)
- **License:** MIT ✅
- **Chain:** Solana
- **Payment:** x402 USDC
- **GitHub:** https://github.com/earnfidotfun/agent-client
- **Docs:** https://app.earnfi.fun/agent-api
- **MCP:** https://app.earnfi.fun/mcp

## What Agents Can Do

| Capability | Method |
|------------|--------|
| Launch social campaigns | `createSocialJob()` |
| Collect human feedback | `createManualJob()` |
| Run contests & bounties | `createContestJob()` |
| Trigger human interrupts | `createInterrupt()` |
| Manage manual reviews | `listSubmissions()` |
| Pay in USDC via x402 | Built-in SVM signer |

## Quick Start

```typescript
import { Connection, Keypair } from '@solana/web3.js';
import { clientFromEnv, EarnFiAgentClient } from '@earn-fi/agent-client';

const client = new EarnFiAgentClient({
  agentToken: process.env.EARNFI_AGENT_TOKEN,
  connection: new Connection(process.env.SOLANA_RPC_URL!),
  wallet: myWallet,
});

// Register agent
await client.register({
  agentName: 'my-agent',
  walletAddress: myWallet.publicKey.toBase58(),
  signMessage: async (msg) => signUtf8(msg),
});

// Get pricing quote
const quote = await client.quoteSocialJob({
  taskType: 'follow',
  slots: 2,
  rewardPerUser: '0.03',
  contentUrl: 'https://x.com/joel_bulldev',
});

// Create job with x402 payment
const job = await client.createSocialJob({
  taskType: 'follow',
  slots: 2,
  rewardPerUser: '0.03',
  contentUrl: 'https://x.com/joel_bulldev',
});

// Poll for completion
const result = await client.pollUntilComplete(job.json.job_id, job.json.secret);
```

## CLI

```bash
npx earnfi-agent init --wallet PUBKEY --name my-agent --secret-key-bs58 KEY
npx earnfi-agent preflight --secret-key-bs58 KEY
npx earnfi-agent create-social --task-type follow --slots 2 --reward 0.03 --content-url URL
npx earnfi-agent poll-job --job-id EF123A --secret SECRET
```

## Lobby UI Integration

### Flow

```
User clicks "Find Teammates"
        ↓
client.quoteSocialJob() → get pricing
        ↓
User sees: "0.025 USDC" (micropayment)
        ↓
client.createSocialJob() → x402 payment
        ↓
Humans claim task
        ↓
client.pollUntilComplete() → wait for results
        ↓
Task complete → payment auto-releases
        ↓
"Teammate found!" → game begins
```

### What We Build

1. **Lobby component** — HTML/JS/React UI
2. **Payment transparency** — Show micropayment clearly
3. **EarnFi integration** — Call SDK methods
4. **Polling loop** — Check job status
5. **Social graph** — Friend list, online status

### What We Use

- **EarnFi Agent Client** — Human execution
- **x402** — Micropayment protocol
- **Solana** — Chain
- **ERC-8004** — Agent identity (future)

## MCP Server

Available at `https://app.earnfi.fun/mcp` for Cursor/MCP-native agents.

## SDK vs MCP vs Skill

| Surface | Use when |
|---------|----------|
| **SDK** | Node/TS agents, Synapse plugins, automation |
| **MCP** | Cursor / MCP-native agents |
| **skill.md** | Human-readable spec + curl examples |

## Open Questions

1. Does the MCP server work with Hermes?
2. What's the minimum USDC balance needed?
3. Can we customize the "find teammates" task type?
4. How do we handle job failure/timeout?

## Next Steps

1. Install SDK: `npm i @earn-fi/agent-client`
2. Register agent on EarnFi
3. Test with devnet USDC
4. Build lobby UI prototype
