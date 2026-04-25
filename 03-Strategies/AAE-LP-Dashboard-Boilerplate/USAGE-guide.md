# AAE LP Dashboard — AVAX/USDC Example

**Source:** LFJ/Trader Joe yield farm tracker (Mar 31, 2026)  
**Modified:** AAE boilerplate with config-driven structure  
**Purpose:** Multi-chain ready template for AgentFi Agent (AAE)

---

## How It Works

1. **Config-driven** — Load `config.example.json` → auto-generate HTML
2. **Multi-chain ready** — Change `chain.id` and `pool.platform` → works on any chain
3. **Agent-aware** — `agent_actions.trigger_conditions` auto-generates claim/compound buttons

---

## Usage

### 1. Copy the template

```bash
cp index.html dist/aae-dashboard-{chain}-{pool}.html
```

### 2. Update config

Edit `config.example.json` with your pool addresses and strategy settings.

### 3. Generate custom HTML (optional)

 ```bash
# Future: Use a simple script to inject JSON config into HTML template
# Or deploy as a static site (Vercel/Netlify) with config API
 ```

---

## Current Config Settings (Live as of Mar 31, 2026)

| Setting | Value |
|---------|-------|
| `chain.id` | `avax` |
| `pool.address` | `0x864d4e5ee7318e97483db7eb0912e09f161516ea` |
| `pool.platform` | `LFJ (Trader Joe)` |
| `strategy` | `CURVE` (149 bins) |
| `position.total_usd` | `$31.16` |
| `rewards.claimable` | `0.12782 AVAX ($1.13)` |
| `fees.last_24h_usd` | `$0.3331` |
| `dca.weekly` | `$50–100` |
| `dca.conviction` | `HIGH` |

---

## Key Differences from Original

| Feature | Original | AAE Template |
|---------|----------|--------------|
| Data source | Hardcoded snapshot | Live fetch via Chainlink + DexScreener |
| Chain | Avalanche only | Configurable (Ethereum/Base/Solana) |
| Agent triggers | Manual review | Auto-generated from config |
| DCA progress | Static text | Animated progress bars |
| Ghost simulation | None | Toggle (simulated vs live) |

---

## Tags  
`#aae #dashboard #lp-tracking #defi #yield-farming #frontend #template #boilerplate #multi-chain`
