---
name: strategies
title: Strategies
description: Crypto/DeFi analysis, portfolio strategy, LP monitoring, yield optimization, market research, on-chain analytics, and milestone tracking for Gentech DeFi Milestone operations.
version: 0.2.0
last_updated: 2026-05-05
---

## AI Agent Payment Integration

**Context**: Pay.sh is a Solana-based payment gateway for AI agents, backed by Solana Foundation and Google Cloud. It enables autonomous agents to pay for API access, transaction fees, and services using stablecoins.

### Core Patterns

#### 1. Pay.sh Integration Pattern

**Integration Points**:
- **AgentEscrow**: Add Pay.sh as a funding method for escrow contracts
- **AAE Financial Controller**: Use Pay.sh for automatic fee payments and API access
- **Agent-to-Agent Payments**: Enable service marketplace transactions

**Implementation**:
```python
class PayShClient:
    def __init__(self, api_key: str, network: str = "mainnet"):
        self.base_url = f"https://{network}.paysh.sh/api/v1"
        self.headers = {"Authorization": f"Bearer {api_key}"}
    
    def create_payment(self, amount: float, recipient: str, memo: str = "") -> str:
        payload = {
            "amount": amount,
            "currency": "USDC",
            "recipient": recipient,
            "memo": memo
        }
        response = requests.post(
            f"{self.base_url}/payments",
            json=payload,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["payment_id"]
```

**Key Considerations**:
- Use testnet/sandbox first
- Implement webhook handlers for payment confirmations
- Add retry logic with exponential backoff
- Monitor rate limits

#### 2. AgentEscrow Payment Architecture

**Context**: AgentEscrow is a trustless escrow system for AI agent services on Solana.

**Payment Flow**:
```
Buyer → Pay.sh → System Wallet → Escrow Contract → Agent (after verification)
```

**Smart Contract Integration**:
```solidity
interface PayShRouter {
    function pay(uint256 amount, bytes32 jobHash) external returns (bool);
}

function fundWithPaySh(bytes32 jobHash, uint256 amount) external {
    PayShRouter(paySh).pay(amount, jobHash);
    _fundEscrow(jobHash, amount, USDC_MINT);
}
```

**Security Patterns**:
- Multi-token support via Swig integration
- Soulbound reputation NFTs (Metaplex)
- World ID verification for Sybil resistance
- Decentralized dispute resolution

#### 3. AAE Financial Controller Agent

**Context**: AAE (AI Agent Ecosystem) is a three-agent system for portfolio management.

**Agent Design**:
```python
class FinancialControllerAgent:
    def __init__(self, pay_sh_client: PayShClient, config: dict):
        self.pay_sh = pay_sh_client
        self.budgets = config["budgets"]
        self.metrics = {}
    
    def allocate_funds(self, strategy: str, amount: float):
        if strategy == "data_feed":
            self.pay_sh.create_payment(
                amount=amount,
                recipient="birdeye_data",
                memo="AAE Analyst data subscription"
            )
        elif strategy == "transaction_fees":
            self.pay_sh.create_payment(
                amount=amount,
                recipient="solana_fee_payer",
                memo="Executor gas fees"
            )
    
    def optimize_portfolio(self, current_positions: dict):
        # Analyst signals → Strategy Brain → Validator → Executor
        # Financial Controller handles all monetary aspects
        pass
```

**Integration with AAE Stack**:
- Analyst agent requests data payments
- Executor agent requests gas fee payments
- Brain agent monitors budgets and approves

### Implementation Methodology

#### Hackathon Sidetrack Adapter Workflow

**When to use**: For hackathon submissions involving new payment integrations.

**5-Step Process**:
1. **API Surface Research** — Map auth, endpoints, SDKs, rate limits
2. **Fit Assessment** — Determine if adapter is "thin" (wraps existing code) or "new program" (requires fresh build)
3. **Decision Framework** — Present options: main focus, low-effort adapters, or full blitz
4. **Adapter Spec Creation** — Write spec with API details, architecture, CLI commands
5. **Sprint Plan Update** — Add adapter tasks to milestones (Days 5-6 after main submission)

**Reference**: `references/sidetrack-adapter-workflow.md`

#### Provider Auth Resilience

**Problem**: Recurring authentication errors (API keys, OAuth tokens).

**Mitigation Stack**:
1. **Retry logic** — Exponential backoff with jitter
2. **Dead-letter queue** — Log failures to `11-Mess Hall/provider-errors/`
3. **Credential pre-rotation** — Validate before critical jobs
4. **Fallback provider pool** — Secondary API keys
5. **Centralized credential store** — HashiCorp Vault or similar

**Monitoring**: Scan logs for `AuthError|401|403|revoked` and alert if threshold crossed.

#### Ground Truth Protocol

**Hierarchy**:
1. On-chain decoded balances (authoritative)
2. Watchlist/price aggregators (secondary)
3. Narrative/summary scripts (tertiary)

**Operational Protocol**:
- Daily vault entries must match ground truth exactly
- If divergence >$0.50 or efficiency differs >5%, document and investigate
- Use symlinks for state files across profiles

**Reference**: `references/ground-truth-protocol.md`

### Pitfalls

#### P1: Payment Rail Not Ready
- **Symptom**: API returns 500 or rate limited during integration
- **Cause**: Sandbox not fully implemented or test keys invalid
- **Fix**: Start with testnet, have backup provider, implement graceful degradation

#### P2: Over-Engineering
- **Symptom**: Building complex adapter when simple webhook would suffice
- **Cause**: Trying to cover all edge cases upfront
- **Fix**: Start minimal, iterate based on actual usage

#### P3: Security Misconfiguration
- **Symptom**: API keys exposed in logs or client-side code
- **Cause**: Improper secret management
- **Fix**: Use environment variables, never commit keys, implement key rotation

#### P4: Ignoring Quiet Hours
- **Symptom**: Alerts sent during user's quiet hours
- **Cause**: `is_quiet_hours()` not checked before sending
- **Fix**: Implement two-mode notification throttling (see `strategies` skill)

#### P5: State File Divergence
- **Symptom**: Different scripts report different balances/efficiency
- **Cause**: State files not synchronized across profiles
- **Fix**: Use symlinks and ground truth protocol

#### P6: Parameter Name Mismatches
- **Symptom**: `NameError: name 'X' is not defined` inside a function
- **Cause**: Call site uses wrong keyword argument name
- **Fix**: Verify function signatures with `grep -n "^def"`; ensure call sites match exactly

### References

