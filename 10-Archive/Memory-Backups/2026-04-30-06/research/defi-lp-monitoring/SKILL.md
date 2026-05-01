---
name: defi-lp-monitoring
description: "Set up automated DeFi LP position monitoring with tiered alert escalation (warning → red alert → all clear). Covers LFJ, concentrated liquidity pools, fee efficiency tracking, and cron job configuration."
tags: [defi, lp, monitoring, alerts, liquidity, avalanche, lfj]
triggers:
  - Setting up LP position monitoring
  - Configuring price range breakout alerts for liquidity pools
  - Tracking fee efficiency on LP positions
  - Creating cron jobs for DeFi pool surveillance
  - Adjusting LP alert thresholds or ranges
  - Fixing false "OUT OF RANGE" alerts after a rebalance
  - Syncing config files across multiple agent profiles
---

# DeFi LP Position Monitoring

Automated monitoring for concentrated liquidity positions (LFJ, Uniswap V3-style) with tiered alert escalation.

## Pattern: Alert Escalation

```
1. Price breaks range     → ⚠️ Light Warning (immediate)
2. Still broken 10+ min   → 🔴 Red Alert (escalation)
3. Price returns to range → ✅ All Clear (confirmation)
```

## Cron Job Template

### LP Monitor + Alerts

```yaml
Schedule: "*/10 6-23 * * *"  # Every 10 min, 6am-11pm
Deliver: telegram:<group_id>
```

**Prompt structure:**
1. **Price Check** — fetch current price, determine IN RANGE / ABOVE / BELOW
2. **Fee Efficiency** — `(24h Fees / Total Liquidity) × 100`
3. **Position Status** — balance, reserves, range distribution, USD value
4. **Alert Logic** — evaluate against thresholds, escalate if needed

### Key Parameters to Include

- Pool address (contract)
- Target range (lower_bound — upper_bound)
- Alert thresholds (light warning, red alert)
- Delivery target (Telegram group)

## Pool Address Management

Store pool addresses in memory for quick access:
```
LFJ AVAX/USDC (Avalanche): 0x864d4e5ee7318e97483db7eb0912e09f161516ea
```

## Output Format

```
📊 LP Monitor — [timestamp]

💰 Price: X.XX AVAX/USDC [IN RANGE / ABOVE / BELOW]
📈 Position: $XXX.XX (XX% USDC / XX% AVAX)

⚡ Fee Efficiency: X.XX%
💧 Liquidity: $X.XM | 24h Vol: $X.XM
🎯 7D APR: XX.XX%

⚠️ / 🔴 / ✅ [alert status if applicable]
```

## On-Chain Position Reading (LFJ V2.2)

**Never use hardcoded/calculated position values in monitoring prompts.** Always read on-chain data. Calculated positions drift from reality (e.g., after withdrawals, partial exits, or fee claims).

### LFJ V2.2 Contract Architecture (Avalanche)

| Contract | Address | Role |
|----------|---------|------|
| Pool (LB Pair) | `0x864d4e5ee7318e97483db7eb0912e09f161516ea` | Holds reserves, handles swaps. IS an ERC1155 "Liquidity Book Token" |
| Position Manager | `0x18556da13313f3532c54711497a8fedac273220e` | Manages positions. Users call `approveForAll` on pool with this as spender |
| WAVAX | `0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7` | Base token |
| USDC | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` | Quote token |

### Reading Wallet Balances (Direct RPC)

**Preferred approach: Direct RPC calls to Avalanche's public endpoint.** No API key needed, no rate limits, works offline. Use `eth_getBalance` for native AVAX and ERC-20 `balanceOf` for USDC.

```python
RPC_URL = "https://api.avax.network/ext/bc/C/rpc"

