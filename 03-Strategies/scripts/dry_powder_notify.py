#!/usr/bin/env python3
"""Dry Powder Mode — Phase 6: Telegram Notification Module

Sends crash alerts, advisory recommendations, and status updates to Jordan via Telegram.
Works in standalone mode or as a library imported by dry_powder_engine.py.

Usage:
    python3 dry_powder_notify.py --test              # Send test message
    python3 dry_powder_notify.py --alert <signal>    # Send crash/recovery alert
    python3 dry_powder_notify.py --status            # Send status summary

Config:
    - TELEGRAM_BOT_TOKEN env var (required for real sends)
    - TELEGRAM_CHAT_ID env var (required — Jordan's chat)
    - Falls back to chat ID from dry-powder-config.json if env not set

Design:
    - Template-based — messages have consistent format
    - Silent mode: messages are rich but not spammy (max 1 per poll cycle)
    - Advisory mode: suggests action, doesn't command
    - Auto mode: notifies after executing action
"""

import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR.parent / "config"
CONFIG_PATH = CONFIG_DIR / "dry-powder-config.json"
STATE_DIR = Path(os.path.expanduser("~/.hermes/state"))
STATE_PATH = STATE_DIR / "dry-powder-state.json"

# ── Templates ──────────────────────────────────────────────────────────────────

CRASH_ALERT_TEMPLATE = """🚨 *DRY POWDER — Crash Alert*

Signal: {signal}
Score: {score}/100
Asset: {symbol} — ${price:.2f} ({change_24h:+.2f}% 24h)

*Triggered Factors:*
{factors}

*Mode:* {mode}
*Recommendation:* {recommendation}

_Checked: {timestamp}_"""

RECOVERY_ALERT_TEMPLATE = """✅ *DRY POWDER — Recovery Signal*

Signal: {signal}
Score: {score}/100
Asset: {symbol} — ${price:.2f} ({change_24h:+.2f}% 24h)

{factors}

*Next step:* {next_step}

_Checked: {timestamp}_"""

STATUS_TEMPLATE = """📊 *Dry Powder Mode — Status Update*

Mode: {mode} | Status: {status}
Last Signal: {last_signal} ({last_score}/100)

Triggers Today: {triggers}
Total Withdrawn: ${withdrawn}
Total Redeployed: ${redeployed}
Current Stables: ${stables}

_Checked: {timestamp}_"""

TEST_TEMPLATE = """🧪 *Dry Powder — Test Message*

This is a test notification from the Dry Powder agent.
If you're reading this, Telegram notifications are working.

*System Status:*
- Engine: {engine_status}
- LP Module: {lp_status}
- Notify Module: ✅ Working

_Test sent: {timestamp}_"""


# ── Helpers ────────────────────────────────────────────────────────────────────


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def load_state():
    defaults = {
        "mode": "advisory",
        "status": "monitoring",
        "last_signal": "SAFE",
        "last_signal_score": 0,
        "triggers_today": 0,
        "total_withdrawn_usd": 0,
        "total_redeployed_usd": 0,
        "current_stable_holdings": 0,
    }
    if STATE_PATH.exists():
        try:
            with open(STATE_PATH) as f:
                data = json.load(f)
                merged = dict(defaults)
                merged.update(data)
                return merged
        except (json.JSONDecodeError, OSError):
            pass
    return dict(defaults)


