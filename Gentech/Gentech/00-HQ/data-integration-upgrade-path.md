# Data Integration Upgrade Path — Mock → Real

**Created**: July 5, 2026
**Why**: APIs are live with mock data; need documented path to real data sources

---

## Current State

| API | Port | Data Source | Status |
|-----|------|-------------|--------|
| Agent Registration | 8001 | Direct blockchain calls | ✅ Production-ready |
| DeFi Intelligence | 8002 | Mock data | ⚠️ Needs BlockRun |
| Agent Search | 8003 | Mock data | ⚠️ Needs BlockRun |

**Revenue APIs Still Work**: x402 payments function regardless of data source.

---

## BlockRun Integration Plan

### Phase 1: Account Setup (When BlockRun is back up)

1. **Create fresh BlockRun account**
   - Sign up at https://blockrun.io
   - Use new email (avoid lost key issues)
   - Enable 2FA

2. **Generate API key**
   - Navigate to Dashboard → API Keys
   - Create new key with: read-only access, no expiration
   - Format: `sk_XXXXXXX`

3. **Secure storage**
   ```bash
   # NEVER commit to git
   # Store in vault (encrypted note)
   # Add to .hermes profile environment
   ```

### Phase 2: Configure Integration

1. **Update `.env` files**:
   ```bash
   # DeFi Intelligence API
   echo "BLOCKRUN_API_KEY=sk_XXXXXXX" >> /root/vaults/gentech/builds/defi-intelligence-api/.env

   # Agent Search API
   echo "BLOCKRUN_API_KEY=sk_XXXXXXX" >> /root/vaults/gentech/builds/agent-search-api/.env
   ```

2. **Add to vault documentation**:
   - Update `builds/defi-intelligence-api/README.md` with API key setup
   - Update `builds/agent-search-api/README.md` with API key setup

3. **Document key rotation**:
   - Create `11-Mess Hall/blockrun-api-key-rotation.md`
   - Add to `skills/api-key-rotation.md`

### Phase 3: Wire Real Data

1. **DeFi Intelligence API** (`builds/defi-intelligence-api/main.py`):
   - Replace mock data with BlockRun calls
   - Use `BLOCKRUN_BASE = "https://api.blockrun.io"`
   - Add auth header: `Authorization: Bearer ${BLOCKRUN_API_KEY}`

2. **Agent Search API** (`builds/agent-search-api/main.py`):
   - Replace mock agents with BlockRun agent registry
   - Query real agent profiles via BlockRun API
   - Add verification status from BlockRun

### Phase 4: Test & Deploy

1. **Test endpoints**:
   ```bash
   # DeFi Intel
   curl "http://localhost:8002/api/v1/defi/pools?protocol=aerodrome&chain=avalanche"

   # Agent Search
   curl "http://localhost:8003/api/v1/agents/search?category=defi"
   ```

2. **Verify real data**:
   - Check for actual pool addresses, not mock IDs
   - Verify agent profiles match BlockRun registry

3. **Deploy**:
   ```bash
   # Reload APIs
   cd /root/vaults/gentech/builds/defi-intelligence-api && ./deploy.sh
   cd /root/vaults/gentech/builds/agent-search-api && ./deploy.sh
   ```

---

## Backup Plan

If BlockRun remains unavailable:

### Option A: Alternative Data Sources

| API | Alternative | Implementation |
|-----|-------------|----------------|
| DeFi Intel | DefiLlama API | Replace BlockRun with DefiLlama |
| Agent Search | The Graph Protocol | Query subgraphs for agent data |

### Option B: Hybrid Approach

- Keep mock data for demo purposes
- Add "real data available" flag
- Allow users to toggle between modes
- Ship both to hackathon as "flexible architecture"

---

## Commit to Vault

```bash
cd /root/vaults/gentech
git add 00-HQ/data-integration-upgrade-path.md
git commit -m "Add data integration upgrade path — mock → real"
git push origin main
```

---

## Reference

- Build queue item #0: OKX AI Genesis Hackathon (deadline Jul 17)
- Build queue item #1: Cloudflare x402 Monetization Gateway (revenue rails)
- Skills: `api-key-rotation.md` (secure key management)