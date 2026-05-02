#!/usr/bin/env python3
"""
Opportunity Scanner — Daily Monitor (DMOB Labs)
Scans validated cached data (manually verified results)
Updates: 02-Labs/Bug-Bounties/00-Active-Bounties.md
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

VAULT = Path("/root/vaults/gentech")
SCAN_DIR = VAULT / "02-Labs" / "Contest-Scans"
SCAN_DIR.mkdir(parents=True, exist_ok=True)
BOUNTIES_FILE = VAULT / "02-Labs" / "Bug-Bounties" / "00-Active-Bounties.md"
NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%Y-%m-%d")
LOG = SCAN_DIR / f"scan_{TODAY}.log"

def log(m):
    ts = NOW.strftime("%H:%M:%S")
    print(f"[{ts}] {m}")
    with open(LOG, "a") as f:
        f.write(m + "\n")

def days_left(end_str):
    if not end_str or end_str.upper() in ("TBD","TBA","LIVE","ONGOING"): return 999
    try:
        end = datetime.fromisoformat(end_str.replace("Z","+00:00"))
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        return max(0, (end - NOW).days)
    except Exception:
        return 999

def clean_prize(s): return re.sub(r"\s+", " ", str(s or "")).strip().upper()

def qualify(prize, days, chain="", platform=""):
    amt = float(re.sub(r"[^0-9.]","",prize or "0"))
    if amt >= 1000 and days >= 7: return True
    if chain.lower() in ("solana","base") and amt >= 5000: return True
    if platform == "Devpost" and amt >= 10000 and days >= 7: return True
    return False

def load_cache(key):
    p = SCAN_DIR / f"{key}_cached.json"
    if p.exists():
        try: return json.loads(p.read_text())
        except: pass
    return []

def scan_code4rena(): return load_cache("c4")
def scan_cantina(): return load_cache("cantina")
def scan_devpost(): return load_cache("devpost")
def scan_colosseum(): return load_cache("colosseum")

def main():
    log("=== Daily Opportunity Scan ===")
    all = []
    all.extend(scan_code4rena())
    all.extend(scan_cantina())
    all.extend(scan_devpost())
    all.extend(scan_colosseum())

    # Compute days_left from deadline if missing/placeholder
    for c in all:
        if c.get("days_left", 999) == 999 and c.get("deadline"):
            c["days_left"] = days_left(c["deadline"])

    seen = {}
    for c in all:
        key = (c["platform"], c["name"])
        if key not in seen: seen[key] = c

    qualified = [c for c in seen.values() if qualify(c["prize"], c["days_left"], c.get("chain",""), c["platform"])]
    qualified.sort(key=lambda c: -float(re.sub(r"[^0-9.]","",c["prize"] or "0")))

    # Build markdown table
    lines = [
        "# Bug Bounties — Active List",
        f"**Updated:** {TODAY}",
        "**Sorted by:** Prize (highest first)",
        "",
        "## Qualifying Contests",
        "",
        "| Platform | Contest | Prize | Time Left | Chain | Deadline |",
        "|----------|---------|-------|-----------|-------|----------|",
    ]
    for c in qualified:
        name = (c["name"][:42] + "…") if len(c["name"]) > 42 else c["name"]
        link = c["link"]
        lines.append(f"| {c['platform']} | [{name}]({link}) | {c['prize']} | {c['days_left']}d | {c['chain'][:6]} | {c['deadline']} |")

    lines.extend([
        "",
        "## Sprint Focus (May 2–17, 2026)",
        "- Priority 1: Solana Frontier (AgentEscrow) — May 11",
        "- Priority 2: Kite AI Global (AAE Brain) — May 17",
        "- Active: Reserve Governor (Cantina, $30K, 8d left)",
        "- Watchlist: IGNITION ($5.12M), K2 ($135K), Monetrix ($22K)",
        "",
        f"*Automated — logged to `{SCAN_DIR.relative_to(VAULT)}/`*",
        "",
        "#bug-bounties #security #automation"
    ])

    BOUNTIES_FILE.write_text("\n".join(lines) + "\n")
    log(f"Wrote bounties: {BOUNTIES_FILE}")

    summary = SCAN_DIR / f"summary_{TODAY}.md"
    summary_lines = [f"# Scan Summary — {TODAY}", f"**Qualified:** {len(qualified)} contests", "", "**Top 3:**"]
    for c in qualified[:3]:
        summary_lines.append(f"- {c['name']} — {c['prize']} ({c['days_left']}d, {c['chain']})")
        summary_lines.append(f"  {c['link']}")
    summary.write_text("\n".join(summary_lines) + "\n")
    log(f"Summary: {summary}")

    log("=== Done ===")
    return 0

if __name__ == "__main__": sys.exit(main())
