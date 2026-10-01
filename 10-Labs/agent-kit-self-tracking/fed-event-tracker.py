#!/usr/bin/env python3
"""
Fed Event Tracker — Tracks FOMC meetings, economic indicators, and key events.
Outputs PS5-themed reminders when events are approaching.
Silent when nothing to report.
"""
import json
import os
import json, os, sys
from datetime import datetime, timezone, timedelta

# ── FOMC Auto-Defense integration ──
# Sets LP monitor to SENTINEL mode 24h before FOMC
DEFENSE_STATE_PATH = "/root/.hermes/scripts/.lfj-defi-state.json"

def set_defense_mode(mode, reason):
    """Update LP monitor defense state."""
    try:
        with open(DEFENSE_STATE_PATH) as f:
            state = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        state = {}
    
    state["defense_mode"] = mode
    state["last_defense_action"] = datetime.now(timezone(timedelta(hours=-4))).isoformat()
    state["defense_reason"] = reason
    if mode == "SENTINEL":
        state["breakout_start"] = datetime.now(timezone(timedelta(hours=-4))).isoformat()
    
    os.makedirs(os.path.dirname(DEFENSE_STATE_PATH), exist_ok=True)
    with open(DEFENSE_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)
from dateutil import parser as dateparser
from dateutil.relativedelta import relativedelta

# ── Import PS5 Cron Theme ───────────────────────────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))
from cron_theme import (
    render_header, render_card, close_card, render_row, render_progress_bar,
    render_tree, render_footer, get_status_icon, get_status_color,
    truncate, BLUE, RED, GREEN, YELLOW, SILVER, BLACK
)

# Hub sync config
GITHUB_PAGES_REPO = "/root/repos/gentechlabs.github.io"
ECONOMIC_CALENDAR_PATH = os.path.join(GITHUB_PAGES_REPO, "DeFi", "economic-calendar.json")

# 2026 FOMC Meeting Dates (announced)
FOMC_2026 = [
    {"date": "2026-01-28", "status": "past", "decision": "Hold at 4.25-4.50%"},
    {"date": "2026-03-18", "status": "past", "decision": "Hold at 4.25-4.50%"},
    {"date": "2026-05-06", "status": "past", "decision": "Hold at 4.25-4.50%"},
    {"date": "2026-06-17", "status": "upcoming", "decision": "Pending — Warsh first meeting as Chair"},
    {"date": "2026-07-29", "status": "upcoming", "decision": "Pending"},
    {"date": "2026-09-17", "status": "upcoming", "decision": "Pending — SEP update"},
    {"date": "2026-10-28", "status": "upcoming", "decision": "Pending"},
    {"date": "2026-12-09", "status": "upcoming", "decision": "Pending — SEP update"},
]

