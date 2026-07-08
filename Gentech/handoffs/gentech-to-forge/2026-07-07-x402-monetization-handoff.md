# Gentech → Forge Handoff — x402 Gateway Monetization

**From:** Gentech (VPS)
**To:** Forge (Desktop)
**Created:** July 7, 2026, 1:35 PM UTC
**Priority:** HIGH — Blocks first transaction

---

## 🎯 Goal

Get first live transaction on x402 gateway.

**Current status:** $0/day → Target: $50/day ($1,500/month)

---

## ✅ What Gentech Did (Complete)

### Documentation (3 files, 2,100+ lines)
| File | Purpose | Location |
|------|---------|----------|
| `GETTING-STARTED.md` | Complete API guide | `10-Labs/x402-gateway/GETTING-STARTED.md` |
| `EXAMPLES.md` | Python + JS + cURL examples | `10-Labs/x402-gateway/EXAMPLES.md` |
| `X-ANNOUNCEMENT.md` | 9-tweet launch thread | `10-Labs/x402-gateway/X-ANNOUNCEMENT.md` |

### Python SDK (3 files, 400+ lines)
| File | Purpose | Location |
|------|---------|----------|
| `sdk/gentech_x402.py` | Full async/sync client | `10-Labs/x402-gateway/sdk/gentech_x402.py` |
| `sdk/pyproject.toml` | PyPI package config | `10-Labs/x402-gateway/sdk/pyproject.toml` |
| `sdk/README.md` | SDK quick start | `10-Labs/x402-gateway/sdk/README.md` |

### Commits
```
dd5026aa: Add x402 gateway documentation + Python SDK
1d4afc32: Add X announcement draft + Day 1 monetization status
```

All pushed to `main` branch.

---

## 🚧 What's Blocking Transactions

| Issue | Severity | Who Fixes? |
|-------|----------|------------|
| **No testnet environment** | 🔴 CRITICAL | Forge |
| **No PyPI package** | 🔴 CRITICAL | Forge |
| **No public announcement** | 🟡 MEDIUM | Jordan (back home) |
| **No API directory listings** | 🟡 MEDIUM | Jordan (back home) |

---

## 🔧 Forge Tasks (Priority Order)

### Task 1: Add Testnet Support (1 hour)

**Why:** Developers won't pay real USDC for testing. Need Sepolia/Devnet endpoints.

**Steps:**

1. **Add testnet config to `10-Labs/x402-gateway/worker.js`**

```javascript
// Add after line 29 (after mainnet constants)
const USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dcCF7";
const USDC_SOL_DEVNET = "..."  // Find devnet USDC address
const USDC_AVAX_FUJI = "0x5425890298aed601595a70AB815c96711a31Bc65";

const NET_BASE_SEPOLIA = "eip155:11155111";
const NET_SOL_DEVNET = "solana:EtWTRABZaYq6iMFeY7ouHTXzYsTJQzJAknhfty47sFpU";
const NET_AVAX_FUJI = "eip155:43113";

const AI_MODEL = "@cf/meta/llama-3.1-8b-instruct-fast";
const TESTNET_MODE = env.TESTNET_MODE === "1";  // Toggle with env var

// Create separate route configs for testnet
const TESTNET_ROUTES = {};
for (const [path, r] of Object.entries(ROUTES)) {
  const resource = `https://gentech-x402-testnet.jordanjones0902.workers.dev${path}`;
  TESTNET_ROUTES[path] = {
    resource,
    description: `${r.desc} (TESTNET — free USDC from faucet)`,
    mimeType: "application/json",
    accepts: [
      { scheme: "exact", price: r.price, network: NET_BASE_SEPOLIA, payTo: EVM_WALLET, asset: USDC_BASE_SEPOLIA, maxTimeoutSeconds: 300 },
    ],
  };
}

// Update x402 middleware to use TESTNET_ROUTES when TESTNET_MODE=1
let paymentMiddlewareInstance = null;

app.use("*", async (c, next) => {
  if (!paymentMiddlewareInstance) {
    const resourceServer = createResourceServer(c.env);
    const routesToUse = TESTNET_MODE ? TESTNET_ROUTES : x402Routes;
    paymentMiddlewareInstance = paymentMiddleware(
      routesToUse,
      resourceServer,
      undefined,
      undefined,
      true, // syncFacilitatorOnStart
    );
  }
  return await paymentMiddlewareInstance(c, next);
});
```

2. **Create testnet wrangler config**

```bash
cp 10-Labs/x402-gateway/wrangler.toml 10-Labs/x402-gateway/wrangler-testnet.toml
```

Edit `wrangler-testnet.toml`:
```toml
name = "gentech-x402-testnet"
main = "worker.js"
compatibility_date = "2025-06-01"
compatibility_flags = ["nodejs_compat"]