- `references/sidetrack-adapter-workflow.md` — API research template, adapter spec format
- `references/ground-truth-protocol.md` — Script discrepancy resolution, state file layout
- `references/provider-strategy.md` — Provider auth resilience, credential management
- `references/defi-milestone-enhancements-2026-05.md` — Implementation details for payment-related alerts
- `references/portfolio-positioning.md` — Messaging and positioning for AI agent projects
- `references/solana-frontier-hackathon.md` — Solana Frontier tracks, AgentEscrow architecture
- `templates/protocol-evaluation-template.md` — Vault file template for new protocol reviews
- `templates/il-spike-vault-entry.md` — Vault entry format for IL review flags
- Integrating payment rails for AI agents (Pay.sh, x402, etc.)
- Designing escrow systems for agent services (AgentEscrow)
- Building financial controllers for autonomous agents (AAE)
- Evaluating payment protocols for agent economy

## Positioning Principles (Personal/Project Portfolios)

When building or reviewing any portfolio or personal-brand page for Jordan or GenTech:

1. **Lead with value, not tools** — Frame around cost savings, risk reduction, hours automated (ROI-driven).
2. **Safety-first narrative** — Emphasize templated deployments, test-driven pipelines, zero standing credentials, auditable outputs.
3. **Agents as amplifiers** — Present AI agents as team members that multiply output, not replace humans. Show roles + metrics per agent.
4. **Quantify outcomes** — Include metrics: "30+ hours automated weekly," "gas optimized by X%," "bugs caught pre-production."
5. **Team showcase** — Include full agent roster with clear role definitions (strategist, marketer, engineer) to demonstrate orchestration capability.
6. **Technical credibility** — Stack badges, contribution heatmaps, CI/CD status, verification mechanisms (security.txt, PGP).
7. **Narrative cohesion** — Consistent story: "I build systems that actually save money" across all sections.

**Tagline guardrail**: Avoid generic "developer" or "builder" labels. Prefer: "Safety-First Agent Orchestrator," "Cost-Saving Systems Builder," "DeFi Tools Engineer" — role + outcome framing.

## Core Patterns

### 1. Hermes Environment Path Resolution

**Problem**: `os.path.expanduser("~")` in Hermes resolves to the profile home (e.g., `/root/.hermes/profiles/yoyo/home`) not the expected `/root` or system home. Script state files must be placed where Hermes cron can read/write them.

**Solution Pattern**:
```python
import os

# Hermes sets HERMES_HOME to the profile root
HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~"))
# Scripts expect to read/write in $HERMES_HOME/home/.hermes/scripts/
HOME_SCRIPTS_DIR = os.path.join(HERMES_HOME, "home", ".hermes", "scripts")

def hermes_path(filename: str) -> str:
    """Return absolute path inside the Hermes profile's script directory."""
    return os.path.join(HOME_SCRIPTS_DIR, filename)

# Usage
STATE_FILE = hermes_path(".d5-lp-state.json")
CONFIG_FILE = hermes_path(".lfj-aae-config.json")
```

**Verification**: Check existence with `os.path.isdir(HOME_SCRIPTS_DIR)` before file operations.

### 2. Config-Driven Architecture

**Pattern**: All tunable parameters live in a JSON config file loaded at runtime. This separates strategy logic from strategy parameters, allowing rapid iteration without code changes.

**Structure** (`.lfj-aae-config.json`):
```json
{
  "position": {
    "range_low": 9.0,
    "range_high": 9.3,
    "shape": "curve"
  },
  "milestones": [
    {"tier": 1, "label": "Scout", "daily_fees": 5.0},
    {"tier": 2, "label": "Raider", "daily_fees": 20.0}
  ],
  "dca": {
    "base_amount": 50,
    "boost_amount": 15,
    "enabled": true
  },
  "quiet_hours": {
    "start": 23,
    "end": 6,
    "timezone_offset": -4
  },
  "alert_rules": {
    "alert_if": ["out_of_range", "efficiency_low", "milestone_hit"],
    "critical_if": ["price_crash", "il_severe"]
  }
}
```

**Load**: `cfg = json.load(open(CONFIG_FILE))` with fallback defaults.

## Debounce + Confirmation Pattern

**Rule**: Transient spikes should not trigger immediate alerts. Implement a stateful debounce that requires a condition to persist for N seconds before raising the alert.

**Implementation**:
```python
OUT_OF_RANGE_DEBOUNCE_SEC = 300  # 5 minutes
EFFICIENCY_LOW_DEBOUNCE_SEC = 300

state = load_state()  # loads from STATE_FILE

# On each run:
if condition_met:
    if state.get("condition_start") is None:
        state["condition_start"] = now_ts()
    elif now_ts() - state["condition_start"] >= DEBOUNCE_SEC:
        trigger_alert()
else:
    state["condition_start"] = None  # reset

save_state(state)
```

**Key**: The timestamp persists between runs via JSON state file. Always clean up state on recovery.

## Two-Mode Notification Throttling & Alert Management

**Problem**: Cron jobs that poll every 10 minutes create notification spam during normal conditions, yet we need rapid alerts when things go wrong. A single debounce isn't enough — we need two distinct operating modes.

**Solution**: Split monitoring into two modes with different throttling policies, switching based on position health.

### Mode Definitions

| Mode | Trigger | Polling Frequency | Notification Policy |
|------|---------|-------------------|---------------------|
| **NORMAL** | Efficiency ≥30% **and** price in range | Every 10 min (cron) | At most **once per hour**; only on material change |
| **ALERT** | Efficiency <30% **or** price out of range | Every 10 min (cron) | Immediate warning → 5-min debounce → **red alert** → subsequent alerts only if metrics worsen or recover |

### State Management

Persist these fields in the script's state JSON:
```python
{
  "mode": "normal" | "alert",
  "last_normal_sent_at": 1714736400.0,   # epoch seconds; hourly cooldown
  "warning_sent_at": 1714736200.0,        # debounce timer for pre-alert
  "out_of_range_warning_sent": 1714736200.0,  # separate debounce
  "last_alert_snapshot": {                # deduplicate identical alerts
    "types": ["LOW_EFFICIENCY"],
    "price": 9.15,
    "efficiency": 29.0,
    "in_range": true
  }
}
```

### Normal Mode Logic

Send only if **all** conditions hold:
1. First run (no prior state) — establish baseline
2. Any of these material changes detected:
   - Price moved ≥1% or ≥$0.20 absolute
   - Efficiency zone shifted (e.g., 81% → 57% crosses 70% boundary)
   - In-range status flipped
   - New alert condition appeared (efficiency dropped below 30%, or position went out of range)
3. **AND** at least 3600 seconds since `last_normal_sent_at`

### Alert Mode Logic

Entry (efficiency <30% or out-of range):
- Immediately send a **warning** message (e.g., *"Efficiency 29% — rebalance recommended within 5 minutes"*)
- Set `warning_sent_at = now_ts`
- Clear `last_normal_sent_at`

After 5-minute debounce (still in condition):
- Snapshot current metrics (`last_alert_snapshot`)
- Send **red alert** with severity and suggested action
- Set `warning_sent_at = None` (already alerted)