# Economic indicators that move the Fed
ECONOMIC_EVENTS = [
    # CPI — Consumer Price Index (inflation)
    {"event": "CPI (MoM)", "dates": ["2026-01-15", "2026-02-12", "2026-03-12", "2026-04-10", "2026-05-13", "2026-06-11", "2026-07-15", "2026-08-12", "2026-09-10", "2026-10-14", "2026-11-12", "2026-12-10"], "importance": "critical"},
    {"event": "CPI (YoY)", "dates": ["2026-01-15", "2026-02-12", "2026-03-12", "2026-04-10", "2026-05-13", "2026-06-11", "2026-07-15", "2026-08-12", "2026-09-10", "2026-10-14", "2026-11-12", "2026-12-10"], "importance": "critical"},
    {"event": "Core CPI (MoM)", "dates": ["2026-01-15", "2026-02-12", "2026-03-12", "2026-04-10", "2026-05-13", "2026-06-11", "2026-07-15", "2026-08-12", "2026-09-10", "2026-10-14", "2026-11-12", "2026-12-10"], "importance": "critical"},

    # PPI — Producer Price Index (wholesale inflation)
    {"event": "PPI (MoM)", "dates": ["2026-01-14", "2026-02-13", "2026-03-13", "2026-04-11", "2026-05-14", "2026-06-12", "2026-07-14", "2026-08-13", "2026-09-11", "2026-10-10", "2026-11-13", "2026-12-11"], "importance": "high"},
    {"event": "PPI (YoY)", "dates": ["2026-01-14", "2026-02-13", "2026-03-13", "2026-04-11", "2026-05-14", "2026-06-12", "2026-07-14", "2026-08-13", "2026-09-11", "2026-10-10", "2026-11-13", "2026-12-11"], "importance": "high"},

    # Jobs / Employment
    {"event": "Non-Farm Payrolls", "dates": ["2026-01-09", "2026-02-06", "2026-03-06", "2026-04-03", "2026-05-08", "2026-06-05", "2026-07-02", "2026-08-07", "2026-09-04", "2026-10-02", "2026-11-06", "2026-12-04"], "importance": "critical"},
    {"event": "Unemployment Rate", "dates": ["2026-01-09", "2026-02-06", "2026-03-06", "2026-04-03", "2026-05-08", "2026-06-05", "2026-07-02", "2026-08-07", "2026-09-04", "2026-10-02", "2026-11-06", "2026-12-04"], "importance": "critical"},
    {"event": "Initial Jobless Claims", "dates": ["weekly"], "importance": "medium"},

    # GDP
    {"event": "GDP (Advance)", "dates": ["2026-01-29", "2026-04-30", "2026-07-30", "2026-10-29"], "importance": "high"},
    {"event": "GDP (2nd Estimate)", "dates": ["2026-02-26", "2026-05-28", "2026-08-27", "2026-11-25"], "importance": "medium"},
    {"event": "GDP (3rd Estimate)", "dates": ["2026-03-26", "2026-06-25", "2026-09-24", "2026-12-18"], "importance": "medium"},

    # PCE — Personal Consumption Expenditures (Fed's preferred inflation gauge)
    {"event": "PCE Price Index (MoM)", "dates": ["2026-01-31", "2026-02-28", "2026-03-27", "2026-04-30", "2026-05-29", "2026-06-26", "2026-07-31", "2026-08-28", "2026-09-25", "2026-10-30", "2026-11-26", "2026-12-19"], "importance": "critical"},
    {"event": "Core PCE (MoM)", "dates": ["2026-01-31", "2026-02-28", "2026-03-27", "2026-04-30", "2026-05-29", "2026-06-26", "2026-07-31", "2026-08-28", "2026-09-25", "2026-10-30", "2026-11-26", "2026-12-19"], "importance": "critical"},

    # Retail Sales
    {"event": "Retail Sales (MoM)", "dates": ["2026-01-16", "2026-02-14", "2026-03-17", "2026-04-15", "2026-05-15", "2026-06-16", "2026-07-16", "2026-08-15", "2026-09-16", "2026-10-16", "2026-11-15", "2026-12-16"], "importance": "high"},

    # ISM Manufacturing & Services
    {"event": "ISM Manufacturing PMI", "dates": ["2026-01-05", "2026-02-02", "2026-03-02", "2026-04-01", "2026-05-01", "2026-06-01", "2026-07-01", "2026-08-03", "2026-09-01", "2026-10-01", "2026-11-02", "2026-12-01"], "importance": "high"},
    {"event": "ISM Services PMI", "dates": ["2026-01-07", "2026-02-05", "2026-03-05", "2026-04-03", "2026-05-06", "2026-06-03", "2026-07-07", "2026-08-05", "2026-09-03", "2026-10-05", "2026-11-04", "2026-12-03"], "importance": "high"},

    # Consumer Confidence
    {"event": "Consumer Confidence (CB)", "dates": ["2026-01-28", "2026-02-25", "2026-03-31", "2026-04-29", "2026-05-27", "2026-06-30", "2026-07-28", "2026-08-26", "2026-09-29", "2026-10-28", "2026-11-25", "2026-12-29"], "importance": "medium"},
    {"event": "UMich Consumer Sentiment (Final)", "dates": ["2026-01-30", "2026-02-27", "2026-03-27", "2026-04-30", "2026-05-29", "2026-06-26", "2026-07-30", "2026-08-28", "2026-09-25", "2026-10-30", "2026-11-25", "2026-12-18"], "importance": "medium"},

    # Housing
    {"event": "Housing Starts", "dates": ["2026-01-17", "2026-02-18", "2026-03-18", "2026-04-17", "2026-05-19", "2026-06-17", "2026-07-17", "2026-08-18", "2026-09-17", "2026-10-19", "2026-11-17", "2026-12-17"], "importance": "medium"},

    # Industrial Production
    {"event": "Industrial Production (MoM)", "dates": ["2026-01-17", "2026-02-14", "2026-03-17", "2026-04-15", "2026-05-15", "2026-06-16", "2026-07-15", "2026-08-15", "2026-09-15", "2026-10-16", "2026-11-17", "2026-12-17"], "importance": "medium"},

    # Fed Speakers (key ones)
    {"event": "Fed Chair Press Conference", "dates": ["2026-06-17", "2026-07-29", "2026-09-17", "2026-10-28", "2026-12-09"], "importance": "critical"},

    # Market-Implied
    {"event": "CME FedWatch Update", "dates": ["daily"], "importance": "high"},
]