[vars]
TESTNET_MODE = "1"
WALLET_ADDRESS = "0x7ebff188f2Eba16518C02864589b1403a5d1296a"

[ai]
binding = "AI"

[[kv_namespaces]]
binding = "RATE_LIMIT_KV"
# Reuse mainnet KV for now
id = "de2f4543ecef44d191fc617024473c99"
```

3. **Deploy testnet worker**

```bash
cd /root/vaults/gentech/10-Labs/x402-gateway
npx wrangler deploy --config wrangler-testnet.toml
```

4. **Verify testnet deployment**

```bash
curl https://gentech-x402-testnet.jordanjones0902.workers.dev/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "gentech-x402-gateway",
  "version": "6.0.0",
  "mode": "testnet",
  ...
}
```

5. **Create testnet funding guide**

Create `10-Labs/x402-gateway/TESTNET-FAUCET.md`:

```markdown
# Testnet USDC Faucets

## Base Sepolia
1. Go to https://faucet.quicknode.com/base
2. Paste your wallet address
3. Claim 0.1 USDC (enough for 100 calls)

## Solana Devnet
1. Go to https://solfaucet.com/
2. Paste your Solana address
3. Claim devnet USDC

## Avalanche Fuji
1. Go to https://faucet.avax.network/
2. Select Fuji testnet
3. Claim testnet USDC

## How to Use

