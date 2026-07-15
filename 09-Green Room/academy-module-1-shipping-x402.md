# 🎓 GenTech Academy — Module 1
## Ship a Compliant x402 API

**Your API. Paid in minutes. No API keys. No accounts. Just x402.**

---

## Overview

Module 1 teaches you to build, test, and deploy an API that accepts payments through the **x402 protocol** — the open standard for machine-to-machine payments over HTTP, now backed by the Linux Foundation (AWS, Google, Visa, Mastercard, Coinbase, Circle, Ripple as founding members).

**By the end of this module you will:**
- Set up a paid API endpoint in under 15 minutes
- Test it against the official GenTech Test Harness
- Pass the x402 Compliance Checker (42 checks)
- Be indexed on x402scan.com for agent discovery
- Be ready to contribute fixes to the x402 ecosystem

**Who this is for:**
- Developers who want to monetize APIs for AI agents
- Builders in the agent economy (Farcaster, Solana, Base)
- Anyone who wants to contribute to the x402 open standard

---

## The Stack

| Tool | Purpose | Cost |
|------|---------|------|
| **GenTech Test Harness** | Reference endpoint — test your client against it | **Free** |
| **x402 Compliance Checker** | 42-point scan of your API | Free scan / $19 fix |
| **AgentCash Router** | Drop-in Node.js router (auto-handles 402, settlement, discovery) | Open source |
| **x402scan.com** | Public index of compliant x402 APIs | Free |
| **GenTech Fix PR** | We fix your open-source API for you | $99-299 |

---

## Module Syllabus

### Part 1: Understanding x402 (30 min)

**Objective:** Learn the protocol flow and v2 format spec.

**Concepts:**
- What is the 402 Payment Required status?
- The three-step flow: client → 402 challenge → sign → retry → success
- x402 v2 format: `x402Version: 2`, `scheme: exact`, CAIP-2 networks, `amount` as string
- The `accepts` array — offering multiple settlement options
- How the GoPlausible facilitator handles verification + settlement

**Read:** [x402 Protocol Spec](https://x402.org)
**Test:** Curl the GenTech Test Harness:
```bash
curl -i https://test.api.gentechlabs.net/hello
# → 402 with base64 Payment-Required header
```

**Deliverable:** Explain the 402 flow in your own words. Paste the decoded challenge from the Test Harness.

---

### Part 2: Build Your First x402 Endpoint (45 min)

**Objective:** Deploy a working paid API endpoint.

**Option A — AgentCash Router (recommended, 5 min):**
```bash
npx agentcash-router create my-paid-api
cd my-paid-api
# Add routes with .paid('0.01').handler(fn)
npm run dev
```

**Option B — Cloudflare Worker (10 min):**
```bash
npm create cloudflare@latest my-x402-api
# Add the 402 handler + v2 challenge payload
npx wrangler deploy
```

**Option C — Express / Hono / any Node.js framework:**
```bash
npm install @agentcash/router
# OR manual implementation using @x402/express
```

**Checklist:**
- [ ] Returns HTTP 402 on unpaid requests
- [ ] Includes `Payment-Required` header (base64-encoded JSON v2)
- [ ] Includes `x402Version: 2` in the challenge payload
- [ ] Uses `accepts` array (not flat payment fields)
- [ ] Specifies `scheme: exact`, CAIP-2 `network`, `amount` as string, `asset`, `payTo`, `maxTimeoutSeconds`
- [ ] Includes `.well-known/x402` discovery endpoint
- [ ] Includes `openapi.json` with pricing extensions
- [ ] Accepts `X-Payment-Proof` header on retry

**Deliverable:** Your endpoint is live on a public URL. Run the GenTech Compliance Checker against it:
```bash
pip install x402-compliance-checker  # coming soon
x402-check https://your-api.com/your-endpoint
```

---

### Part 3: Pass the Compliance Checker (30 min)

**Objective:** Get a green check on all 42 compliance checks.

**What the checker verifies:**
1. **Status code** — Returns 402 (not 400, 401, or 403)
2. **Header format** — `Payment-Required` header is present and base64-encoded
3. **JSON validity** — Decoded payload is valid JSON
4. **Version field** — `x402Version` is exactly `2`
5. **Accepts array** — Not `paymentRequirements` (v1), not flat fields
6. **Scheme** — `scheme` is lowercase `"exact"`
7. **Network** — Uses CAIP-2 format (e.g. `eip155:84532`, `solana:...`)
8. **Amount** — String, not number
9. **Asset** — Lowercase hex or valid identifier
10. **PayTo** — Present and valid format
11. **maxTimeoutSeconds** — Present, integer, >= 30, <= 600
12. **Resource object** — URL, description, mimeType
13. **CORS headers** — `Access-Control-Allow-Origin: *`
14. **Discovery** — `/.well-known/x402` returns valid metadata
15. **OpenAPI** — `openapi.json` includes pricing extensions
... and 27 more checks

**Common failures and fixes:**
| Issue | Fix |
|-------|-----|
| Returns 400 instead of 402 | Change status code to 402 |
| Uses `paymentRequirements` instead of `accepts` | Rename the key |
| `amount` is a number like `1000` | Wrap as string `"1000"` |
| Network is `"base-sepolia"` (human name) | Use CAIP-2: `"eip155:84532"` |
| Missing `/.well-known/x402` | Add simple JSON response at that path |
| Header is `X-Payment` (v1, capital X) | Use lowercase `Payment-Required` |

**Deliverable:** Screenshot of all 42 checks passing.

---

### Part 4: Get Indexed on x402scan (15 min)

**Objective:** Make your API discoverable by every x402 agent.

**Steps:**
1. Submit your API to [x402scan.com](https://x402scan.com) (or it auto-discovers via `/.well-known/x402`)
2. Ensure your `openapi.json` includes the `x402` extension field
3. Verify your endpoint appears in the x402scan index

**Deliverable:** Your API is listed on x402scan.com.

---

### Part 5 (Bonus): "Fix People Up" (60 min)

**Objective:** Contribute back to the x402 ecosystem by fixing an open-source API.

The GenTech PR Scout scans GitHub daily for x402 APIs that need fixes. Choose from open bounties:

| Repo | Issue | Bounty |
|------|-------|--------|
| marlinprotocol/x402-gateway | README outdated | Documented fix |
| brave-experiments/x402 | v1 header format | $50 |
| smartcontractkit/x402-cre-price-alerts | SDK migration | $100 |

**Deliverable:** One merged PR to an open-source x402 repo.

---

## Pricing

| Tier | What you get | Price |
|------|-------------|-------|
| **Free** | Full course, test harness, compliance checker — self-guided | **$0** |
| **Pro** | Everything above + certificate + priority support | **$19** |
| **Enterprise** | Everything + custom onboarding + 1 Fix PR for your repo | **$50** |

---

## Ready to Ship

GenTech Academy is built on the same stack we teach. Every tool in this module is something we use daily.

**Start here:**
```bash
curl https://test.api.gentechlabs.net/
```

**Questions?** Join the GenTech Labs Discord or DM @ProtoJay4789.

---

*GenTech Academy — Tough love for the agent economy.*