# Reminder triggers — days before an event
REMINDER_DAYS = {
    "critical": [7, 3, 2, 1, 0, -1],
    "high": [3, 1, 0],
    "medium": [1, 0],
}

# ── Event Impact Profiles ────────────────────────────────────────────────────
# Maps each event to its market impact, volatility range, and rainbow zone shift
EVENT_IMPACT = {
    "CPI (MoM)": {
        "crypto_vol": "2-5% BTC, 3-8% altcoins",
        "direction": "Hot CPI → risk-off (crypto down). Cool CPI → risk-on (crypto up).",
        "rainbow_shift": "Hot CPI could push AVAX from Harvest Mode → Bleeding Edge. Cool CPI → Peak Yield.",
        "fed_signal": "Higher inflation = higher-for-longer rates = bad for risk assets",
        "typical_move": "AVAX ±3-6% within 2 hours of release",
    },
    "CPI (YoY)": {
        "crypto_vol": "2-5% BTC, 3-8% altcoins",
        "direction": "Same as MoM but market weights the YoY trend more heavily.",
        "rainbow_shift": "Sustained YoY decline = sustained Harvest Mode+. Sticky YoY = Bleeding Edge risk.",
        "fed_signal": "Trend matters more than print — market prices in 6-month rate path",
        "typical_move": "AVAX ±3-6%, trend follows for 1-3 days",
    },
    "Core CPI (MoM)": {
        "crypto_vol": "2-5% BTC, 3-8% altcoins",
        "direction": "Core = ex-food/energy. Fed watches this closest. Surprise moves are violent.",
        "rainbow_shift": "Core hot = Bleeding Edge or Panic Farm. Core cool = Peak Yield zone.",
        "fed_signal": "Core persistence = rate cuts delayed = crypto bearish",
        "typical_move": "AVAX ±4-7% — core surprises hit harder than headline",
    },
    "PPI (MoM)": {
        "crypto_vol": "1-3% BTC, 2-5% altcoins",
        "direction": "Leading indicator for CPI. Higher PPI → CPI likely hot → crypto down.",
        "rainbow_shift": "PPI spike = forward-looking CPI fear = potential Bleeding Edge shift.",
        "fed_signal": "Wholesale costs pass through to consumers → inflation persistence",
        "typical_move": "AVAX ±2-4%, muted vs CPI",
    },
    "Non-Farm Payrolls": {
        "crypto_vol": "2-4% BTC, 3-6% altcoins",
        "direction": "Hot jobs = economy strong = rates stay high = crypto down. Weak jobs = rate cuts incoming = crypto up.",
        "rainbow_shift": "Strong NFP = risk-off → Bleeding Edge. Weak NFP = rate cut hopes → Peak Yield.",
        "fed_signal": "Labor market is dual mandate #2. Weak jobs = Fed pivots sooner",
        "typical_move": "AVAX ±3-5%, directional move holds for hours",
    },
    "Unemployment Rate": {
        "crypto_vol": "2-4% BTC, 3-6% altcoins",
        "direction": "Rising unemployment = Fed must cut = crypto bullish. Falling = higher for longer.",
        "rainbow_shift": "Rising unemployment → Harvest Mode or Peak Yield. Falling → Bleeding Edge.",
        "fed_signal": "4.0%+ unemployment triggers emergency cut discussions",
        "typical_move": "AVAX ±2-5%, less volatile than NFP headline",
    },
    "GDP (3rd Estimate)": {
        "crypto_vol": "1-2% BTC, 2-3% altcoins",
        "direction": "Revision of prior quarter. Big revisions move markets. Small ones ignored.",
        "rainbow_shift": "Minimal direct impact on yield farming unless revision is massive (±1%).",
        "fed_signal": "Stagflation risk: weak GDP + high inflation = worst case for risk assets",
        "typical_move": "AVAX ±1-3%, usually a non-event unless surprise revision",
    },
    "PCE Price Index (MoM)": {
        "crypto_vol": "2-5% BTC, 3-8% altcoins",
        "direction": "THE Fed's preferred inflation gauge. More important than CPI for rate decisions.",
        "rainbow_shift": "Hot PCE = Bleeding Edge or Panic Farm. Cool PCE = Peak Yield territory.",
        "fed_signal": "This is what the Fed actually targets. 2% annual PCE is the goal.",
        "typical_move": "AVAX ±3-6%, can trigger multi-day trend",
    },
    "Core PCE (MoM)": {
        "crypto_vol": "2-5% BTC, 3-8% altcoins",
        "direction": "Ex-food/energy PCE. THE single most important number for rate path.",
        "rainbow_shift": "Core PCE surprise = instant rainbow zone shift. This is the one that matters most.",
        "fed_signal": "If Core PCE stays above 2.5%, no rate cuts in 2026. Below 2.5% = cuts likely.",
        "typical_move": "AVAX ±4-7%, biggest move of any economic release",
    },
    "UMich Consumer Sentiment (Final)": {
        "crypto_vol": "1-2% BTC, 2-4% altcoins",
        "direction": "Inflation expectations component matters. High expectations = sticky inflation = bearish.",
        "rainbow_shift": "Low sentiment + high inflation fears = Bleeding Edge. High sentiment = neutral.",
        "fed_signal": "Consumer expectations self-fulfill — if consumers expect inflation, they spend faster",
        "typical_move": "AVAX ±1-3%, sentiment survey is softer data",
    },
    "ISM Manufacturing PMI": {
        "crypto_vol": "1-3% BTC, 2-5% altcoins",
        "direction": "Above 50 = expansion, below 50 = contraction. Contraction = rate cuts = crypto up.",
        "rainbow_shift": "Manufacturing contraction → rate cut hopes → Peak Yield. Expansion → rates stay → Bleeding.",
        "fed_signal": "Manufacturing weakness forces Fed hand on cuts",
        "typical_move": "AVAX ±2-4%, directional but less than CPI/PCE",
    },
    "ISM Services PMI": {
        "crypto_vol": "1-3% BTC, 2-5% altcoins",
        "direction": "Services = 70% of US economy. More important than manufacturing.",
        "rainbow_shift": "Services contraction is rare and signals serious economic weakness → Harvest Mode.",
        "fed_signal": "Services inflation is sticky — high services PMI = inflation persists",
        "typical_move": "AVAX ±2-4%",
    },
    "Consumer Confidence (CB)": {
        "crypto_vol": "1-2% BTC, 2-3% altcoins",
        "direction": "Confidence drops = spending slows = economy weakens = rate cuts.",
        "rainbow_shift": "Low confidence = forward-looking rate cut signal → potential Peak Yield.",
        "fed_signal": "Confidence leads actual spending by 1-2 months",
        "typical_move": "AVAX ±1-3%",
    },
    "Retail Sales (MoM)": {
        "crypto_vol": "1-3% BTC, 2-4% altcoins",
        "direction": "Consumer spending = GDP driver. Weak sales = economy slowing = rate cuts.",
        "rainbow_shift": "Weak retail = economic slowdown = rate cut hopes → Harvest Mode.",
        "fed_signal": "Retail weakness = consumer weakness = Fed must act",
        "typical_move": "AVAX ±2-4%",
    },
    "Fed Chair Press Conference": {
        "crypto_vol": "3-8% BTC, 5-12% altcoins",
        "direction": "THE volatility event. Warsh doesn't telegraph — he acts and explains after.",
        "rainbow_shift": "Hawkish surprise = Panic Farm. Dovish surprise = Euphoria. No middle ground.",
        "fed_signal": "New paradigm: no forward guidance. Market reacts to ACTIONS, not words.",
        "typical_move": "AVAX ±5-10% during presser, can extend for days",
    },
    "Housing Starts": {
        "crypto_vol": "1-2% BTC, 1-3% altcoins",
        "direction": "Housing = interest rate sensitive. Weak starts = rates too high = cut pressure.",
        "rainbow_shift": "Minimal direct impact on crypto yield farming.",
        "fed_signal": "Housing weakness is lagging indicator for rate impact",
        "typical_move": "AVAX ±1-2%, usually a non-event",
    },
    "Industrial Production (MoM)": {
        "crypto_vol": "1-2% BTC, 1-3% altcoins",
        "direction": "Factory output = economic activity. Declining = recession risk.",
        "rainbow_shift": "Minimal direct impact.",
        "fed_signal": "Production decline supports rate cut narrative",
        "typical_move": "AVAX ±1-2%",
    },
}

