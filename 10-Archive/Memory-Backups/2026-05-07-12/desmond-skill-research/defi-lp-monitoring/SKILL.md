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
  - Discovering duplicate/conflicting monitoring jobs across agent profiles
  - Consolidating multi-agent cron sprawl (identifying authoritative source)
---

# DeFi LP Position Monitoring

Automated monitoring for concentrated liquidity positions (LFJ, Uniswap V3-style) with tiered alert escalation.

## Alert Escalation (Two-Stage Pattern — May 2026, Jordan)

Jordan's preferred escalation for critical conditions (out-of-range OR efficiency <30%):

```
Stage 1: Condition detected         → ⚠️ MEDIUM Warning (immediate, no debounce)
Stage 2: Same condition persists ≥5min → 🔴 HIGH Red Alert (confirmed)
Stage 3: Condition clears           → ✅ Reset (ready for next episode)
```

**Key details:**
- **Stage 1** fires immediately on first detection (not after a debounce). This alerts you that something is wrong and we're watching.
- **Stage 2** triggers only if the identical condition persists without interruption for ≥5 minutes. This confirms it's not a transient wick.
- **After Stage 2**, further repeats are suppressed until the condition fully clears and then re-occurs. No spam.
- **State tracking:** Use dedicated timestamp fields per condition:
  - `out_of_range_warning_sent` / `out_of_range_red_sent`
  - `efficiency_warning_sent` / `efficiency_red_sent`
- **Applicable triggers:**
  - Price < `range_low` OR > `range_high`  → two-stage out-of-range escalation
  - Fee efficiency < 30%                    → two-stage low-efficiency escalation
- **Severity mapping:** Warning = MEDIUM, Red = HIGH
- **Debounce for other alerts** (non-critical): ≥1% or ≥$0.20 price move, efficiency-zone flip, in/out range status flip → standard material-change reporting (no escalation needed)

**Cooldown rationale (5 min):**
- Matches Jordan's "wait 5 mins to confirm breakout" request
- Balances timeliness vs false positives on concentrated liquidity (AVAX/USDC curve is volatile)
- For less critical conditions, material-change thresholds suffice; no staged escalation needed.

## Duplicate Signal Suppression

**Rule (May 2026 — Desmond):** Prevent multiple identical signals from being generated in quick succession by tracking recent signal hashes in the state file.

**Why:** Without deduplication, a condition that persists across multiple monitoring intervals (e.g., price stays out of range for 3 consecutive 10-min runs) floods the channel with redundant alerts.

**Implementation:**

```python
import hashlib
import time

STATE_FILE = Path.home() / ".hermes" / "scripts" / ".lfj-aae-state.json"

def load_state() -> Dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_signal": None, "last_signal_time": 0, "last_signal_hash": None}

def save_state(state: Dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def signal_is_duplicate(signal_text: str, state: Dict, suppress_seconds: int = 600) -> bool:
    """Return True if this signal was already sent within the suppression window."""
    now = time.time()
    signal_hash = hashlib.sha256(signal_text.encode()).hexdigest()[:16]  # compact fingerprint
    
    # Expire old entries
    if now - state.get("last_signal_time", 0) > suppress_seconds:
        return False
    
    # Compare hash — identical content means duplicate
    if state.get("last_signal_hash") == signal_hash:
        return True
    
    return False

def update_signal_state(state: Dict, signal_text: str):
    """Record this signal as the most recent."""
    state["last_signal_time"] = time.time()
    state["last_signal_hash"] = hashlib.sha256(signal_text.encode()).hexdigest()[:16]
    state["last_signal"] = signal_text[:200]  # preview for debugging
    save_state(state)

# Usage in main monitoring flow:
state = load_state()
signal_text = format_signal(...)  # your full alert message
if signal_is_duplicate(signal_text, state, suppress_seconds=600):
    print("DUPLICATE SUPPRESSED — identical signal sent within 10 minutes")
    return  # skip sending
else:
    send_alert(signal_text)
    update_signal_state(state, signal_text)
```

**Tuning:**
- `suppress_seconds=600` (10 min) matches typical 10-min monitoring cadence — prevents spam if condition persists
- For critical alerts (RED BREAKOUT), consider `suppress_seconds=300` (5 min) for faster escalation on worsening conditions
- Hash includes the full message body, so content changes (e.g., efficiency number drifts) will break duplication and re-alert

