# x402 Gateway Deploy Runbook — July 6, 2026

**Purpose:** Finish deploying the x402 gateway after the kimi-k2.7-code AUDIT+FIX patch.

**Cloudflare Account ID:** `a618b777aff85c5360bd847629385b4d`

**Token permission requirements:**
Your API token must include:
- **Account → Cloudflare Workers Scripts:Edit**
- **Account → Workers KV Storage:Edit**
- *(Recommended)* **User → User Details:Read** (removes the `wrangler whoami` warning)

**Authentication gotcha:** Both supplied tokens authenticate for `wrangler whoami` but fail with **Authentication error [code: 10000]** on KV creation. Update the token permissions or create a new one.

**For Gentech VPS:** The second token (`...14cdf`) is stored in the Obsidian vault at `00-HQ/cloudflare-token-for-gentech.md` (not committed to Git).
- CDP API keys: `apiKeyId`, `apiKeySecret`, `walletSecret`
- Wrangler CLI installed (already present in `10-Labs/x402-gateway/`)

---

## Step 1: Export Cloudflare Credentials

```bash
export CF_API_TOKEN="your-token-here"
export CF_ACCOUNT_ID="your-account-id-here"
```

Verify:
```bash
cd 10-Labs/x402-gateway
npx wrangler whoami
```

---

## Step 2: Create KV Namespace

```bash
npx wrangler kv:namespace create RATE_LIMIT_KV
```

Copy the returned namespace ID and paste it into `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "RATE_LIMIT_KV"
id = "paste-id-here"
```

---

## Step 3: Set CDP Secrets

The hardcoded CDP keys have been removed. Set them as Wrangler secrets:

```bash
npx wrangler secret put CDP_API_KEY_ID
npx wrangler secret put CDP_API_KEY_SECRET
npx wrangler secret put CDP_WALLET_SECRET
```

When prompted, paste each value from the old `worker.js` or from the CDP portal.

---

## Step 4: Deploy

```bash
npx wrangler deploy
```

---

## Step 5: Verify

### Free endpoints
```bash
curl https://gentech-x402-gateway.jordanjones0902.workers.dev/health
curl https://gentech-x402-gateway.jordanjones0902.workers.dev/pricing
curl https://gentech-x402-gateway.jordanjones0902.workers.dev/openapi.json
```

### Paid endpoint (should return 402)
```bash
curl -i "https://gentech-x402-gateway.jordanjones0902.workers.dev/api/games/search?q=test"
```

Expected:
- HTTP `402 Payment Required`
- `PAYMENT-REQUIRED` or similar header
- Response body with payment instructions

---

## Step 6: Optional — Custom Domain

Uncomment in `wrangler.toml`:

```toml
[[routes]]
pattern = "api.gentechlabs.net"
custom_domain = true
```

Then redeploy:
```bash
npx wrangler deploy
```

Requires Cloudflare API token with **DNS:Edit** permission.

---

## Step 7: Update Forge Handoff Response

After deploy, edit `handoffs/forge-to-gentech/2026-07-06-forge-response.md` and mark:
- ✅ x402 API Deployed
- ✅ KV namespace created
- ✅ CDP secrets set

Commit and push:
```bash
cd gentech-vault-new
git add .
git commit -m "Forge: x402 gateway deployed with secrets + KV rate limiting"
git push origin main
```

---

## Troubleshooting

### `You are not authenticated`
You forgot `CF_API_TOKEN` or it's invalid. Re-export and run `npx wrangler whoami`.

### `No KV namespace with ID ...`
The placeholder ID in `wrangler.toml` wasn't replaced. Run Step 2 and paste the real ID.

### `facilitator getSupported failed`
CDP secrets are missing or wrong. Run Step 3 again.

### Paid endpoint returns 500 instead of 402
Check `npx wrangler tail` for error logs. Likely facilitator auth or KV issue.

---

*Runbook created: 2026-07-06 by Forge (kimi-k2.7-code)*