# Warsh era context — no telegraphing
WARSH_CONTEXT = """
⚡ WARSH ERA NOTE: New Fed Chair doesn't telegraph moves.
Unlike Powell, Warsh acts THEN explains. This means:
• FOMC meetings are HIGH VOLATILITY — expect surprises
• PCE/CPI prints hit harder (no pre-positioning by market)
• Press conferences are reaction events, not guidance events
• Rainbow zone can shift 2+ bands in a single day
"""


def parse_date(date_str):
    """Parse a date string."""
    return dateparser.parse(date_str)


def _write_calendar(hub_events, today):
    """Write the hub's economic calendar. ALWAYS writes — a quiet day is a fact worth recording.

    Factored out 2026-09-27 because the writer used to live only on the "there IS an event" path
    (behind an early `return  # empty = SILENT`), so on quiet days the file was never rewritten
    and kept asserting a stale "TODAY" event for ten days. One writer, called from both paths,
    is the version that cannot drift apart again.
    """
    hub_data = {
        "lastUpdated": datetime.now().isoformat() + "Z",
        "date": today.strftime("%A, %B %d, %Y"),
        "events": list(hub_events or []),
        "summary": (f"Macro impact analysis for AVAX/USDC LP farming. {len(hub_events)} event(s) today."
                    if hub_events else
                    "No high-impact macro events in the reminder window — nothing today."),
    }
    try:
        os.makedirs(os.path.dirname(ECONOMIC_CALENDAR_PATH), exist_ok=True)
        with open(ECONOMIC_CALENDAR_PATH, "w") as f:
            json.dump(hub_data, f, indent=2)
        print(f"Economic calendar refreshed: {len(hub_events or [])} high-impact event(s) in window."
              + ("" if hub_events else " (events: [] — nothing today)"))
    except Exception as e:
        # NOT silent. This write failing IS how the file went stale, and a swallowed error is
        # indistinguishable from a successful refresh.
        print(f"  ⚠️  could not refresh the economic calendar at {ECONOMIC_CALENDAR_PATH}: "
              f"{type(e).__name__}: {e}")