**Edge case:** If a condition resolves and then re-occurs after 10 minutes, it should re-alert (fresh incident). The hash comparison ensures only identical boilerplate within the window is suppressed.

**State schema extension:** Add these fields to your existing `.lfj-aae-state.json`:
```json
{
  "total_fees_earned_usd": 12.34,
  "milestone_tier": 2,
  "last_signal_time": 1714678901,
  "last_signal_hash": "a1b2c3d4e5f6g7h8",
  "last_signal": "ALERT:warning_below — Price $9.08 below range..."
}
```

**Note:** Two-stage alert escalation (see above) already includes per-condition suppression via `*_warning_sent` and `*_red_sent` timestamps. Hash-based deduplication is complementary for one-off material-change reports that don't use the escalation ladder.

## Smart DCA Zones (Efficiency-Based)

Map fee efficiency to DCA size to avoid chasing in low-earning zones:

| Efficiency Zone | Condition | DCA Amount | Rationale |
|-----------------|-----------|------------|-----------|
| 🟢 **Center** | ≥ 70% | $50 (full) | Position deep in range, earning optimally — keep stacking |
| 🟡 **Mid** | 50–70% | $30 (reduced) | Still earning but approaching edges — size down, don't chase |
| 🟠 **Low** | 30–50% | $20 (micro) | Near edge — watch for rebalance, minimal new capital |
| 🔴 **Edge/Crash** | < 30% | $10 (micro) + URGENT | Earnings collapsed — rebalance immediately, tiny DCA only |

**Trigger:** `dca_by_efficiency(eff)` returns `(amount, reason_string)`. Tie to Monday DCA schedule if `weekday() == 0`.

## Edge Detection Threshold

**≤ 30% fee efficiency** is the rebalance urgency threshold for curve-shaped positions:
- Below 30%: price is near a range boundary, liquidity is poorly deployed
- Action: "Shift range to capture volatility" + suggest new bounds based on recent vol

*Rationale:* On curve shapes, fee efficiency drops sharply as price approaches the edges. 30% is the inflection where salvage becomes unlikely without intervention.

## Quiet Hours Pattern

Respect config-based quiet hours to avoid off-hour noise:

```python
QUIET_START = 23   # 11 PM
QUIET_END   = 6    # 6:30 AM (with 30-min grace)
...
def is_quiet_hours():
    now = datetime.now(eastern)
    if now.hour >= QUIET_START or now.hour < QUIET_END:
        return True
    if now.hour == QUIET_END and now.minute < 30:
        return True  # grace period
    return False
```

If quiet hours → print `QUIET_HOURS` and exit 0 (silent).

## Persistent Alert Debounce (Hourly Silence After Confirmation)

**Problem:** Alert mode fires every 10 minutes when conditions remain bad (out-of-range OR efficiency <30%). After confirming the condition persists, further pings become noise until the state changes.

**Solution:** After **2 consecutive alert-mode reports**, silence further alerts until the **next hour boundary**. This gives you a confirmatory ping (first alert → second alert confirms) then radio silence. Hour rollover provides a periodic heartbeat so you don't miss a persistent condition all day.

**Implementation:**
Add to state file (`.lfj-d5-state.json` or `.lfj-defi-state.json`):
```json
{
  "consecutive_alert_count": 0,
  "alert_silence_until": null
}
```

Early-exit gate in `should_send_in_alert_mode()`:
```python
def should_send_in_alert_mode(state, ...):
    now = time.time()
    # Gate: suppress within silence window
    silence_until = state.get("alert_silence_until")
    if silence_until and now < silence_until:
        return False, "persistent alert silence until next hour"
    # ... existing active-alert checks follow ...
```

Increment and set silence when an alert report is actually sent (in main flow after `should_send` returns `True` and before generating report):
```python
if should_send and current_mode == MODE_ALERT:
    state["consecutive_alert_count"] = state.get("consecutive_alert_count", 0) + 1
    if state["consecutive_alert_count"] == 2:
        next_hour_dt = now_et().replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        state["alert_silence_until"] = next_hour_dt.timestamp()
```

Clear on mode exit (when returning to NORMAL) or hour rollover:
```python
def should_send_in_alert_mode(...):
    # ... at start, clear expired window ...
    now_ts = time.time()
    if state.get("alert_silence_until") and now_ts >= state["alert_silence_until"]:
        state["consecutive_alert_count"] = 0
        state["alert_silence_until"] = None

# Also in update_state_after_report():
if current_mode != MODE_ALERT:
    state["consecutive_alert_count"] = 0
    state["alert_silence_until"] = None
```

