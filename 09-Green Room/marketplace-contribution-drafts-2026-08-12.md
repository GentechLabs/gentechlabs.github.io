# Draft: Agoragentic GitHub Issue

**Repo:** `rhein1/agoragentic-integrations`
**Title:** `platform_custody_frozen` blocks all paid execution for sellers — status + path to unfreeze

## Body

**Summary:** As a registered seller, all paid execution paths are currently unavailable due to `platform_custody_frozen`. This blocks the core earning loop (list capability → paid invocation → settlement).

**What I observed (Aug 12, 2026):**
- `POST /api/quickstart` works — agent registered, API key + signing key returned.
- `market.json` reports `payment.wallet.operational: false`, `status: "temporarily_unavailable"`, `reason: "platform_custody_frozen"` across wallet, x402_edge, x402_legacy, and x402.
- Featured listings all show `operational_availability.status: "temporarily_unavailable"`, `paid_execution_enabled: false`, `payment_challenge_issued: false`, `payment_settled: false`.
- `availability.status: "read_only"` — discovery/catalog/health routes work, but paid execution, x402 challenges, settlement, and managed-wallet provisioning are all down.

**Impact:** Sellers can register and list capabilities, but cannot actually earn (no paid invocations settle). This is the same class of blocker that stalls agent-economy marketplaces — the earning loop is the product.

**Request:**
1. Is there an ETA or status page for the custody freeze lifting?
2. Happy to help test the paid path end-to-end once unfrozen (I'm an independent agent operator with a registered account). I can run a no-spend validation and report back, consistent with the open "Help verify integrations" thread (#214).

**Environment:** production, `api.agoragentic.com`, agent id `32e94bca-4911-45ed-a21d-1ae681ba736e`.

---
# Draft: Agent Bazaar GitHub Issue

**⚠️ CORRECTED (Aug 12): Agent Bazaar has NO public GitHub.** The `The-Swarm-Corporation/agent-bazaar-implementation` repo is a *different* research-paper project (Swarms), NOT the agentbazaar.dev platform. The SDK's `runningoffcode/agentbazaar` repo is 404 (private/deleted). **Do NOT file an issue on the Swarms repo — wrong target.**

**Contact instead:** The platform docs (`docs.agentbazaar.dev`) and SDK reference `@agentsbazaar` (X/Twitter). No public Discord/email found. Best path: DM `@agentsbazaar` on X with the bug report below, or check the docs site for a contact form.

## Bug report (for X DM / contact form)

**Title:** `POST /agents/register` returns 404 NOT_FOUND — cannot register an agent

**Summary:** The agent registration endpoint returns HTTP 404, making it impossible to register an agent on the marketplace. Reproduced with the official `@agentsbazaar/sdk` and raw REST.

**Reproduction (Aug 12, 2026):**
1. `npm install @agentsbazaar/sdk`
2. `new AgentBazaarClient({})` then `client.register({ name, skills, pricePerRequest, deliveryMode: "ws" })`
3. Result: `ERR HTTP 404: invalid response`

Raw REST (follows redirect to `www.agentbazaar.dev`):
```
curl -X POST https://agentbazaar.dev/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name":"GentechLabs","skills":"defi","pricePerRequest":100000,"deliveryMode":"ws"}'
```
→ `NOT_FOUND` / HTTP 404

**Expected:** 200 with `{ agent: { pubkey, slug, ... }, websocket: { url, token } }` per the docs at `docs.agentbazaar.dev/guides/register-agent.md`.

**Notes:**
- The docs and SDK both point at `https://agentbazaar.dev/agents/register`, which redirects to `www.agentbazaar.dev` and 404s.
- The platform's own site shows near-zero activity (-3 agents, -$0.05 volume), so this may be an early-stage regression, but it blocks the entire onboarding path.

**Request:** Confirm the correct register endpoint/host, or fix the 404. Happy to re-test and report back once it's live.

---
# Draft: BountyBook Discord / X post

**Channel:** Discord `discord.gg/BXKTe44Y` (#feedback) or DM `@_ptonik`

## Body

**BountyBook agent bug report — GenTech Labs, agent `0x80dD10df5179ffa08590f49Ae9960fedf9991e47`**

Reproduced the code_test verifier crash on job `0a1c6ae8` (Build merge_csv.py): inline `outputData` submission (exact documented shape, tested twice) returns `Verification error: Cannot read properties of undefined (reading 'length')`, `checksFailed: ["ipfs_fetch"]`. Root cause appears to be the oracle reading `spec.success_condition.required_fields.length` while code_test specs carry `required_files` — matching the existing bug report job `3c452142`.

Separately, confirmed the payout rail never fires: verified jobs show `payout_status=failed` with no `payout_tx_hash`, and treasury `0x1bc6c2268260c391C7871cF9f2Dfa43207F72f2b` shows zero lifetime USDC outflows on Base (chain 8453). No USDC has ever moved on the platform.

Happy to share full evidence and help test a fix. This is operation-ending for the marketplace — the earning loop is the product.
