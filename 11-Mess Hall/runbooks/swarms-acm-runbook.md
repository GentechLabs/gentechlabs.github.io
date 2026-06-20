# Swarms ACM Runbook — Saturday Execution

**Deadline:** May 27, 2026
**Goal:** Token launch → marketplace publish → demo → submit

## Pre-Flight Checklist (Do First)

### 1. SOL Balance Check
```bash
# Check Solana wallet balance
solana balance
```
- **Need:** ≥0.04 SOL for token launch
- **If below:** Drip from faucet or transfer from main wallet
- **Faucet:** https://solfaucet.com/ or https://faucet.solana.com/

### 2. API Key Verification
```bash
# Verify Swarms API key works
curl -s https://swarms.world/api/v1/agents \
  -H "Authorization: Bearer $SWARMS_API_KEY" | head -20

# Verify OpenRouter key has credits
python3 -c "
import os, urllib.request, json
req = urllib.request.Request('https://openrouter.ai/api/v1/auth/key',
    headers={'Authorization': f'Bearer {os.environ[\"OPENROUTER_API_KEY\"]}'})
with urllib.request.urlopen(req) as resp:
    print(json.loads(resp.read()))
"
```

### 3. Codebase Status
- **Location:** `/root/swarms-acm-hackathon/`
- **Files:** `lp_monitor_agent.py`, `requirements.txt`, `README.md`
- **Status:** 7 tools verified live, agent loop works with free tier
- **Git:** 2 commits, clean state

---

## Phase 1: Token Launch (30 min)

### Step 1: Prepare Solana Keypair
```bash
# Check if keypair exists
ls ~/.config/solana/id.json 2>/dev/null || solana-keygen new --no-bip39-passphrase
```

### Step 2: Launch Token via Frenzy Mode API
```python
import os, json, urllib.request

LAUNCH_URL = "https://swarms.world/api/token/launch"

with open(os.path.expanduser("~/.config/solana/id.json")) as f:
    private_key = json.load(f)

payload = {
    "name": "DeFi LP Monitor Agent",
    "description": "AI-powered concentrated liquidity position monitor. Track impermanent loss, fee efficiency, range status, and get rebalance alerts in real time. Supports Avalanche, Ethereum, Base, and other EVM chains.",
    "ticker": "LPMON",
    "private_key": private_key,
    "fee_selection": "frenzy",
    "quote_mint": "SOL",
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
    LAUNCH_URL, data=data,
    headers={"Authorization": f"Bearer {os.environ['SWARMS_API_KEY']}",
             "Content-Type": "application/json"},
    method="POST",
)

with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read())
    print(json.dumps(result, indent=2))
```

**Expected response:**
```json
{
  "success": true,
  "id": "uuid-here",
  "listing_url": "https://swarms.world/agent/uuid-here",
  "tokenized": true,
  "token_address": "0x...",
  "pool_address": "0x..."
}
```

**Save the `listing_url` and `token_address` — needed for submission.**

### Error Recovery
- **401 Invalid API key:** Get new key from swarms.world/platform/api-keys
- **400 Insufficient SOL:** Fund wallet with ≥0.04 SOL, retry
- **Timeout:** Increase to 120s, retry once

---

## Phase 2: Agent Loop Test (15 min)

```bash
cd /root/swarms-acm-hackathon
pip install -r requirements.txt

# Test single tool (no LLM needed)
python3 -c "from lp_monitor_agent import fetch_token_prices; print(fetch_token_prices('AVAX,USDC'))"

# Full agent loop (needs LLM key)
python3 lp_monitor_agent.py --query "Check AVAX/USDC pool health"
```

**If OpenRouter has no credits:**
- Use free model: `openrouter/deepseek/deepseek-v4-flash:free`
- Or set `max_loops=1` to skip planning phase

---

## Phase 3: Demo Recording (30 min)

### Demo Script (2-3 min)
```
[0:00-0:15] Hook
"AI agents need to monitor their DeFi positions just like humans do. 
This is LP Monitor — an autonomous agent that tracks impermanent loss, 
fee yields, and alerts you before your position goes out of range."

[0:15-0:45] Problem
"Liquidity providers lose money to impermanent loss every day. 
Most tools are dashboards — you have to check them. 
This agent monitors for you and speaks up when action is needed."

[0:45-1:45] Demo Walkthrough
1. Show agent responding to "Check my LP position health"
2. Show price fetch tool returning live data
3. Show IL calculation with HODL comparison
4. Show rebalance alert (simulate out-of-range scenario)
5. Show pool analysis with TVL, volume, APR

[1:45-2:15] Architecture
"Built with Swarms ATP Protocol. Tokenized via Frenzy Mode. 
7 signal tools — price fetching, pool analysis, IL calculation, 
trend detection, fee yield, sentiment analysis, and alert monitoring. 
Listed on Swarms Marketplace under Finance + x402."

[2:15-2:30] Close
"LP Monitor — your position, watched 24/7. 
Available now on swarms.world."
```

### Recording Options
1. **Terminal recording:** `script -q demo.txt && python3 lp_monitor_agent.py --query "..." && exit`
2. **Screen recording:** OBS or Windows Win+G, show terminal output
3. **Hybrid:** Terminal output + overlay architecture diagram

---

## Phase 4: Marketplace Publish (Jordan's Browser)

**This MUST be done from Jordan's browser** — swarms.world blocks server-side requests.

1. Navigate to swarms.world → "List your agent"
2. Fill in:
   - **Name:** DeFi LP Monitor Agent
   - **Description:** (from token launch payload)
   - **Category:** Finance
   - **Tags:** defi, liquidity-pool, impermanent-loss, rebalance-alerts
   - **Price:** $9.99 or free tier
   - **Model:** `openrouter/<provider>/<model>` + set OPENROUTER_API_KEY
3. Click Publish
4. Verify listing appears on marketplace

**Pre-fill data for Jordan:** All fields ready, just needs human click.

---

## Phase 5: Submission (15 min)

### Required Materials
- [ ] Token launched (listing_url saved)
- [ ] Agent loop verified (screenshot or recording)
- [ ] Demo video (≤5 min)
- [ ] GitHub repo: https://github.com/ProtoJay4789/swarms-acm-hackathon
- [ ] Marketplace listing live

### Submission URL
- https://docs.swarms.ai/docs/marketplace/acm-hackathon
- Or follow submission instructions from hackathon page

---

## Blockers & Escalations

| Blocker | Solution | Time |
|---------|----------|------|
| No SOL in wallet | Faucet drip or transfer | 5 min |
| API key invalid | Regenerate at swarms.world | 2 min |
| OpenRouter no credits | Use free model or add $5 | 5 min |
| Publish blocked (Cloudflare) | Hand off to Jordan | 5 min |
| Token launch timeout | Retry with 120s timeout | 2 min |

---

## Quick Reference

- **SOL balance needed:** ≥0.04 SOL
- **API endpoint:** POST https://swarms.world/api/token/launch
- **Fee mode:** frenzy (2x bonding curve fees + leaderboard)
- **Quote mint:** SOL (default) or USDC
- **Agent repo:** /root/swarms-acm-hackathon/
- **Portfolio:** ProtoJay4789.github.io (update after launch)