Further 10-minute checks while condition persists:
- **Suppress** if: same alert types AND price changed <1% AND efficiency changed <5 pp AND in-range status unchanged
- **Send** only if: metrics changed meaningfully (worsening or improving) OR new alert type added OR alert condition cleared (recovery)

Exit alert mode (condition resolves):
- Clear `warning_sent_at`, `out_of_range_warning_sent`, `last_alert_snapshot`
- Send immediate recovery notification
- Switch to NORMAL and set `last_normal_sent_at` (counts as the hourly send)

### Implementation Pattern

```python
def evaluate_mode(position: Dict) -> str:
    """Return MODE_NORMAL or MODE_ALERT based on efficiency and range."""
    efficiency = position["efficiency"]
    in_range = position["in_range"]
    if efficiency < 30 or not in_range:
        return MODE_ALERT
    return MODE_NORMAL

def should_send_in_normal_mode(state: Dict, position: Dict, new_alerts: List[str]) -> bool:
    now = time.time()
    if state.get("mode") != MODE_NORMAL:
        return False
    if now - state.get("last_normal_sent_at", 0) < 3600:
        return False  # hourly cooldown active
    if not significant_change_detected(state, position, new_alerts):
        return False
    return True

def should_send_in_alert_mode(state: Dict, position: Dict, new_alerts: List[str]) -> bool:
    now = time.time()
    # First-time warning (pre-red alert debounce)
    if state.get("warning_sent_at") is None:
        return True  # send immediate warning
    # Debounce period active
    if now - state["warning_sent_at"] < 300:
        return False  # still within 5-min waiting period
    # After debounce: send if meaningful change since last alert
    if not alert_has_meaningful_change(state, position, new_alerts):
        return False
    # Suppress identical repeat; update snapshot after sending
    return True

def alert_has_meaningful_change(state, position, new_alerts) -> bool:
    snap = state.get("last_alert_snapshot", {})
    old_alerts = set(snap.get("types", []))
    if set(new_alerts) != old_alerts:
        return True  # new alert type
    old_price = snap.get("price", position["price"])
    old_eff = snap.get("efficiency", position["efficiency"])
    old_in_range = snap.get("in_range", position["in_range"])
    # Thresholds: price ≥1% or ≥$0.20, efficiency ≥5 pp, in_range flip
    if abs(position["price"] - old_price) >= max(0.20, 0.01 * old_price):
        return True
    if abs(position["efficiency"] - old_eff) >= 5.0:
        return True
    if position["in_range"] != old_in_range:
        return True
    return False
```

### Schedule Alignment Caveat

**Challenge**: User requests: *"Run once an hour after crypto watchlist"*. If the watchlist schedule is unknown or varies, alignment is tricky.

**Options**:
- **Option A (current)**: Keep cron at every 10 minutes, but script self-throttles in NORMAL mode. ALERT mode still checks every 10 min for rapid response. Pros: retains alert agility; Cons: extra cron invocations.
- **Option B**: Split into two cron jobs:
  - Hourly job for NORMAL updates (e.g., `0 * * * *` → after watchlist if watchlist runs at :50)
  - Separate `*/10` job *only* when in ALERT mode, enabled/disabled via state flag file. Pros: precise alignment; Cons: complexity of toggling cron or using conditional script.
- **Option C**: Have the hourly job set a flag; a separate short-interval alert-monitoring daemon watches that flag and escalates checks when needed. Overkill for single-position monitoring.

**Recommendation**: Option A (current) is simplest and meets user requirements unless cron load is a concern. Document the watchlist schedule when found and adjust D5 cron to `*/10` offset by N minutes if needed (e.g., if watchlist runs at :03, set D5 cron to `2,12,22,...` to run just after).

### User Preference: "Keep Silent If Nothing Changed"