def get_bot_token() -> str:
    """Get Telegram bot token from env or config."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "") or load_config().get("telegram_bot_token", "")
    return token


def get_chat_id() -> str:
    """Get Telegram chat ID from env or config."""
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "") or load_config().get("notification_channel", "")
    # Strip 'telegram_hq' alias — map to actual chat ID
    if chat_id == "telegram_hq":
        chat_id = os.environ.get("TELEGRAM_HQ_CHAT_ID", "-1003863540828")  # HQ group
    return chat_id


def send_telegram(message: str, parse_mode: str = "Markdown") -> bool:
    """Send a message via Telegram Bot API.

    Returns True on success, False on failure.
    If no bot token is configured, prints to stdout and returns False.
    """
    token = get_bot_token()
    chat_id = get_chat_id()

    if not token:
        print("   ⚠ No TELEGRAM_BOT_TOKEN configured — message printed to stdout:")
        print(message)
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as e:
        print(f"   ❌ Telegram API error: {e.code} — {e.read().decode()[:200]}")
        return False
    except Exception as e:
        print(f"   ❌ Telegram send failed: {e}")
        return False


def format_factors(factors: list) -> str:
    """Format crash/recovery factor list for Telegram."""
    if not factors:
        return "_(none triggered)_"
    lines = []
    for f in factors[:5]:  # Max 5 factors
        name = f.get("factor", "unknown").replace("_", " ")
        score = f.get("score", 0)
        max_score = f.get("max", 100)
        extra = ""
        for key in ("value", "rsi", "ratio"):
            if key in f and f[key] is not None:
                extra = f" ({f[key]})"
                break
        lines.append(f"• {name}{extra} — {score}/{max_score}")
    return "\n".join(lines)


def format_factor_summary(factors: list) -> str:
    """Short inline summary of factors."""
    if not factors:
        return "No signals triggered"
    scores = [f.get("score", 0) for f in factors]
    return f"{len(factors)} factors, {sum(scores)} total points"


# ── Message Builders ──────────────────────────────────────────────────────────


def send_crash_alert(
    signal: str,
    score: int,
    symbol: str,
    price: float,
    change_24h: float,
    factors: list,
    mode: str = "advisory",
) -> bool:
    """Send crash alert to Jordan."""
    recommendation = (
        "Withdraw LP → USDC manually" if mode == "advisory"
        else "Auto-withdrawal triggered"
    )
    msg = CRASH_ALERT_TEMPLATE.format(
        signal=signal,
        score=score,
        symbol=symbol,
        price=price,
        change_24h=change_24h,
        factors=format_factors(factors),
        mode=mode.upper(),
        recommendation=recommendation,
        timestamp=datetime.now().strftime("%H:%M UTC"),
    )
    return send_telegram(msg)


def send_recovery_alert(
    signal: str,
    score: int,
    symbol: str,
    price: float,
    change_24h: float,
    factors: list,
    next_step: str = "Continue monitoring",
) -> bool:
    """Send recovery signal to Jordan."""
    msg = RECOVERY_ALERT_TEMPLATE.format(
        signal=signal,
        score=score,
        symbol=symbol,
        price=price,
        change_24h=change_24h,
        factors=format_factor_summary(factors),
        next_step=next_step,
        timestamp=datetime.now().strftime("%H:%M UTC"),
    )
    return send_telegram(msg)


def send_status_update() -> bool:
    """Send current system status to Jordan."""
    config = load_config()
    state = load_state()
    msg = STATUS_TEMPLATE.format(
        mode=config.get("mode", "advisory"),
        status=state.get("status", "monitoring"),
        last_signal=state.get("last_signal", "SAFE"),
        last_score=state.get("last_signal_score", 0),
        triggers=state.get("triggers_today", 0),
        withdrawn=state.get("total_withdrawn_usd", 0),
        redeployed=state.get("total_redeployed_usd", 0),
        stables=state.get("current_stable_holdings", 0),
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    )
    return send_telegram(msg)


def send_test() -> bool:
    """Send test message to verify notifications work."""
    engine_ok = os.path.exists(SCRIPT_DIR / "dry_powder_engine.py")
    lp_ok = os.path.exists(SCRIPT_DIR / "dry_powder_lp.py")
    msg = TEST_TEMPLATE.format(
        engine_status="✅ Ready" if engine_ok else "❌ Missing",
        lp_status="✅ Ready" if lp_ok else "❌ Missing",
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
    )
    return send_telegram(msg)


# ── Main ──────────────────────────────────────────────────────────────────────


def main():
    if "--test" in sys.argv:
        result = send_test()
        status = "✅ Test message sent!" if result else "⚠ Test printed to stdout (no bot token)"
        print(status)
        return 0

    if "--alert" in sys.argv:
        # Parse alert type from next arg
        alert_type = "crash"
        for i, arg in enumerate(sys.argv):
            if arg == "--alert" and i + 1 < len(sys.argv):
                alert_type = sys.argv[i + 1]
                break

        if alert_type == "crash":
            result = send_crash_alert(
                signal="CRASH",
                score=75,
                symbol="AVAX",
                price=6.70,
                change_24h=-8.5,
                factors=[{"factor": "price_drop_5min", "value": -5.2, "score": 25, "max": 30}],
            )
        elif alert_type == "recovery":
            result = send_recovery_alert(
                signal="RECOVERING",
                score=45,
                symbol="AVAX",
                price=7.10,
                change_24h=1.2,
                factors=[{"factor": "rsi_recovery", "score": 25, "max": 35}],
            )
        else:
            print(f"Unknown alert type: {alert_type}")
            return 1

        status = "✅ Alert sent!" if result else "⚠ Alert printed to stdout"
        print(status)
        return 0

    if "--status" in sys.argv:
        result = send_status_update()
        status = "✅ Status sent!" if result else "⚠ Status printed to stdout"
        print(status)
        return 0

    # Default: test
    print("Dry Powder Notification Module")
    print()
    print("Usage:")
    print("  --test            Send test message")
    print("  --alert [type]    Send alert (crash / recovery)")
    print("  --status          Send status summary")
    print()
    print("Config:")
    print("  TELEGRAM_BOT_TOKEN — Bot token (env var)")
    print("  TELEGRAM_CHAT_ID  — Jordan's chat ID (env var)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