def rpc_call(to, data, label=""):
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "eth_call",
        "params": [{"to": to, "data": data}, "latest"], "id": 1
    }).encode()
    req = urllib.request.Request(RPC_URL, data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
    return result.get("result", "0x") if "error" not in result else None

def get_wallet_avax(wallet):
    """Native AVAX balance via eth_getBalance."""
    payload = json.dumps({
        "jsonrpc": "2.0", "method": "eth_getBalance",
        "params": [wallet, "latest"], "id": 1
    }).encode()
    req = urllib.request.Request(RPC_URL, data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode())
    return int(result["result"], 16) / 1e18

def get_wallet_erc20(wallet, token_address, decimals):
    """ERC-20 balance via balanceOf(address)."""
    # balanceOf(address) selector = 0x70a08231
    addr_padded = wallet.lower().replace("0x", "").zfill(64)
    data = "0x70a08231" + addr_padded
    result = rpc_call(token_address, data)
    return int(result, 16) / (10 ** decimals) if result else 0

# Usage:
# USDC = get_wallet_erc20(wallet, "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", 6)
# WAVAX = get_wallet_erc20(wallet, "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", 18)
```

**Why direct RPC over third-party APIs:**
- No API key required (Routescan, Snowtrace, DeBank all need keys or have rate limits)
- Works offline / in airgapped environments
- Avalanche's public RPC is reliable and free
- Universal pattern: same code works on any EVM chain (just change RPC_URL)

**Portfolio view structure (LP + wallet):**
```python
# 1. LP position (from config or on-chain query)
lp_avax, lp_usdc = get_lp_position(wallet, pool)

# 2. Wallet balances (direct RPC)
w_avax = get_wallet_avax(wallet)
w_usdc = get_wallet_erc20(wallet, USDC, 6)

# 3. Total portfolio
total_value = (lp_avax + w_avax) * price + lp_usdc + w_usdc
```

### Reading LFJ LP Positions

The pool uses **ERC1155** (not ERC721). Standard `balanceOf(address)` and `ownerOf(uint256)` revert. Use:
- `balanceOf(address _account, uint256 _id)` — ERC1155 style
- Position Manager's `getPosition(tokenX, tokenY, binStep, orderType, binId, positionId)` — returns `(liquidity, amount, withdrawn)`

**To read a user's position, you need:**
1. Their wallet address
2. Position Manager contract ABI (extractable from LFJ app JS bundle at `https://lfj.gg/static/js/main.*.js`)
3. The position ID(s) — obtainable from LFJ app frontend or by scanning `approveForAll` transactions

**Note:** Until you have the position NFT token ID, use config amounts as the LP portion and RPC wallet balances as the liquid portion. This gives a reasonable total portfolio view.

### Position Tracker File

Store actual balance in `~/.hermes/scripts/.lfj-position-tracker.json` with:
```json
{
  "actual_balance_usd": 135.09,
  "wallet_address": "0x...",
  "position_ids": [...],
  "last_updated": "ISO timestamp",
  "updated_by": "on-chain|manual"
}
```

## Config File Management (Post-Rebalance Checklist)

After ANY rebalance, range change, or position adjustment, update ALL copies of `.lfj-aae-config.json`. There are typically 3 locations:

| Location | Used By |
|----------|---------|
| `/root/.hermes/scripts/.lfj-aae-config.json` | Scripts run from main HOME |
| `/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json` | Gentech cron jobs |
| `/root/.hermes/profiles/yoyo/home/repos/gentech-vault/03-Strategies/scripts/.lfj-aae-config.json` | YoYo cron jobs |

Also update `/root/vaults/gentech/00-HQ/config/defi-lp-config.env` (env-format backup).

**To find all copies after a rebalance:**
```bash
find /root/.hermes -name ".lfj-aae-config.json" 2>/dev/null
```

**To verify the active config matches reality:**
```bash
HOME=/root python3 /root/.hermes/profiles/gentech/scripts/lp-position-reader.py 2>&1 | python3 -c "import sys,json; d=json.load(sys.stdin); p=d['position']; print(f\"Range: ${p['range_low']}-${p['range_high']} | In Range: {p['in_range']}\")"
```

## Pitfalls

- **Config drift across profile copies** — `.lfj-aae-config.json` exists in multiple profile directories. After a rebalance, the cron job reads from its profile's copy, which may still have the old range. This causes false "OUT OF RANGE" alerts when the position is actually in range. Always update ALL copies (see Config File Management above).
- **One-shot jobs get consumed on run** — if testing with `cronjob run`, recreate the job after as it may not persist
- **Script path mismatches break cron silently** — If the `script` field in `jobs.json` doesn't match the actual filename on disk, the cron agent reports "Script not found." Always verify `jobs.json` → `script` matches the real file in `~/.hermes/profiles/<profile>/scripts/`. Run the script manually with `HOME=/root/.hermes/profiles/<profile>/home` to confirm it resolves paths correctly. The config file (`.lfj-aae-config.json`) must also exist at the path `~/.hermes/scripts/.lfj-aae-config.json` relative to the profile's HOME.
- **Pool addresses are case-sensitive** — use checksummed addresses
- **Range updates require job prompt edits** — update the prompt with new bounds, don't just change a config value
- **High-frequency jobs (10 min) burn tokens** — ensure prompt is efficient, avoid redundant API calls
- **Alert state isn't persisted between runs** — each run is independent; for escalation tracking, write state to vault (e.g., `04-Entertainment/lp-alert-state.md`)
- **Hardcoded position values drift** — If a cron prompt says "position = X AVAX + Y USDC", it becomes stale after any on-chain action (withdraw, claim, rebalance). Always read on-chain or accept manual balance updates
- **LFJ V2.2 pool is ERC1155, not ERC721** — Standard `ownerOf(uint256)` and `balanceOf(address)` revert on the pool contract. Use ERC1155 `balanceOf(address, uint256)` or the Position Manager
- **Script copies must stay in sync** — When updating a monitoring script, copy to ALL locations: vault (`03-Strategies/scripts/`), `/root/.hermes/scripts/`, and `/root/.hermes/profiles/gentech/scripts/`. Cron jobs resolve scripts relative to their profile's HOME. Missing a copy = stale script running silently.

## Related

- CoinGecko API for price feeds
- LFJ subgraph for pool/position data
- Obsidian vault for alert state persistence
- `defi-dashboard-digest` — daily digest combining this LP data with market overview (complementary skill; use for scheduled digests, not real-time alerts)
- `defi-lp-regime-strategy` — strategy framework for deciding when to LP vs spot based on market regime (use for strategic decisions, not monitoring)