This session reinforced the user's explicit preference: *"if nothing has changed too much, keep silent"*. The pattern above implements this by:
- Hourly cooldown in normal mode (can't send more often even if changed)
- Threshold-based change detection (≥1% price, ≥5 pp efficiency) to ensure only "significant" updates are sent
- Alert suppression when conditions remain static

**Do not send**: routine check-ins, "all clear" pings when nothing moved, duplicate messages within cooldown windows.

### 4. Milestone Ladder Tracking

**Pattern**: Milestones are ordinal thresholds (daily fee targets) stored in config. Current tier is computed from estimated daily fees; state tracks last reached tier to detect promotions.

**Helper**:
```python
def get_current_tier(est_fees: float, milestones: List[Dict]) -> int:
    if est_fees < milestones[0]["daily_fees"]:
        return -1  # Unranked
    for i, ms in enumerate(milestones):
        if est_fees < ms["daily_fees"]:
            return i - 1  # previous tier is current
    return len(milestones) - 1  # max tier
```

**State field**: `current_milestone_idx` — compare against new calculation to detect `milestone_changed`.

### 5. CMC Watchlist Integration

**Pattern**: Fetch top N assets from CoinMarketCap, compare current price to previous day's close, trigger alerts on threshold moves (≥5% default). Store last prices in a separate state file reset daily.

**State file**: `.cmc-watchlist-state.json`
```json
{
  "date": "2026-05-02",
  "last_prices": {
    "BTC": 65000.00,
    "SOL": 145.20
  }
}
```

**Daily reset**: Compare `state["date"]` to `now_et().strftime("%Y-%m-%d")`; if different, clear `last_prices`.

## Cron Job Routing Audit Pattern

**Trigger**: User asks to verify or update cron job delivery targets. Also run as part of periodic infrastructure health checks.

**Smart Routing Rules (Gentech org)**:
- **HQ** (`-1003863540828`) — coordination hub, daily briefings, portfolio updates, job hunting, cross-department summaries
- **Strategies** (`-1002916759037`) — investment work, DeFi monitoring, LP positions, market analysis
- **Labs** — development work, code builds, technical infrastructure
- **Entertainment** — content creation, social media, marketing

**Audit Procedure**:
1. `cronjob list` — get all jobs with their `deliver` field
2. For each job, determine which department owns the work (not which agent wrote the prompt)
3. Verify the `deliver` target matches the department
4. If a chat ID is unknown, resolve it before making any changes:
   ```bash
   # Check each profile's .env for HOME_CHANNEL mappings
   grep -r "TELEGRAM_HOME_CHANNEL" /root/.hermes/profiles/*/.env 2>/dev/null
   ```
5. Only THEN update delivery targets

**Pitfall — Don't Assume Chat ID Mappings**: In this session, YoYo assumed `-1003863540828` was an unknown group and tried to "fix" Omni-Summary's routing by changing it to Strategies. It was actually HQ the whole time. **Always resolve the chat ID via `.env` grep before changing delivery targets.** The mapping is not documented in one central place — it's in each profile's `.env`.

**Correct routing for current cron jobs** (as of 2026-05-05):
| Job | Correct Group | Chat ID |
|-----|---------------|---------|
| Omni-Summary | HQ | `-1003863540828` |
| Portfolio Site | HQ | `-1003863540828` |
| College.xyz | HQ | `-1003863540828` |
| Defi Milestone | Strategies | `-1002916759037` |

## Media Handling Rule

**User directive**: "Don't send it to other groups." When a user sends an image, video, or file in one group:
- **Keep it local** — confirm receipt in the same group
- **Do NOT broadcast** the media to other Telegram groups (Strategies, Labs, Entertainment, etc.)
- **Do NOT send images to groups unless explicitly asked**
- If the content needs to be shared, describe it in text instead of forwarding the media

This applies to all agents, not just YoYo. Embed this as a workflow rule in any skill that handles media or cross-group communication.

## Hackathon Sidetrack Adapter Workflow

**Trigger**: When evaluating or building sidetrack submissions for hackathons (additional prize tracks beyond the main submission).

**Workflow** (5 steps):
1. **API Surface Research** — Visit developer docs for each sponsor/sidetrack. Map: auth method, key endpoints, SDK availability, rate limits, Solana support. Document in a structured table.
2. **Fit Assessment** — Map sidetrack requirements to existing project layers. "Thin adapter" = wraps existing code with new API. "New program" = requires fresh Solana program build. Prefer thin adapters when time-constrained.
3. **Decision Framework** — Present Jordan with options:
   - Option A: Focus only on main submission ($30K grand champion)
   - Option B: Main + N low-effort adapters ($8K+ extra, 2-3hr each)
   - Option C: Full sidetrack blitz (risky, spreads engineer thin)
   - **Recommendation**: Option B when engineers are available, Option A when time is critical
4. **Adapter Spec Creation** — For each chosen sidetrack, write a spec file with: API details, adapter architecture (file structure), CLI commands, submission narrative, and integration points with main project.
5. **Sprint Plan Update** — Add adapter tasks to daily milestones. Adapters go last 2 days (Days 5-6) after main submission is solid.

**Reference**: `references/sidetrack-adapter-workflow.md` — full API research template and spec format.

## Agent Coordination: Don't Idle Rule

**User directive**: When an agent hits a stopping point on any project (waiting for approval, missing tools, engineer unavailable, etc.), immediately queue up the next project and start working. Don't idle waiting for a response.

**What counts as a stopping point**:
- Waiting for Jordan's approval on a decision
- Engineer (DMOB/Storm) not available or hasn't ACK'd handoff
- Missing tool or API access needed to proceed
- Blocked on external dependency

**What to do instead**:
1. Document the blocking reason in the current project's status file
2. Check vault for next-priority project in the queue
3. Start working on that project until you hit another stopping point
4. Report status when the original blocker resolves

**Why this matters**: Agents that idle waste Jordan's most expensive resource — time. Even 30 minutes of proactive work on a secondary project compounds across a sprint.

## Token Shutdown / Delisting Response

**Trigger**: A token on the watchlist announces dApp shutdown, delisting, or rug. Immediate action required to prevent stale research and wasted monitoring cycles.

**Response checklist (execute in order)**:
1. **Verify the news** — Read the official announcement (X/Twitter, blog, Discord). Confirm it's real, not FUD.
2. **Check exposure** — Search vault for any active positions, LP pairs, or staking in the affected token:
   ```bash
   rg -l "TICKER" /root/vaults/gentech/03-Strategies/ /root/vaults/gentech/03-Projects/ --type markdown
   ```
3. **Update watchlist** — Strike through the token entry with shutdown date and rationale:
   ```
   | ? | ~~Token~~ | ~~TICK~~ | — | — | — | ⚠️ **dApp shutting down (Month Year)** — removed from active watchlist |
   ```
4. **Cancel pending research** — Mark any planned pool research, LP evaluation, or adapter work as cancelled with reason.
5. **Update cron configs** — Remove from CMC watchlist if price monitoring is active. Suppress any alerts for the token.
6. **Commit to vault** — Single commit with clear message: `Watchlist: remove TICKER — dApp shutting down (Month Year)`
7. **Log the lesson** — If the shutdown was predictable (declining TVL, team exodus, governance capture), add to `references/protocol-due-diligence-framework.md` as a case study.

**User preference**: User reacts emotionally to shutdowns of projects they were tracking ("Well damn, so much for Landshare. This is unfortunate."). Acknowledge the loss briefly, then focus on damage assessment and cleanup. Don't over-analyze the "why" unless asked.

**Post-shutdown monitoring**: If the token has a security token component (e.g., LSRWA), note it as "technically still exists but ecosystem dead" — do not keep on active watchlist.

## Pitfalls

### P1: Hermes HOME Mismatch
- **Symptom**: State file not found or not persisting between cron runs.
- **Cause**: Using `os.path.expanduser("~")` directly returns Hermes profile home, but scripts executed by Hermes cron may expect state in `/root/.hermes/scripts/` or profile's `.hermes/scripts/`.
- **Fix**: Use `hermes_path()` helper that builds path from `HERMES_HOME` explicitly. Verify the directory exists at startup.

### P2: Cron Job Duplication
- **Symptom**: Multiple cron entries running the same or similar scripts, causing redundant alerts.
- **Cause**: Organic growth without central registry.
- **Fix**: Maintain a single consolidated script per domain. Use `jobs.json` as source of truth; document which job IDs map to which script.

### P3: Silent Quiet Hours
- **Symptom**: No alerts received during expected market moves.
- **Cause**: `is_quiet_hours()` returning `True` and exiting silently.
- **Fix**: Log "QUIET_HOURS — no report" to stdout (not stderr). Cron should capture output to a log file for audit.

### P4: Config File Missing Keys
- **Symptom**: `KeyError` on `cfg["position"]["range_low"]`.
- **Cause**: `.lfj-aae-config.json` incomplete or malformed.
- **Fix**: Use `cfg.get("position", {}).get("range_low")` with explicit error message and non-zero exit on missing required keys.

### P5: DexScreener Schema Changes
- **Symptom**: `KeyError: 'priceNative'` or missing fields.
- **Cause**: DexScreener API response structure changed.
- **Fix**: Defensive extraction with `.get()` defaults. Log raw response on error for debugging.

### P6: "D5" vs "DeFi Milestone" Naming
- **Symptom**: User corrects you: "It's DeFi Milestone not D5"
- **Cause**: The LP milestone tracker was historically called "D5" in code and docs, but the user prefers "DeFi Milestone" as the proper name.
- **Fix**: Use "DeFi Milestone" in all user-facing docs, reports, and messages. Script filenames (`d5-master-cron.py`, `d5-milestone-tracker.py`) can keep the `d5-` prefix to avoid breaking cron jobs, but documentation and conversation should use "DeFi Milestone". Memory saved 2026-05-07.

### P7: Parameter Name Mismatches in Function Calls
- **Symptom**: `NameError: name 'X' is not defined` inside a function, even though a similarly-named parameter exists in the function signature (e.g., `oor_duration_minutes` vs `out_of_range_duration_minutes`).
- **Cause**: A call site uses the wrong keyword argument name that does not match the function's defined parameter name. The parameter exists; the name used is simply incorrect.
- **Fix**: Verify function signatures with `grep -n "^def function_name"` or IDE "find references." Ensure all call sites use the exact parameter name. Type hints and static analysis (mypy/pyright) catch mismatches during development.
- **Prevention**: Keep parameter names consistent across signature and all call sites. Prefer positional-only or keyword-only parameters for clarity. Add a comment above the signature listing expected keywords if multiple optional bools/flags are present.
- **Detection Flow**:
  1. Read traceback → identify missing variable name.
  2. Print function signature and all call sites for that function.
  3. Compare keyword names used at call sites against signature parameters.
  4. Correct the mismatch(s) and re-run.

## Workflow: Consolidating Duplicate Cron Jobs

**Problem**: Monitoring systems often need to detect when an entity transitions *into* a desired state (e.g., an LP position returning to range after being out-of-range). Simple threshold checks only detect the *current* state, not transitions.

**Anti-pattern**: Checking only `in_range` and alerting on `not in_range` misses the recovery event entirely. State is lost between runs; without capturing the previous state, transitions are invisible.

**Solution**: Pre-state capture + transition flag.
```python
# In main loop, before mutating state:
was_out = state.get("out_of_range_since") is not None

# ... run condition checks and potentially clear state ...

# After condition evaluation, in the "in-range" else branch:
if in_range:
    # Compute whether we just recovered
    just_recovered = in_range and was_out
else:
    just_recovered = False

# Propagate flag through call chain
build_aae_signal(..., just_recovered=just_recovered)
```

**Signature propagation** (maintains backward compatibility):
```python
def build_aae_signal(..., just_recovered: bool = False): ...
def determine_severity(..., just_recovered: bool = False):
    if just_recovered:
        return "OK"  # Positive notification, not a problem
def get_suggested_action(..., just_recovered: bool = False):
    if just_recovered:
        return "🟢 Recovered — back in range"
```

**Ordering**: Place `if just_recovered:` checks *before* other conditional branches to ensure recovery takes precedence over out-of-range or other states.

**State cleanup**: Recovery should clear the debounce timestamp (`out_of_range_start`) and return to a clean baseline.

## Protocol Due Diligence Pipeline

**Use when**: Evaluating new DeFi protocols for integration, investment, or competitive analysis.

**Pipeline Steps** (execute in order):
1. **Vault Inventory** — Check `03-Strategies/` for existing protocol research files. Flag duplicates or stale analysis.
2. **Active Monitoring Scan** — Review `Defi-Monitor/` daily logs and `scripts/` config files for protocols currently under live tracking.
3. **Competitive Landscape Research** — Identify protocols gaining traction in target ecosystems (Base, Avalanche, Solana) via X thread tier lists, hackathon participant lists, and Dune/DefiLlama trending.
4. **Risk Flagging** — Apply red flag checklist:
   - 🚨 **Rug signals**: Liquidity removal within 90 days, team wallet dumps (>5% supply in 7 days), proxy/upgradable contracts without timelock, anonymous/unverified team
   - ⚠️ **Concerning patterns**: TVL/volume ratio <0.5x, fee APR >200% unsustainably high, token distribution >30% to team/insiders, no GitHub commits in >60 days
   - 📢 **Upgrade risks**: Recent contract upgrades without migration announcement, governance proposals enabling fee siphoning
5. **Risk Rating (1–5 scale)**:
   - **1 — Very Low**: Blue-chip (BTC, ETH, SOL with >$1B TVL, multi-audited, decentralized governance)
   - **2 — Low**: Established L1s/L2s, audits complete, transparent team, TVL >$100M
   - **3 — Moderate**: Newer protocols with audits, some centralization risk, TVL $10–100M
   - **4 — High**: Una kek or minimal audit, anonymous team, <6 months old, TVL < $10M
   - **5 — Very High**: Unaudited, no mainnet, clear rug indicators, hype-driven, liquidity pool < $100K
6. **Report Production** — Concise data-driven output (≤300 words): protocol name, risk rating, key metrics (TVL, volume, APR), specific red flags, recommended action (Monitor / Capped / Avoid).

**Output destination**: Vault file `03-Strategies/<protocol>-evaluation-<YYYY-MM-DD>.md` + summary in weekly report.

**Verification**: Cross-check TVL via DeFiLlama, contract ownership via Etherscan, token distribution via Santiment/Covalent.

---

## Cross-Chain Farming Feasibility Assessment

**Use when**: Evaluating whether a token (especially low-liquidity RWA/altcoin) is viable for yield farming on a target chain (e.g., Solana, Avalanche) that is not its native chain.

**Core insight**: Farming viability is gated by chain-native token presence first, liquidity depth second. If no native token exists on target chain, cross-chain farming is almost certainly non-viable for sub-$50M MC tokens.

**Decision flow**:
```
1. Vault check → Does watchlist/config already specify chain info?
   └─ Yes → Note chains, proceed to step 2
   └─ No  → Continue

2. Chain-native presence verification
   Query: "Does the token have a native or wrapped representation on target chain?"
   ├─ CoinGecko `GET /coins/{id}` → platforms dict
   ├─ Search for "wrapped <TOKEN> <CHAIN>" if not listed
   └─ If no presence → STOP: "Not available on <chain>"

3. Liquidity depth check (if present)
   Thresholds (dynamic by target chain):
   - Solana: ≥$2M 24h volume, ≥$500K pool TVL
   - Base/Ethereum L2: ≥$5M 24h volume, ≥$1M pool TVL
   - BSC/Polygon: ≥$1M 24h volume, ≥$250K pool TVL

   If below thresholds → Reject: "Thin liquidity; slippage/fees > yield"

4. Cross-chain bridge cost analysis (if native but thin on target)
   Bridge steps needed × gas fees × exit slippage
   Formula: Total friction = bridge_in + bridge_out + expected_slippage
   If Total friction > 30% of expected 30-day yield → Not worth it

5. Farming mechanics validation
   - Is there a pool on target chain DEX? (Raydium/Orca for Solana, Uniswap V3 for Ethereum L2s, etc.)
   - What's the current APR (real, not inflated)?
   - Is the pool concentrated liquidity or x*y=k?
   - Rewards token sustainability (if protocol-owned liquidity or emissions)

**Outcome**: One of three recommendations:
- ✅ **Farmable** → Proceed with range/LP sizing strategy
- ⚠️ **Marginal** → Only if bridging costs are one-time and position held >90 days
- ❌ **Not viable** → Abandon on this chain

**Example (this session's findings)**:
| Token | Native Chains | Solana? | 24h Volume | Verdict |
|-------|---------------|--------|------------|---------|
| PROPS | Base, Aptos | ❌ No | $1.7M | ❌ Cross-chain only; not worth bridging |
| LAND  | BSC, Polygon, Arbitrum | ❌ No | $3K | ❌ Extreme illiquidity; exit impossible |
| ONDO  | Ethereum, Solana ✅ | ✅ Yes | $28M | ✅ Consider Solana pools if available |

**Follow-up tasks**:
- If ❌ (not available), monitor for future Solana bridge announcements
- If ⚠️ (marginal), model exact bridge costs with current gas prices and 90-day yield projection
- If ✅ (farmable), proceed to "Range/LP Strategy Design" pattern below

---

## Vault Context Retrieval Pattern (Brain-as-a-Database)

**User directive**: *"use it as a brain literally. Sometimes have context you can pull up is great."* — The vault is not just storage; it's a queryable knowledge base that must be consulted before every strategic analysis.

**When to trigger**:
- Before evaluating a new token/protocol → search for prior analysis
- Before portfolio rebalance → pull historical decision rationale
- Before LP position change → review past IL experiences with similar pairs
- During hackathon project scoping → find past project post-mortems

**Query patterns** (in order of preference):
1. **By tag**: `rg "tags:.*defi.*lp.*" /root/vaults/gentech --md` — structured frontmatter search
2. **By protocol name**: `rg "## PROTOCOL_NAME|PROTOCOL_NAME" /root/vaults/gentech/03-Strategies/ --md` — section headers + inline
3. **By date range**: `rg "2026-0[4-5]" /root/vaults/gentech/03-Strategies/ --md` — recent analyses only
4. **By agent**: `rg "^owner:.*YoYo" /root/vaults/gentech --md` — filter by contributor

**Retrieval workflow**:
```bash
# Step 1: Search with ripgrep (fast, md-only)
QUERY="PROTOCOL_NAME"
RESULTS=$(rg -l "$QUERY" /root/vaults/gentech/03-Strategies/ --type markdown | head -5)

# Step 2: Extract relevant sections with context
for file in $RESULTS; do
  echo "=== $file ==="
  rg -C 3 "$QUERY" "$file" | sed 's/^/  /'
done

# Step 3: Load full note if relevant (Obsidian link format for human follow-up)
echo "\nOpen in Obsidian: $RESULTS"
```

**Automation opportunity**: Wrap as a Hermes skill `strategies/vault-lookup` that returns top 3 relevant notes with excerpts. Use before LP monitoring or protocol research.

**Pitfall — Stale analysis**: Always check `last_updated` in frontmatter. Discard findings >90 days old unless marked `status: archived` (historical reference only).

---

## External Tool Integration Decision Framework

**Context**: Evaluating platforms like Composio that offer managed SaaS integrations vs building direct API calls. Applies to any third-party "tool-as-a-service" platform.

**Decision matrix**:

| Criterion | Build Direct (Hermes) | Use External (Composio-like) |
|-----------|----------------------|------------------------------|
| **Auth complexity** | Each agent manages separate keys/API tokens | Centralized OAuth consent flow, token storage |
| **Tool quantity** | ≤ 10 tools, few endpoints | ≥ 50 tools across ≥ 5 services |
| **Rate limiting** | Manual per-provider handling | Built-in, per-client throttling |
| **Cost sensitivity** | High (minimize spend) | Medium (usage-based acceptable) |
| **Data/privacy** | Sensitive data → keep in-house | Non-PII can pass through proxy |
| **Reliability requirement** | Can self-heal/retry | Need SLA + sandboxed failures |
| **Cross-platform consistency** | Per-platform implementation | Single SDK across providers |
| **Maintenance burden** | Acceptable (few endpoints) | Undesirable (many integrations) |

**Hermes scope** (keep in-house):
- System operations (terminal, file, git, browser automation)
- On-chain blockchain queries (direct RPC)
- Custom DeFi protocol integrations (Uniswap, Aerodrome)
- Local model inference (LLM calls via OpenRouter/local)

**External platform scope** (consider Composio):
- SaaS app APIs with OAuth complexity (Slack, Notion, GitHub issues, Gmail)
- Apps requiring webhooks/triggers
- Services with frequent API version churn
- Tools where auth rotation is frequent/annoying

**Pilot criteria** (start small):
1. Pick 2–3 non-critical toolkits
2. Set hard monthly cost cap ($50–100)
3. Use only for scheduled batch jobs, not real-time agent loops
4. Verify output quality matches direct API calls before scaling

**Example decision** (this session's Composio analysis):
- GitHub API integration → **External candidate** (867 tools, OAuth complexity, rate limits)
- Web scraping → **Hermes** (browser tool + Firecrawl already works)
- Crypto price feeds → **Hermes** (direct DEX/CMC API, no OAuth)

---

## Provider Auth Resilience Pattern

**Trigger**: Recurring provider authentication errors (e.g., "Nous Portal refresh session revoked", "GitHub Copilot 403", API key exhaustion).

**Mitigation stack** (in order of implementation):

### Immediate (this session)
1. **Retry logic** — Wrap API calls with exponential backoff:
   ```python
   import time, random
   
   def resilient_call(fn, max_retries=3, base_delay=5):
       for attempt in range(max_retries):
           try:
               return fn()
           except AuthError as e:
               if attempt == max_retries - 1:
                   raise
               delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
               time.sleep(delay)
   ```
2. **Dead-letter queue** — On permanent failure, write output to `11-Mess Hall/provider-errors/` with:
   - Timestamp, provider, error type
   - Original input prompt/query
   - Suggested remediation (re-auth, rotate key)
   - Alert Gentech in `00-HQ/` with `🔴 Provider Auth` tag

### Short-term (next 24h)
3. **Credential pre-rotation** — Before scheduled critical jobs, proactively validate provider credentials via a health-check endpoint (e.g., `hermes doctor` or provider-specific `/me` endpoint). Auto-rotate if expiry < 24h.
4. **Fallback provider pool** — Maintain secondary API keys per provider. On auth failure, switch to backup key and alert. Avoids complete outage.

### Long-term (architectural)
5. **Credential store abstraction** — Move all provider keys to a central secrets manager (HashiCorp Vault, 1Password, or Hermes credential pools). Agents fetch keys at runtime, not from env/per-profile.
6. **Provider health dashboard** — Track per-provider uptime, error rates, key expiry dates. Visualize in vault `00-HQ/Provider-Health.md`.

**Monitoring**: Add a cron job that scans Hermes gateway logs (`~/.hermes/logs/gateway.log`) for `AuthError|401|403|revoked` and aggregates counts per provider. Alert if any provider crosses threshold (5 failures/hour).

---

## Brain Backup Architecture & Vault Consolidation

**Canonical architecture** (as of 2026-05-03):
```
Primary:     /root/vaults/gentech/          ← Single source of truth (Obsidian)
                 ├── 00-HQ/
                 ├── 03-Strategies/
                 ├── 11-Mess Hall/
                 └── .git → origin = git@github.com:Gentech-Labs/hermes-brain-backup.git

Backup:      GitHub mirror (Gentech-Labs/hermes-brain-backup) ← Auto-pushed every 6h
Stale copy:  /root/repos/hermes-brain/vault/  ← REDUNDANT — DELETE (subset, gets overwritten)
```

**Rules**:
1. **Write only to `/root/vaults/gentech/`** — never to `/root/repos/hermes-brain/vault/` (it's a partial copy that gets clobbered on Hermes updates)
2. **Git push responsibility** — DMOB daily maintenance ensures backup repo is current
3. **Obsidian Headless (`ob` CLI)** unnecessary for local vault sync (only needed for remote vaults on different machines)
4. **All agents** must use `vault_path = "/root/vaults/gentech"` as the base directory for any file operations

**Consolidation actions taken** (May 3, 2026):
- Identified duplicate via `diff -rq /root/repos/hermes-brain/vault /root/vaults/gentech`
- Marked `/root/repos/hermes-brain/vault/` for deletion — it's a stale subset, not actively used
- Cleaned up deprecated GitHub fork `ProtoJay4789/gentech-vault` (empty, no history)

**Verification**:
```bash
# Confirm vault is the only active copy
rg "/root/repos/hermes-brain/vault" ~/.hermes/profiles/*/cron/jobs.json 2>/dev/null
# Should return empty — no job should reference the stale path
```

---

## Cross-Script State Consistency & Ground Truth Protocol

**Ground truth hierarchy**:
1. **On-chain decoded balances** (via `lp-position-reader.py`) — always authoritative
2. **Watchlist/price aggregators** (e.g., `d5-master-cron.py`) — secondary, for market data only
3. **Narrative/summary scripts** (e.g., `d5-milestone-summary.py`) — tertiary, for templated reporting only

**Operational protocol**:
- Daily vault entries must match ground truth numbers exactly (Balance, Efficiency, APR fields)
- If secondary source diverges by >$0.50 or efficiency differs by >5 percentage points, document variance and investigate
- When state files are involved, ensure all profiles point to the same physical file via symlinks (see `references/state-file-symlink-pattern.md`)

**Script-specific roles**:
- `lp-position-reader.py` → produces vault Balance, Efficiency, APR, Range
- `d5-master-cron.py` → produces CMC watchlist alerts, pool volume, price change narrative; does NOT provide vault Balance
- `d5-milestone-summary.py` → reads milestone ladder + tier names; uses ground truth Balance to compute "to-go"; ignore its internal efficiency calc

**Verification** (run daily before vault writes):
```bash
python3 lp-position-reader.py   # mandate these numbers for Balance/Efficiency
python3 d5-master-cron.py       # use for watchlist prices + volume only
# d5-milestone-summary.py → narrative boilerplate only
```

**Drift incident response template** (`09-Green Room/active-handoffs/<date>-script-discrepancy-<owner>.md`):
1. Capture output from all three scripts at same timestamp
2. Identify which script is ground truth and why
3. Document root cause (state path divergence, pending DCA inclusion, config mismatch)
4. Assign remediation task (symlink, config update, code fix) with deadline
5. Update `references/ground-truth-protocol.md` with new edge cases if discovered

---

## Handoff ACK Enforcement & Pre-Escalation Monitoring

**Context**: Gentech coordination protocol (2026-04-20 unified rules) requires recipients to acknowledge handoffs within 2 hours (relaxed to EOD next day for weekend handoffs), with automatic escalation to Jordan if unacknowledged past enforcement deadline. Handoff board is the single source of truth.

**Monitoring cadence**:
- **Every session start** — scan `11-Mess Hall/handoff-board.md` for any handoffs tagged to you; ACK immediately
- **3 hours before enforcement deadline** — run pre-escalation check on any P0/P1 handoffs still in `🚀 Pending Ack` status
- **1 hour before enforcement deadline** — final reminder written to board; if still pending, prepare escalation notice to Jordan

**Pre-escalation checklist** (for handoff owners):
- [ ] Verify the handoff file exists in `09-Green Room/active-handoffs/` or `04-Handoffs/` archive
- [ ] Read acceptance criteria; confirm you can meet them
- [ ] If blocked, update handoff status to `🔴 Blocked — <reason>` and tag Gentech immediately
- [ ] If you cannot complete by deadline, update status to `🟡 Acknowledged — ETA <date>` and notify sender

**Escalation triggers** (automatic):
- 15+ minutes no ACK → Gentech writes reminder to board
- 4+ hours no ACK → Gentech nudges agent directly
- Past enforcement deadline (e.g., 13:45 UTC for May 2 handoffs) → board updated to `🔴 ESCALATED` and Jordan tagged

**Status field conventions**:
- `🚀 Pending Ack` — not yet acknowledged
- `🟡 Claimed` — acknowledged, work in progress
- `🟢 Ready for <owner>` — completed, awaiting next step
- `🔴 Blocked — <reason>` — stuck, needs help
- `🔴 ESCALATED` — past deadline, Jordan notified

**Tooling**: Cron job `d31c330959de` runs every 15 minutes and enforces silently. Do not rely on it as a backup — self-monitor using `references/handoff-enforcement-schedule.md`.

---

## Config-Code Drift Detection (Milestone Ladder)

**Discovery**: `d5-master-cron.py` hardcodes milestone ladder `$5/$20/$55/$200` while `00-HQ/config/defi-lp-config.env` (or a separate config file) specifies `$3/$5/$8/$10/...`. Config drift leads to mis-attributed milestone progress and incorrect DCA sizing.

**Validation pattern**: At script startup (or during handoff acceptance), verify that hardcoded constants match config values.

**Implementation**:
```python
import json

CONFIG_MILESTONES = cfg.get("milestones", [])
CODE_MILESTONES = [5.0, 20.0, 55.0, 200.0]  # or loaded from a constant

def validate_milestone_ladder() -> bool:
    """Assert config and code milestone arrays are identical."""
    config_vals = [m["daily_fees"] for m in CONFIG_MILESTONES]
    if config_vals != CODE_MILESTONES:
        log.error("Milestone ladder mismatch: config=%s code=%s", config_vals, CODE_MILESTONES)
        raise ValueError("Config-code drift detected — reconcile before proceeding")
    return True
```

**When to run**:
- On script start (fail-fast if mismatch)
- During handoff acceptance (DMOB verifies before implementing)
- During vault sync (YoYo checks when updating milestone tracker)

**Remediation**:
1. Decide which source is canonical (prefer config for tunability)
2. Update code to read ladder from config, or update config to match approved ladder
3. Document decision in `03-Strategies/Defi-Monitor/milestone-ladder-reconciliation-<date>.md`

---

## IL Spike Auto-Flag & Review Workflow

**Trigger**: Impermanent Loss (IL) exceeds threshold (default: |IL| > 2% for stable/volatile pair, |IL| > 5% for correlated assets).

**Immediate actions**:
1. Vault entry updated with `🚨 Review` action tag and rationale: "IL spike to X% exceeds Y% threshold — on-chain verification required"
2. Telegram alert sent to `GenTech Strategies` with IL value, price movement, and range status
3. Review assigned to strategy owner (YoYo for D5 position)

**Review checklist**:
- [ ] Re-fetch position via `lp-position-reader.py` to confirm on-chain IL calculation
- [ ] Check price range boundaries — are we still inside target band?
- [ ] Compare efficiency zone — is fee income offsetting IL?
- [ ] Determine root cause: price move vs. rebalancing need vs. oracle delay
- [ ] Decision: Hold / Rebalance now / Wait for recovery
- [ ] Document decision and rationale in vault entry

**Escalation**: IL > 10% → immediate rebalance consideration; alert to Jordan.

---

## Bid-Ask Edge DCA Boost Strategy

**Use when**: LP position efficiency is between 30% and 50% (moderately impaired) and the current price is near the lower boundary of the target range. This indicates elevated risk of a breakout downward; a larger DCA can buy at a favorable price and boost fee-earning capital to restore efficiency.

**Parameters** (stored in config `dca` section):
- `LOWER_EDGE_BUFFER_PCT` — default `0.02` (2%). Price considered "near edge" if `price <= range_low * (1 + LOWER_EDGE_BUFFER_PCT)`.
- `BID_ASK_BOOST_MULTIPLIER` — default `1.5`. Multiplier applied to the base DCA amount when condition holds.

**Condition**:
```python
efficiency_band = (efficiency >= 30) and (efficiency < 50)
near_lower_edge = (price is not None) and (range_low is not None) and (price <= range_low * (1 + LOWER_EDGE_BUFFER_PCT))
if efficiency_band and near_lower_edge:
    boosted_amount = base_amount * BID_ASK_BOOST_MULTIPLIER
```

**Alert integration**: When suggesting a DCA action in an alert message, include `📈 Bid-ask edge — DCA boosted 1.5x` to communicate the rationale.

**Caveats**:
- Do not apply if efficiency ≤30% — that's a critical condition requiring full rebalance, not incremental DCA.
- Do not apply if price is already past the lower edge (out of range) — then the position needs rebalancing, not DCA.
- Ensure `price` and `range_low` are passed into the DCA calculation function; previously some call sites only passed `efficiency`. Update all call sites accordingly.

**Implementation details**: See `references/d5-milestone-enhancements-2026-05.md`.

---

## Vault Logging Integration for Monitoring Scripts

**Requirement**: Every execution of a monitoring script (even silent runs with no alerts) must append a timestamped summary to the vault. This provides an audit trail, enables trend analysis, and satisfies compliance/documentation needs.

**Destination directory**: `03-Strategies/Defi-Monitor/`

**Filename convention**: `YYYY-MM-DD-update.md`. Each run appends a new entry separated by `---`.

**Entry format** (Markdown):
```markdown
## 2026-05-03 18:30 EDT

**Pool**: <pool name> <fee tier>
**Price**: $<price>
**Range**: $<low> – $<high>
**Status**: 🟢 In Range / 🔴 Out of Range
**Efficiency**: <value>%
**Shape**: <CURVE/FULL_RANGE/etc>

**Position**
- Entry: $<entry_price>
- IL: <+/-X.XX>%

**DCA Strategy**
- Zone: <Center/Middle/Edge>
- Amount: $<amount>

**Alerts**: <None / List of alert types>

---
```

**Insertion point**: Call the vault logging function just before the final `print(report)` (or after the report string is constructed but before printing). This ensures the log contains exactly what was sent to Telegram.

**Implementation pattern**:
```python
def log_to_vault(report: str, timestamp: str = None):
    import os, datetime
    VAULT_LOG_DIR = "/root/vaults/gentech/03-Strategies/Defi-Monitor"
    os.makedirs(VAULT_LOG_DIR, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(VAULT_LOG_DIR, f"{today}-update.md")
    header = f"## {timestamp or datetime.datetime.now().strftime('%Y-%m-%d %H:%M EDT')}\n\n"
    with open(log_file, "a") as f:
        f.write(header + report + "\n---\n")
```

**Important**: Use an absolute path pointing to the primary vault (`/root/vaults/gentech/...`). Do not write to any stale copies.
- `references/sidetrack-adapter-workflow.md` — Sidetrack API research template, adapter spec format, sprint integration pattern, common pitfalls
## References

- `references/chain-ecosystem-scan.md` — **NEW:** methodology for mapping a blockchain's protocol landscape by category using DeFiLlama API, with bot-detection fallback patterns
- `D5-Milestone-Tracker-Consolidation.md` — detailed change log for the May 2, 2026 consolidation
- `LP-Monitor-Rules.md` — original monitoring rules and thresholds
- `protocol-due-diligence-framework.md` — risk rating rubric, red flag checklist, vault file template, competitive intel tiers, case studies (AVAX LP, Kite AI, Base agents), quiet hours edge gotcha, config-tracker mismatch fix
- `templates/protocol-evaluation-template.md` — ready-to-use vault file template for new protocol reviews (copy → fill → archive)
- `references/ground-truth-protocol.md` — script discrepancy resolution workflow, state file layout, verification checklist, incident response template
- `references/handoff-enforcement-schedule.md` — Gentech enforcement rules, pre-escalation monitoring cadence, status-field conventions, escalation triggers
- `references/state-file-symlink-pattern.md` — Hermes profile directory layout, symlink commands for `.lfj-*.json` state files, post-symlink validation
- `templates/il-spike-vault-entry.md` — standard vault entry format for IL review flags (action tag, rationale, checklist fields)
- `references/defi-milestone-enhancements-2026-05.md` — **NEW:** session implementation details (immediate ≤30% alert, bid-ask DCA boost, vault logging) with code snippets and thresholds
- `references/portfolio-positioning.md` — **NEW:** Team roster definitions, messaging principles, case study template, value-quantification guide, and "what to include" checklist for Jordan's portfolio
- `references/sidetrack-adapter-workflow.md` — Sidetrack API research template, adapter spec format, sprint integration pattern, common pitfalls
- `references/solana-frontier-hackathon.md` — Solana Frontier tracks, prizes, sidetrack map, AgentEscrow architecture summary, sprint timeline
- `.lfj-aae-config.json` — current configuration schema
- `defi-master-cron.py` — legacy cron orchestration (deprecated)
- `lp-range-monitor-v3.py` — reference for fee efficiency calculations and breakout logic