**Dial-in notes:**
- **2-ping confirmation** balances awareness vs. spam. Adjust to 3 if you want more assurance before silencing.
- **Silence window = until next hour** provides natural heartbeat and preserves hourly cadence for critical conditions.
- **Escalation precedence:** Active debounced alerts (`OUT_OF_RANGE_CONFIRMED`, `LOW_EFFICIENCY_REBALANCE`) bypass silence — they are always sent when they fire. The silence gate only applies to the *persistent hourly check* path (efficiency <30% without a fresh debounced alert, or out-of-range without a fresh debounced alert).
- **Hourly check still respected:** Even within silence, if a *new* debounced alert fires (e.g., efficiency drops further from 28% → 22%, triggering a fresh `LOW_EFFICIENCY_REBALANCE`), it breaks through and restarts the 2-ping cycle.

**Related:** This complements Two-Stage Alert Escalation. Escalation handles *first-detection* (warning → red). This handles *persistent-state annoyance* after the red has already fired. Both use different state fields.

## State Schema for Two-Stage Escalation

For condition-specific escalation tracking, extend `.lfj-aae-state.json` with:

```json
{
  "out_of_range_warning_sent": null,     // timestamp of first warning
  "out_of_range_red_sent": null,         // timestamp of red alert (null until sent)
  "efficiency_warning_sent": null,       // timestamp of first efficiency warning
  "efficiency_red_sent": null,           // timestamp of red efficiency alert
  "last_price": 9.1589,
  "last_efficiency": 94.1,
  "last_in_range": true,
  "last_zone": "zone_70_plus"
}
```

**Logic:**
- On detection: if `warning_sent` is null → send warning, set timestamp
- On subsequent runs: if `red_sent` is null AND `now - warning_sent >= 5min` → send red, set timestamp
- When condition clears: reset both timestamps to `null`
- After red: further repeats suppressed until reset