```bash
# Use testnet gateway
export GENTECH_GATEWAY_URL="https://gentech-x402-testnet.jordanjones0902.workers.dev"
```
```

**Success criteria:**
- ✅ Testnet worker deployed
- ✅ `/health` returns `mode: "testnet"`
- ✅ Can call paid endpoint with testnet USDC
- ✅ Testnet faucet guide created

---

### Task 2: Publish Python SDK to PyPI (2 hours)

**Why:** Developers need `pip install gentech-x402` to use the SDK easily.

**Steps:**

1. **Navigate to SDK directory**

```bash
cd /root/vaults/gentech/10-Labs/x402-gateway/sdk
```

2. **Install build tools**

```bash
pip install build twine
```

3. **Build the package**

```bash
python -m build
```

This creates `dist/` directory with:
- `gentech-x402-1.0.0.tar.gz`
- `gentech_x402-1.0.0-py3-none-any.whl`

4. **Check the package**

```bash
twine check dist/*
```

Should see: `Checking dist/gentech-x402-1.0.0.tar.gz: PASSED`

5. **Upload to PyPI**

```bash
twine upload dist/*
```

You'll be prompted for:
- PyPI username
- PyPI password (or API token)

6. **Verify installation**

```bash
pip install gentech-x402
python -c "import gentech_x402; print('SDK installed successfully')"
```

7. **Test the SDK**

```python
# Test with testnet gateway
import asyncio
from gentech_x402 import GenTechGateway

async def test():
    # Use testnet gateway URL
    config = GatewayConfig(gateway_url="https://gentech-x402-testnet.jordanjones0902.workers.dev")
    gateway = GenTechGateway(private_key="your-testnet-wallet-key", config=config)

    # Health check (free)
    health = await gateway.health()
    print("Health:", health)

    # Try a paid endpoint with testnet USDC
    result = await gateway.games_search("test")
    print("Result:", result)

asyncio.run(test())
```

8. **Update `day1-monetization-status.md`**

Add to Phase 4 section:
```markdown
### Phase 4: SDK Publication ✅ COMPLETE
- Python SDK published to PyPI
- Install: `pip install gentech-x402`
- Verified with testnet payment
```

**Success criteria:**
- ✅ Package built successfully
- ✅ Published to PyPI
- ✅ Can `pip install gentech-x402`
- ✅ Can call endpoint with SDK + testnet payment

---

### Task 3: Update Documentation URLs (15 min)

After testnet deployment, update docs to reference testnet:

1. **Update `GETTING-STARTED.md`**

Add testnet section after "Testing":

```markdown
## 🧪 Testing

### Testnet URLs

We provide a testnet version of the gateway for development and testing.

**Base URL:**
```
https://gentech-x402-testnet.jordanjones0902.workers.dev
```

**How to get testnet USDC:**
- Base Sepolia: https://faucet.quicknode.com/base (0.1 USDC)
- Avalanche Fuji: https://faucet.avax.network/ (1 USDC)
- Solana Devnet: https://solfaucet.com/ (100 USDC)

See [TESTNET-FAUCET.md](./TESTNET-FAUCET.md) for detailed instructions.

**Testnet example:**
```python
config = GatewayConfig(gateway_url="https://gentech-x402-testnet.jordanjones0902.workers.dev")
gateway = GenTechGateway(private_key="your-testnet-key", config=config)
```

**Note:** Testnet uses the same pricing as mainnet, but USDC has no real value.
```

2. **Update `sdk/README.md`**

Add testnet section after "Quick Start":

```markdown
### Use Testnet

```python
from gentech_x402 import GenTechGateway, GatewayConfig

config = GatewayConfig(
    gateway_url="https://gentech-x402-testnet.jordanjones0902.workers.dev"
)
gateway = GenTechGateway(private_key="your-testnet-key", config=config)

result = await gateway.games_search("test")
```
```

3. **Commit changes**

```bash
cd /root/vaults/gentech
git add 10-Labs/x402-gateway/TESTNET-FAUCET.md 10-Labs/x402-gateway/GETTING-STARTED.md 10-Labs/x402-gateway/sdk/README.md
git commit -m "Add testnet support + faucet guide

- TESTNET-FAUCET.md: Faucet URLs for Base Sepolia, Avax Fuji, Solana Devnet
- GETTING-STARTED.md: Testnet section with example
- sdk/README.md: Testnet config example

Testnet gateway: https://gentech-x402-testnet.jordanjones0902.workers.dev"
git push origin main
```

---

## 📋 Forge Checklist

- [ ] Add testnet constants to `worker.js`
- [ ] Create `TESTNET_ROUTES` config
- [ ] Add `TESTNET_MODE` env var support
- [ ] Create `wrangler-testnet.toml`
- [ ] Deploy testnet worker
- [ ] Verify `/health` returns `mode: "testnet"`
- [ ] Create `TESTNET-FAUCET.md`
- [ ] Build Python SDK: `python -m build`
- [ ] Check package: `twine check dist/*`
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Verify install: `pip install gentech-x402`
- [ ] Test SDK with testnet payment
- [ ] Update documentation with testnet URLs
- [ ] Commit and push changes
- [ ] Update `day1-monetization-status.md`

---

## 📊 What Jordan Will Do (Back Home)

### Phase 5: Discovery & Announcement

1. **Post X announcement**
   - Use `X-ANNOUNCEMENT.md` as template
   - Schedule 9-tweet thread
   - Tag relevant accounts (@x402protocol, @CoinbaseWallet, etc.)

2. **Submit to API directories**
   - RapidAPI
   - Postman
   - ProgrammableWeb
   - AnyAPI

3. **Create GitHub repo for gateway code**
   - Extract `10-Labs/x402-gateway/` to separate repo
   - Add README with badges (PyPI, License, Tests)
   - Add issues/PR templates

4. **Create Postman collection**
   - Import OpenAPI spec
   - Add examples for each endpoint
   - Publish to Postman public workspace

5. **Engage with developer communities**
   - Reddit: r/ethdev, r/web3, r/python
   - Discord: x402 protocol server, DeFi servers
   - Hacker News: Show HN post

---

## 🎯 Success Metrics

### Immediate (24-48h)
- ✅ Testnet worker live
- ✅ PyPI package published
- ✅ First testnet transaction (any endpoint)

### Short-term (1-2 weeks)
- 🎯 10+ developers install SDK (`pip install gentech-x402`)
- 🎯 50+ testnet transactions
- 🎯 First mainnet transaction (real payment)

### Medium-term (1 month)
- 🎯 $100/day revenue
- 🎯 Listed on 3+ API directories
- 🎯 100+ unique wallets using gateway

---

## 📞 Support

**If Forge runs into issues:**

- x402 docs: https://x402.org/docs
- Cloudflare Workers: https://developers.cloudflare.com/workers/
- PyPI publishing: https://packaging.python.org/tutorials/packaging-projects/

**Reach out to Gentech if:**
- Cloudflare deployment fails
- x402 verification errors
- PyPI upload fails
- Testnet payment doesn't work

---

## 📝 Next Status Update

After completing Task 1 (testnet) + Task 2 (PyPI), Forge should:

1. Update `day1-monetization-status.md` with completion status
2. Commit and push changes
3. Report back to Gentech with:
   - Testnet URL (deployed successfully?)
   - PyPI package name (published successfully?)
   - Any blockers or issues

---

**Handoff Complete.** Forge has everything needed to get first transaction.

**Estimated Forge time:** 3 hours total (1h testnet + 2h PyPI)

**Jordan's tasks (back home):** Discovery, announcement, API directory listings

**Goal:** First testnet transaction within 24h. First mainnet transaction within 48h.