def main():
    now = datetime.now()
    today = now.date()
    today_str = today.isoformat()

    events = []

    # Check FOMC meetings
    for meeting in FOMC_2026:
        try:
            event_date = datetime.strptime(meeting["date"], "%Y-%m-%d").date()
        except:
            continue
        days_until = (event_date - today).days

        if days_until == 2:
            events.append(("FOMC", f"⚠️ FOMC in 2 DAYS — {meeting['decision']}"))
        elif days_until == 1:
            events.append(("FOMC", f"🔔 FOMC TOMORROW — {meeting['decision']}"))
            set_defense_mode("SENTINEL", f"FOMC tomorrow ({meeting['decision']})")
        elif days_until == 0:
            events.append(("FOMC", f"🚨 FOMC TODAY — {meeting['decision']}"))
            set_defense_mode("SENTINEL", f"FOMC today ({meeting['decision']})")
        elif days_until == -1:
            events.append(("FOMC", f"📊 FOMC was YESTERDAY — {meeting['decision']}"))
            set_defense_mode("SENTINEL", f"Post-FOMC ({meeting['decision']}) — awaiting clear signal")

    # Check economic events
    for econ in ECONOMIC_EVENTS:
        if econ["dates"] == ["weekly"] or econ["dates"] == ["daily"]:
            continue

        importance = econ["importance"]
        reminder_days = REMINDER_DAYS.get(importance, [0])

        for date_str in econ["dates"]:
            try:
                event_date = parse_date(date_str).date()
            except Exception:
                continue

            days_until = (event_date - today).days

            if days_until in reminder_days:
                emoji_map = {"critical": "🔴", "high": "🟠", "medium": "🟡"}
                emoji = emoji_map.get(importance, "⚪")

                if days_until == 0:
                    prefix = f"{emoji} TODAY"
                elif days_until == 1:
                    prefix = f"{emoji} TOMORROW"
                elif days_until == -1:
                    prefix = f"{emoji} YESTERDAY"
                else:
                    prefix = f"{emoji} in {days_until} days"

                events.append((importance, f"{prefix}: {econ['event']}"))

    if not events:
        # ── A QUIET DAY MUST STILL REFRESH THE FILE (fixed 2026-09-27) ───────────────────────
        # This early return is the ORIGIN of the stale-calendar bug. "empty = SILENT" is right for
        # the NOTIFICATION (nobody wants a ping saying nothing happened) and wrong for the FILE.
        # Returning here meant the writer below never ran on a quiet day, so the previous file
        # survived with its events still reading time:"TODAY" indefinitely.
        #
        # Measured: /var/www/gentechlabs/DeFi/economic-calendar.json sat 245 HOURS (10 days) old
        # still asserting "high-impact event TODAY: PPI (MoM), PPI (YoY)". posture's protection
        # layer reads that string, so macro_imminent stayed True on every run, PROTECTION
        # short-circuited to FARM_BIDASK, and the market and regime never got a vote on the shape.
        # Jordan's book read as a bid-ask the market wanted to be a curve because the only layer
        # wanting bid-ask was reading a ten-day-old file.
        #
        # A calendar's value includes the NEGATIVE fact ("nothing today"), and a consumer cannot
        # read a negative fact from a file that was never rewritten. So we still stay silent on
        # stdout for the notification, but we MUST still write the file and stamp lastUpdated.
        _write_calendar([], today)
        return  # still SILENT on output — that part was always right

    # Sort: FOMC first, then by importance
    importance_order = {"FOMC": 0, "critical": 1, "high": 2, "medium": 3}
    events.sort(key=lambda x: importance_order.get(x[0], 99))

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # VISUAL UPGRADE: AAE DeFi Milestone theme
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # Initialize lines list
    lines = []
    
    # Header with box-drawing
    lines.append("┌────────────────────────────────────────────────────────┐")
    lines.append("│ 📋 **Economic Calendar**                              │")
    lines.append(f"│ {today.strftime('%A, %B %d, %Y'):51s} │")
    lines.append("└────────────────────────────────────────────────────────┘")
    lines.append("")

    # Quick scan: events list
    if events:
        lines.append("🗓️ **Upcoming Events**")
        for _, msg in events:
            lines.append(f"  ├─ {msg}")
        lines.append("")

    # Collect impact events for today/tomorrow
    impact_events = []
    for event in ECONOMIC_EVENTS:
        if event["dates"] == ["weekly"] or event["dates"] == ["daily"]:
            continue
        for date_str in event["dates"]:
            try:
                event_date = parse_date(date_str).date()
                days_until = (event_date - today).days
                if days_until in [0, 1]:
                    impact_events.append((days_until, event["event"], event["importance"]))
            except Exception:
                continue

    # Add FOMC impact if upcoming
    for meeting in FOMC_2026:
        event_date = parse_date(meeting["date"]).date()
        days_until = (event_date - today).days
        if days_until in [0, 1, 2]:
            impact_events.append((days_until, "Fed Chair Press Conference", "critical"))

    # Impact analysis card
    if impact_events:
        lines.append("┌────────────────────────────────────────────────────────┐")
        lines.append("│ 📊 **Impact Analysis — AVAX/USDC LP**                │")
        lines.append("└────────────────────────────────────────────────────────┘")
        lines.append("")

        for days, event_name, importance in impact_events:
            impact = EVENT_IMPACT.get(event_name)
            if not impact:
                continue
            timing = "TODAY" if days == 0 else "TOMORROW" if days == 1 else f"in {days} days"
            emoji = "🔴" if importance == "critical" else "🟠" if importance == "high" else "🟡"
            
            lines.append(f"{emoji} **{event_name}** — `{timing}`")
            lines.append(f"├─ Volatility: `{impact['crypto_vol']}`")
            lines.append(f"├─ Direction: {impact['direction']}")
            lines.append(f"├─ Rainbow shift: `{impact['rainbow_shift']}`")
            lines.append(f"└─ Expected move: `{impact['typical_move']}`")
            lines.append("")

    # Warsh context card (if FOMC week)
    has_fomc = any(
        parse_date(m["date"]).date() - today in range(0, 8)
        for m in FOMC_2026 if m["status"] == "upcoming"
    )
    if has_fomc:
        lines.append("⚡ **WARSH ERA NOTE**")
        lines.append("└─ No telegraphing. FOMC meetings are HIGH VOLATILITY.")
        lines.append("└─ PCE/CPI hit harder. Press conferences = reaction events.")
        lines.append("└─ Rainbow zone can shift 2+ bands in a single day.")
        lines.append("")

    # Position reminder card
    lines.append("┌────────────────────────────────────────────────────────┐")
    lines.append("│ 🎯 **Your Position**                                   │")
    lines.append("│ AVAX/USDC LP | Check live range & efficiency          │")
    lines.append("│ Price at event → rainbow zone shift → action         │")
    lines.append("└────────────────────────────────────────────────────────┘")
    lines.append("")

    print("\n".join(lines))

    # === Hub JSON Sync ===
    # Build structured JSON for the Hub's economic calendar section
    hub_events = []
    for days, event_name, importance in impact_events:
        impact = EVENT_IMPACT.get(event_name, {})
        timing = "TODAY" if days == 0 else "TOMORROW" if days == 1 else f"in {days} days"
        emoji_map = {"critical": "🔴", "high": "🟠", "medium": "🟡"}
        hub_events.append({
            "name": event_name,
            "time": timing,
            "impact": importance,
            "emoji": emoji_map.get(importance, "⚪"),
            "forecast": "—",
            "previous": "—",
            "description": impact.get("direction", ""),
            "volatility": impact.get("crypto_vol", ""),
            "avxBias": impact.get("rainbow_shift", ""),
        })

    # Also include FOMC if upcoming
    for meeting in FOMC_2026:
        event_date = parse_date(meeting["date"]).date()
        days_until = (event_date - today).days
        if days_until in [0, 1, 2]:
            timing = "TODAY" if days_until == 0 else "TOMORROW" if days_until == 1 else f"in {days_until} days"
            hub_events.append({
                "name": "FOMC Meeting",
                "time": timing,
                "impact": "critical",
                "emoji": "🚨",
                "forecast": meeting["decision"],
                "previous": "—",
                "description": "Fed interest rate decision. Warsh era — no telegraphing, expect surprises.",
                "volatility": "5-12% altcoins during presser",
                "avxBias": "Hawkish surprise = Panic Farm. Dovish = Euphoria.",
            })

    # ── A QUIET DAY MUST STILL REFRESH THE FILE (fixed 2026-09-27) ───────────────────────────
    # This was `if hub_events:` — the writer ran ONLY when an event was near. On a quiet day it
    # wrote nothing, so the PREVIOUS file survived with its events still reading time:"TODAY"
    # indefinitely. Measured: the live calendar sat 245 hours (10 days) old still asserting
    # "high-impact event TODAY: PPI (MoM), PPI (YoY)". posture's protection layer reads that
    # string, so macro_imminent stayed True on EVERY run, PROTECTION short-circuited to
    # FARM_BIDASK, and the market and regime never got a vote on the shape. Jordan's book read as
    # a bid-ask the market wanted to be a curve because the only layer wanting bid-ask was
    # reading a ten-day-old file.
    #
    # A calendar's value includes the NEGATIVE fact ("nothing today"), and a consumer cannot read
    # a negative fact from a file that was never rewritten. So: ALWAYS write, always stamp
    # lastUpdated, and an empty events list MEANS "nothing high-impact today".
    _write_calendar(hub_events, today)


if __name__ == "__main__":
    main()