**Why separate fields per condition?** Prevents cross-condition interference (out-of-range red shouldn't block efficiency warnings).

## Consolidation Pattern — Single Unified Tracker

When duplicate LP/cron jobs exist, consolidate into **one canonical script**:

**Anti-pattern:** Multiple overlapping jobs (`lp-range-monitor-v2.py`, `v3.py`, `d5-master-cron.py`) each with separate state files → conflicting data, alert fatigue, config drift.

**Pattern:**
1. **Create `d5-milestone-tracker.py`** (functionally named, not "consolidated")
2. **Load live `.lfj-aae-config.json`** — no hardcoded POOL dicts
3. **Merge concerns:**
   - CMC watchlist (≥3% moves)
   - LP range + efficiency + P&L
   - Milestone tracking
   - Alert escalation (5 min warning → red)
   - Edge detection (≤30% efficiency → rebalance urgency)
   - Smart DCA zones (4-zone mapping)
4. **Single state file:** `~/.hermes/scripts/.d5-milestone-state.json`
5. **Unified schedule:** 4×/day (08:15, 12:15, 16:15, 20:15 ET) — balances timely alerts without spam
6. **Retire duplicates** via Hermes cron (pause + remove)
7. **Archive** old scripts with `.archive-YYYY-MM-DD` suffix

**Benefits:** One source of truth, consistent efficiency numbers, no state races, easier maintenance.

**Naming:** Name scripts by their function, not implementation detail. Prefer `d5-milestone-tracker.py` over `d5-consolidated-cron.py`.

## Alert Prefix Convention

Standardize prefixes for Hermes routing:

```
ALERT:<type>_<subtype>   → e.g., ALERT:red_breakout_above, ALERT:light_warning_below
MILESTONE:$<amount>      → e.g., MILESTONE:$20.00 (tier reached)
STATUS:OK                → silent run, no action needed
QUIET_HOURS              → suppressed due to quiet hours
```

Consume these prefixes in the cron job prompt for automated routing.

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

After ANY rebalance, range change, or position adjustment, update ALL copies of config. There are typically **two groups** of files to update:

### Group 1: `.lfj-aae-config.json` (script runtime config)

**Full list of known copies (7 found May 2026):**

| # | Location | Used By |
|---|----------|---------|
| 1 | `/root/.hermes/scripts/.lfj-aae-config.json` | Scripts run from main HOME |
| 2 | `/root/.hermes/profiles/desmond/home/.hermes/scripts/.lfj-aae-config.json` | Desmond cron (via `HERMES_HOME`) |
| 3 | `/root/.hermes/profiles/dmob/home/.hermes/scripts/.lfj-aae-config.json` | DMOB cron (via `HERMES_HOME`) |
| 4 | `/root/.hermes/profiles/yoyo/home/.hermes/scripts/.lfj-aae-config.json` | YoYo cron (via `HERMES_HOME`) |
| 5 | `/root/.hermes/profiles/gentech/home/.hermes/scripts/.lfj-aae-config.json` | Gentech cron (via `HERMES_HOME`) |
| 6 | `/root/.hermes/profiles/gentech/.hermes/scripts/.lfj-aae-config.json` | Gentech alt path |
| 7 | `/root/.hermes/profiles/gentech/scripts/.lfj-aae-config.json` | Gentech scripts dir |

**⚠️ Path resolution:** Scripts using `HERMES_HOME` resolve to `~/.hermes/profiles/{agent}/home/.hermes/scripts/`, NOT `/root/.hermes/scripts/`. The `HERMES_HOME` env var defaults to the agent's profile directory when run via cron. This means a script may read from copy #2–5 while you edited copy #1.

**To find all copies after a rebalance:**
```bash
find /root/.hermes -name ".lfj-aae-config.json" -type f 2>/dev/null
```

**To batch-sync all copies (preferred — run after any rebalance):**
```python
import json, glob

# Read the authoritative values
NEW_POSITION = {
    "range_low": 9.44,
    "range_high": 9.74,
    "shape": "bid-ask",
    "total_usd": 123.74,
    "token0_amount": 6.13,
    "token1_amount": 64.85
}

for path in glob.glob("/root/.hermes/**/.lfj-aae-config.json", recursive=True):
    with open(path) as f:
        config = json.load(f)
    config["position"].update(NEW_POSITION)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✅ {path}")
```

### Group 2: Vault documentation (single source of truth for humans + d5-master-cron.py)
| File | What to update |
|------|---------------|
| `/root/vaults/gentech/03-Strategies/scripts/d5-master-cron.py` | `POOL["range_low"]` and `POOL["range_high"]` in the `POOL` dict |
| `/root/vaults/gentech/00-HQ/config/defi-lp-config.env` | `RANGE_LOW=` and `RANGE_HIGH=` |
| `/root/vaults/gentech/03-Projects/defi-milestones.md` | Range in "Position Summary" header |
| `/root/vaults/gentech/03-Strategies/cron-jobs.md` | Model/provider overrides if changed |

Also update `/root/vaults/gentech/00-HQ/config/defi-lp-config.env` (env-format backup).

**To find all copies after a rebalance:**
```bash
find /root/.hermes -name ".lfj-aae-config.json" 2>/dev/null
```

**To verify the active config matches reality:**
```bash
# Check which config the script actually reads (HERMES_HOME-dependent):
cd /root/.hermes/scripts && python3 -c "
import os
HERMES_HOME = os.environ.get('HERMES_HOME', os.path.expanduser('~'))
config = os.path.join(HERMES_HOME, 'home', '.hermes', 'scripts', '.lfj-aae-config.json')
print(f'Script reads from: {config}')
import json
with open(config) as f:
    d = json.load(f)
p = d['position']
print(f'Range: ${p[\"range_low\"]}–${p[\"range_high\"]} | Shape: {p[\"shape\"]} | Total: ${p[\"total_usd\"]}')
"

# Quick manual test (set HERMES_HOME to profile dir):
HOME=/root python3 /root/.hermes/scripts/d5-lp-consolidated.py 2>&1 | head -10
```

## Pitfalls

- **Config drift across profile copies** — `.lfj-aae-config.json` exists in multiple profile directories. After a rebalance, the cron job reads from its profile's copy, which may still have the old range. This causes false "OUT OF RANGE" alerts when the position is actually in range. Always update ALL copies (see Config File Management above).
- **One-shot jobs get consumed on run** — if testing with `cronjob run`, recreate the job after as it may not persist
- **Script path mismatches break cron silently** — If the `script` field in `jobs.json` doesn't match the actual filename on disk, the cron agent reports "Script not found." Always verify `jobs.json` → `script` matches the real file in `~/.hermes/profiles/<profile>/scripts/`. Run the script manually with `HOME=/root/.hermes/profiles/<profile>/home` to confirm it resolves paths correctly. The config file (`.lfj-aae-config.json`) must also exist at the path `~/.hermes/scripts/.lfj-aae-config.json` relative to the profile's HOME.
- **Pool addresses are case-sensitive** — use checksummed addresses
- **Range updates require job prompt edits** — update the prompt with new bounds, don't just change a config value
- **High-frequency jobs (10 min) burn tokens** — ensure prompt is efficient, avoid redundant API calls
- **Alert state must be persisted between runs** — For escalation tracking (warning → red), you need stateful timestamps. Do NOT rely on one-shot memory. Write to `.lfj-aae-state.json` with per-condition timestamps (`*_warning_sent`, `*_red_sent`) and reset when condition clears. See State Schema above.
- **Hardcoded position values drift** — If a cron prompt says "position = X AVAX + Y USDC", it becomes stale after any on-chain action (withdraw, claim, rebalance). Always read on-chain or accept manual balance updates
- **LFJ V2.2 pool is ERC1155, not ERC721** — Standard `ownerOf(uint256)` and `balanceOf(address)` revert on the pool contract. Use ERC1155 `balanceOf(address, uint256)` or the Position Manager
- **Script copies must stay in sync** — When updating a monitoring script, copy to ALL locations: vault (`03-Strategies/scripts/`), `/root/.hermes/scripts/`, and `/root/.hermes/profiles/gentech/scripts/`. Cron jobs resolve scripts relative to their profile's HOME. Missing a copy = stale script running silently.
- **Two-stage escalation requires resetting both timestamps on clear** — When condition clears (price back in range OR efficiency rises above 30%), you MUST set both `*_warning_sent` and `*_red_sent` to `None`. Forgetting to reset `warning_sent` prevents future escalation cycles.
- **Cron jobs inherit broken model when config provider fails** — If ALL DeFi monitoring cron jobs start erroring simultaneously, the inherited model/provider from `config.yaml` is likely broken (401, out of funds). Fix: pin each job to a working model via `cronjob update ID --model '{"model":"MODEL_NAME","provider":"custom:PROVIDER_NAME"}'`. Check `~/.hermes/logs/errors.log` for the actual provider error. This affects ALL jobs across all profiles that don't have explicit model overrides.
- **Two Xiaomi providers with different API keys** — `config.yaml` has both `xiaomi` (built-in, key: `tp-swwf...`) and `custom:XiaomiMega` (custom, key: `tp-s7yf...`). The built-in `xiaomi` provider returns 401 for cron sessions even though it works interactively. **Always use `custom:XiaomiMega`** for cron jobs — it's what DMOB's working jobs use. Symptom: cron job errors with `Invalid API Key` immediately after trigger, but same model works in interactive chat.
- **Missing skills in cron job definitions cause silent failures** — If a cron job references skills that don't exist in the agent's profile (e.g., `cmc-watchlist-scraper`, `crypto-monitoring-cron`), the job errors with a 401 from the skill's API call, not a "skill not found" error. Fix: clear the `skills` field on the job (`skills: []`) and embed the logic directly in the prompt.
- **Stale range in job prompts after rebalance** — The `.lfj-aae-config.json` may be updated but the cron job prompt still hardcodes the old range (e.g., prompt says 9.00-9.40 while config says 9.25-9.59). After ANY rebalance, update BOTH config files AND all cron job prompts that reference the range. Use `cronjob update ID --prompt '...'` to fix.
- **Manual script run is the canonical first debugging step** — When cron jobs error, run the script directly (`cd /root/vaults/gentech/03-Strategies/scripts && python3 d5-lp-consolidated.py`) to prove whether the issue is the provider/model or the script itself. If the manual run succeeds, the problem is in the cron provider config. If it fails, the problem is in the script or its dependencies.
- **Config uses nested position object** — `.lfj-aae-config.json` stores range as `position.range_low` / `position.range_high` (nested under `position` key), NOT top-level `range_low` / `range_high`. Access with `config["position"]["range_low"]`, not `config["range_low"]`.
- **Cron prompt-only jobs fabricate data** — When a cron job prompt tells an agent to "fetch current price and compare to range" but the agent lacks API tools, it **fabricates plausible-looking data** (wrong range, wrong shape, wrong status). The output looks authoritative but is fiction. **Fix:** Use the `script` parameter in the cron job to run `d5-lp-consolidated.py` (or similar) first. The script fetches real on-chain data; the agent only formats the output. Example: `cronjob update <id> --script d5-lp-consolidated.py --prompt "Format the script output above into a clean report."`
- **`HERMES_HOME` resolves to profile dir, not `/root`** — Scripts using `HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))` resolve config paths to `/root/.hermes/profiles/{agent}/home/.hermes/scripts/.lfj-aae-config.json`, not `/root/.hermes/scripts/.lfj-aae-config.json`. This means the script may read a different config copy than the one you edited. **Always verify** which copy the script actually reads: add `print(f"Config: {CONFIG_PATH}")` to the script's main(), or check `python3 -c "import os; print(os.environ.get('HERMES_HOME', os.path.expanduser('~')))"` in the cron context.

## User Preferences (Jordan, May 2026)

### Dual-Schedule Milestone Reporting

Jordan prefers **two daily milestone check-ins** rather than one:
- **Morning:** 08:30 AM — start-of-day progress snapshot
- **Evening:** 09:00 PM — end-of-day cumulative summary

**Implementation:** Use cron `30 8,21 * * *` (8:30 & 21:00 daily) for the DeFi Milestone report job. The report should focus on:
- Current tier progress (Scout → Raider → Warlord → Sovereign)
- Fees earned today vs. daily target
- Distance to next milestone
- LP efficiency & in-range status (brief)
- Any rebalance recommendations

**Do NOT** send milestone updates more frequently than twice daily unless a tier boundary is crossed.

### Silent Range Monitoring (Crime Job)

The LP range monitor should run frequently but **only speak when something matters**:
- Baseline mode: silent when IN RANGE AND efficiency ≥ 75%
- Escalation mode: triggered when out-of-range OR efficiency < 30% (see Two-Stage Alert Escalation above)

**Implementation reference:** `d5-lp-consolidated.py` implements this with `should_send` gate + two-stage alert engine.

### Cadence Preference (Jordan, May 2026)

Jordan prefers **adaptive monitoring frequency**:

| Mode | Cadence | Trigger |
|------|---------|---------|
| **Baseline** | Every hour (aligned after crypto watchlist) | Normal conditions — position in range, efficiency healthy |
| **Critical** | Every 10 minutes | Out-of-range OR efficiency <30% (until condition clears) |

**Rationale:** Avoid unnecessary notifications while maintaining situational awareness during stress periods. The script itself can run at a fixed frequency, but the *reporting* is gated by material-change logic; or the cron schedule can be dynamically adjusted based on alert state.

**Implementation:** Either:
- Fixed 10 min schedule with quiet-on-no-change gate (current approach in `d5-lp-consolidated.py`)
- Or two separate cron jobs (hourly + 10min-critical) with state-based enabling/disabling via `force_send` flag

---

### Consolidation Architecture (May 2026)

**Intended Single Source of Truth**

**The LP position data should be owned by ONE job:**

```
[job] DeFi Milestone Tracker (DMOB)
├── Job ID: 3fc1a11a88d7 (or new ID if not found)
├── Script: d5-milestone-tracker.py (canonical, not d5-master-cron.py)
├── Schedule: 30 8,21 * * * (8:30 AM & 9:00 PM daily)
├── Outputs: Structured AAE signal + Human-readable Telegram report
└── Feeds: D5 milestone ladder, AAE progression engine
```

All other monitors (watchlists, dashboards) should **consume** this data, not re-scrape the pool independently.

**Actual Multi-Agent Job Sprawl (Discovered May 2, 2026)**

**Problem:** Three independent profiles (DMOB, Desmond, YoYo) all run overlapping LP/crypto monitors with different scripts and schedules. This causes:
- Conflicting efficiency numbers (different calculation methods)
- Alert fatigue (same event notified 3–4×)
- State file races (multiple jobs writing `.lfj-aae-state.json`)
- Duplicate cron tokens burned

**Job Registry Snapshot (Post-Cleanup Target)**

| Profile | Job Name | Job ID | Schedule | Script | Status |
|---------|----------|--------|----------|--------|--------|
| **DMOB** | **DeFi Milestone Tracker** | `3fc1a11a88d7` (or new) | `30 8,21 * * *` (8:30 & 9:00 PM) | `d5-milestone-tracker.py` | ✅ Authoritative |
| **DMOB** | LP Range Monitor | `b2bb2bae4fc5` | Every 10 min (6–23) | `lp-range-monitor-v3.py` | ⚠️ Stale (Apr 27) |
| **DMOB** | Consolidated Crypto Watchlist | `3044d70c58bc` | Every 2h (6–18) | Prompt-based | Active |
| **DESMOND** | Defi Milestone | `0c8debb70799` | Daily (1440m) | Prompt-based | ⚠️ Duplicate (paused) |
| **DESMOND** | YoYo — Crypto Watchlist + LP Monitor | `e00b46103b08` | 4× daily (8,12,16,20) | Prompt-based | ⚠️ Duplicate (paused) |
| **DESMOND** | YoYo — LP Position Monitor | `0b2beec3f702` | Every 10 min (6–23) | Manual scrape | ⚠️ Legacy (paused) |
| **YOYO** | YoYo — Crypto Watchlist + LP Monitor | `faed4f588aef` | 4× daily (8,12,16,20) | Prompt-based | ⚠️ Duplicate (paused) |
| **YOYO** | YoYo — DeFi Milestone + LP Monitor | `cfa8d1c19357` | Daily 14:10 | `lp-range-monitor-v2.py` | ❌ Error (paused) |
| **GENTECH** | YoYo — Crypto Watchlist + LP Monitor | Not in `hermes cron list` output (likely cloned in jobs.json but not loaded) | 4× daily | Prompt-based | ⚠️ Duplicate (paused) |

**Canonical script location:** `/root/vaults/gentech/03-Strategies/scripts/`
- `d5-milestone-tracker.py` — consolidated tracker (authoritative)
- `lp-range-monitor-v3.py` — silent range watcher (keep active)
- `d5-lp-consolidated.py` — deprecated (archive)

**Consolidation Checklist (Updated)**

When cleaning up duplicates:

- [ ] Match job IDs across `hermes cron list` and `jobs.json` to identify ownership
- [ ] Verify script file exists at `~/.hermes/scripts/` or `~/.hermes/profiles/<profile>/scripts/`
- [ ] Pause duplicates via `hermes cron pause <job-id>` (preserves history)
- [ ] Remove from `jobs.json` if confirmed obsolete
- [ ] Update surviving job prompts to reference **single source** state file: `~/.hermes/scripts/.lfj-aae-state.json`
- [ ] Verify remaining job runs cleanly (check `~/.hermes/profiles/<agent>/cron/output/<job-id>/`)
- [ ] Document final job registry in `references/job-registry-consolidated-YYYY-MM-DD.md`
- [ ] Update all config copies to match the vault master: `/root/vaults/gentech/00-HQ/config/defi-lp-config.env`

**⚠️ Pitfall — Prompt Threshold Mismatch:** When updating or creating duplicate job prompts, ensure milestone thresholds match the actual configuration. A common error is using $500/day for Scout tier instead of the correct $5/day. This causes confusing outputs where the progress bar shows a threshold different from the actual milestone value. Always cross-reference the `.lfj-aae-config.json` file for correct milestone values (Scout: $5, Raider: $20, Warlord: $50, Sovereign: $100).
After cleanup, ONLY these jobs should remain **ACTIVE**:

| Job Name | Owner | Job ID | Schedule | Purpose |
|----------|-------|--------|----------|---------|
| **LP Range Monitor** | DMOB | `b2bb2bae4fc5` | Every 10 min (6–23) | Silent out-of-range alerts only |
| **DeFi Milestone Report** | DMOB | `3fc1a11a88d7` | 30 8,21 * * * (8:30 & 21:00) | Twice-daily milestone progress |
| **Price Watchlist** | YoYo | `faed4f588aef` | 4× daily (8,12,16,20) | Price movements only, no LP re-scrape |

All other LP-specific jobs should be **PAUSED** or **REMOVED**.

### Consolidation Checklist (Updated)

When cleaning up duplicates:

- [ ] Match job IDs across `hermes cron list` and `jobs.json` to identify ownership
- [ ] Verify script file exists at `~/.hermes/scripts/` or `~/.hermes/profiles/<profile>/scripts/`
- [ ] Pause duplicates via `hermes cron pause <job-id>` (preserves history)
- [ ] Remove from `jobs.json` if confirmed obsolete
- [ ] Update surviving job prompts to reference **single source** state file: `~/.hermes/scripts/.lfj-aae-state.json`
- [ ] Verify remaining job runs cleanly (check `~/.hermes/profiles/<agent>/cron/output/<job-id>/`)
- [ ] Document final job registry in `references/job-registry-consolidated-YYYY-MM-DD.md`
- [ ] Update all config copies to match the vault master: `/root/vaults/gentech/00-HQ/config/defi-lp-config.env`

### Pitfall: Conflicting Efficiency Numbers

**Symptom:** D5 Master Cron reports 79.6% efficiency, AAE Signal Monitor reports 50.3% for the same pool.

**Cause:** Different data sources + calculation nuances:
- D5: DexScreener TVL directly
- AAE: On-chain RPC fallback + granular reserves calc
- Different price decimals handling
- Different range boundaries (config drift)

**Fix:** Standardize on **one** source. The authoritative job (`3fc1a11a88d7`) should be the only one writing to `.lfj-aae-state.json` and `.lfj-aae-config.json`. Disable all other jobs that write to these state files.

## Screenshot Analysis (Vision Tool Fallback Pattern)

When users share LP position screenshots (Trader Joe, DexScreener, etc.) and on-chain data isn't immediately available:

**Problem:** `browser_vision` may fail with `google/gemini-2.0-flash-001` not supported (400 error). This is a known Hermes Agent issue — the vision model endpoint is misconfigured or unavailable.

**Fallback chain:**
1. **Try `browser_vision` first** — if it works, use it
2. **If vision fails → OCR with tesseract:**
   ```bash
   tesseract /path/to/image.jpg stdout --psm 6 2>/dev/null
   ```
3. **Dark-themed UIs produce garbage OCR** — trading platforms (Trader Joe, DexScreener) use dark backgrounds with light text, which tesseract struggles with
4. **Crop strategy** — split image into top/middle/bottom thirds and OCR each separately. This helps isolate distinct UI sections (header, chart, position details):
   ```python
   from PIL import Image
   img = Image.open('screenshot.jpg')
   w, h = img.size
   img.crop((0, 0, w, h//3)).save('/tmp/top.jpg')
   img.crop((0, h//3, w, 2*h//3)).save('/tmp/mid.jpg')
   img.crop((0, 2*h//3, w, h)).save('/tmp/bot.jpg')
   ```
5. **Manual interpretation required** — OCR on dark trading UIs is inherently messy. Extract what you can (platform name, pair, balance, date) and ask user to confirm ambiguous numbers

**Key fields to extract from LP screenshots:**
- Platform (Trader Joe / DexScreener / etc.)
- Pool pair (AVAX/USDC, etc.)
- Active bin / current price
- Deposit balance (USD)
- Range bounds (lower — upper)
- Claimable rewards
- Fees earned (24h / total)
- Last refreshed timestamp

**Pitfall:** Don't trust OCR'd numbers from dark UIs without user confirmation. Tesseract misreads decimals, merges adjacent characters, and drops digits on dark backgrounds. Always present extracted data as "approximately X" and ask for confirmation.

## Related

- CoinGecko API for price feeds
- LFJ subgraph for pool/position data
- Obsidian vault for alert state persistence
- `defi-dashboard-digest` — daily digest combining this LP data with market overview (complementary skill; use for scheduled digests, not real-time alerts)
- `defi-lp-regime-strategy` — strategy framework for deciding when to LP vs spot based on market regime (use for strategic decisions, not monitoring)

## Documentation

- **Config drift incident (May 2026):** `references/config-drift-incident-2026-05-06.md` — 7 config copies with 3 different value sets, `HERMES_HOME` path resolution issue, prompt-only fabrication bug, batch sync fix
- **Job registry snapshot:** `references/job-registry-snapshot-2026-05-02.md` — discovered sprawl across DMOB/Desmond/YoYo profiles, consolidation plan (May 2026)
- **Twice-daily milestone template:** `scripts/twice-daily-milestone-report.py` — starter script for Jordan's preferred 8:30 AM & 9:00 PM milestone reports (copy to vault and adapt)
- **Persistent alert debounce (May 2026):** `references/persistent-alert-debounce-implementation-2026-05-03.md` — hourly silence after 2 consecutive alert reports; code changes to `defi-milestone-tracker.py`
- **Cron provider troubleshooting (May 2026):** `references/cron-provider-troubleshooting-2026-05-05.md` — debugging 401 errors across `xiaomi` vs `custom:XiaomiMega`, missing skills causing misleading errors, manual script verification pattern
