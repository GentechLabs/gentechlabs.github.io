#!/usr/bin/env python3
"""
Opportunity Scanner v2 — DMOB Labs
Daily scan of security contests across Code4rena, Cantina, Devpost, Colosseum
Uses Playwright for SPA sites + push-segment decoder for C4
Stores raw artifacts in `02-Labs/Contest-Scans/` for re-audit
Updates `02-Labs/Bug-Bounties/00-Active-Bounties.md`
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Any

VAULT = Path("/root/vaults/gentech")
SCAN_ROOT = VAULT / "02-Labs" / "Contest-Scans"
SCAN_ROOT.mkdir(parents=True, exist_ok=True)
BOUNTIES_FILE = VAULT / "02-Labs" / "Bug-Bounties" / "00-Active-Bounties.md"

NOW = datetime.now(timezone.utc)
TODAY = NOW.strftime("%Y-%m-%d")
LOG_FILE = SCAN_ROOT / f"scan_{TODAY}.log"

def log(msg: str):
    ts = NOW.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")

# ── Utilities ──────────────────────────────────────────────────────────────────
def days_remaining(end_str: str) -> int:
    if not end_str or end_str.upper() in ("TBD", "TBA", "LIVE", "ONGOING"):
        return 999
    try:
        end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        return max(0, (end - NOW).days)
    except Exception:
        return 0

def clean_prize(raw: Any) -> str:
    s = str(raw or "")
    s = re.sub(r"\s+", " ", s).strip()
    return s.upper()

def qualify(prize_raw: str, days: int, chain: str = "", platform: str = "") -> bool:
    num = float(re.sub(r"[^0-9.]", "", prize_raw or "0"))
    if num >= 1000 and days >= 7:
        return True
    if chain.lower() in ("solana", "base") and num >= 5000:
        return True
    if platform == "Devpost" and num >= 10000 and days >= 7:
        return True
    return False

# ── Code4rena: Push-Segment Decoder ───────────────────────────────────────────
def scan_code4rena() -> List[Dict]:
    url = "https://code4rena.com/contests"
    raw_path = SCAN_ROOT / f"c4_raw_{TODAY}.html"
    try:
        subprocess.run(
            ["curl", "-sL", "-A", "Mozilla/5.0 (compatible; DMOB-Scanner/1.0)", "-o", str(raw_path), url],
            timeout=30, check=True
        )
        raw = raw_path.read_text(errors="replace")
    except Exception as e:
        log(f"[C4] curl failed: {e}")
        return []

    # Try __NEXT_DATA__ first (structured state)
    next_match = re.search(r'id="__NEXT_DATA__"[^>]*>(\{.*?\})</script>', raw, re.DOTALL)
    if next_match:
        try:
            state = json.loads(next_match.group(1))
            contests = state.get("props", {}).get("pageProps", {}).get("audits", {}).get("Active", [])
            parsed = []
            for c in contests:
                parsed.append({
                    "platform": "Code4rena",
                    "name": c.get("title", ""),
                    "prize": clean_prize(c.get("formattedAmount", "")),
                    "days_left": days_remaining(c.get("endsAt", "TBD")),
                    "deadline": (c.get("endsAt") or "TBD")[:10],
                    "chain": c.get("league", "EVM"),
                    "link": f"https://code4rena.com/contests/{c.get('id','')}",
                    "raw": c,
                })
            log(f"[C4] Parsed {len(parsed)} from __NEXT_DATA__")
            return parsed
        except Exception as e:
            log(f"[C4] __NEXT_DATA__ parse error: {e}")

    # Fallback: push-segment reconstruction
    log("[C4] Falling back to push-segment decode")
    segments = re.findall(r'\]\}\],\d+,\[', raw)
    if not segments:
        log("[C4] No push segments found")
        return []
    combined = "[" + ",".join(segments) + "]"
    try:
        data = json.loads(combined)
        # Drill into known structure: data → [0] → state → audits → Active
        state = data[0][2] if len(data[0]) > 2 else data[0]
        contests = state.get("audits", {}).get("Active", [])
        parsed = []
        for c in contests:
            parsed.append({
                "platform": "Code4rena",
                "name": c.get("title", ""),
                "prize": clean_prize(c.get("formattedAmount", "")),
                "days_left": days_remaining(c.get("endsAt", "TBD")),
                "deadline": (c.get("endsAt") or "TBD")[:10],
                "chain": c.get("league", "EVM"),
                "link": f"https://code4rena.com/contests/{c.get('id','')}",
            })
        log(f"[C4] Decoded {len(parsed)} from push segments")
        return parsed
    except Exception as e:
        log(f"[C4] Push decode failed: {e}")
        return []

# ── Cantina: Playwright Render ─────────────────────────────────────────────────
def scan_cantina() -> List[Dict]:
    """Render Cantina SPA with Playwright and scrape competition cards."""
    script = SCAN_ROOT / "cantina_playwright.py"
    script.write_text("""
from playwright.sync_api import sync_playwright
import json, sys
p = sync_playwright().start()
browser = p.chromium.launch(headless=True)
page = browser.new_page(user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
page.goto('https://cantina.xyz/competitions', wait_until='networkidle', timeout=30000)
page.wait_for_timeout(3000)
cards = page.query_selector_all('a[href*="/competitions/"]')
out = []
for c in cards:
    href = c.get_attribute('href')
    text = c.inner_text()[:500]
    out.append({'href': href, 'text': text})
print(json.dumps(out))
browser.close()
p.stop()
""")
    try:
        result = subprocess.run(
            ["/usr/local/lib/hermes-agent/venv/bin/python3", str(script)],
            capture_output=True, text=True, timeout=60
        )
        cards = json.loads(result.stdout)
        parsed = []
        for card in cards:
            href = card.get("href", "")
            text = card.get("text", "")
            # Heuristic: prize ~$XXXXX, date in text
            prize_m = re.search(r'\$([\d,]+)', text)
            date_m = re.search(r'(\d{1,2}/\d{1,2}/\d{4})|([A-Z][a-z]+ \d{1,2}, \d{4})', text)
            parsed.append({
                "platform": "Cantina",
                "name": text.split('\\n')[0][:60] if '\\n' in text else text[:60],
                "prize": f"${prize_m.group(1) if prize_m else '?'}",
                "days_left": 999,  # will refine later per-competition
                "deadline": date_m.group(0) if date_m else "TBD",
                "chain": "Base",  # from our earlier per-page fetch; refine later
                "link": ("https://cantina.xyz" + href) if href.startswith("/") else href,
                "_raw_text": text,
            })
        log(f"[Cantina] Scraped {len(parsed)} cards")
        return parsed
    except Exception as e:
        log(f"[Cantina] Playwright error: {e}")
        return []

# ── Devpost API ────────────────────────────────────────────────────────────────
def scan_devpost() -> List[Dict]:
    url = "https://devpost.com/api/hackathons?limit=50&page=1"
    try:
        subprocess.run(["curl", "-sL", "-o", str(SCAN_ROOT / f"devpost_{TODAY}.json"), url], timeout=30, check=True)
        data = json.loads((SCAN_ROOT / f"devpost_{TODAY}.json").read_text())
        contests = data.get("hackathons", [])
        parsed = []
        for c in contests:
            prize = c.get("prize") or f"${c.get('prize_amount', 0):,}"
            end_raw = c.get("ends_at", "")
            end_dt = datetime.fromisoformat(end_raw.replace("Z", "+00:00")) if end_raw else None
            parsed.append({
                "platform": "Devpost",
                "name": c.get("title", ""),
                "prize": prize,
                "days_left": max(0, (end_dt - NOW).days) if end_dt else 999,
                "deadline": end_dt.strftime("%Y-%m-%d") if end_dt else "TBD",
                "chain": "Multi",  # infer from description later
                "link": c.get("url", ""),
            })
        log(f"[Devpost] Found {len(parsed)} hackathons")
        return parsed
    except Exception as e:
        log(f"[Devpost] API failed: {e}")
        return []

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    log("=== Opportunity Scanner v2 ===")
    all_contests = []

    all_contests.extend(scan_code4rena())
    all_contests.extend(scan_cantina())
    all_contests.extend(scan_devpost())

    # Filter + dedupe by name+platform
    uniq = {}
    for c in all_contests:
        key = (c["platform"], c["name"])
        if key not in uniq:
            uniq[key] = c
        else:
            existing = uniq[key]
            # Keep entry with fresher deadline
            if c["days_left"] < existing["days_left"]:
                uniq[key] = c

    qualifying = [
        c for c in uniq.values()
        if qualify(c["prize"], c["days_left"], c.get("chain",""), c["platform"])
    ]

    log(f"Total: {len(all_contests)} → {len(qualifying)} qualifying")

    # Sort by prize amount descending
    def prize_key(c):
        n = float(re.sub(r"[^0-9.]", "", c["prize"] or "0"))
        return -n
    qualifying.sort(key=prize_key)

    # Generate Markdown table
    lines = [
        "# Bug Bounties — Active List",
        f"**Updated:** {TODAY}",
        "**Sorted by:** Prize (highest first)",
        "**Sources:** Code4rena, Cantina, Devpost — scanned daily at 09:00 UTC",
        "",
        "## Qualifying Contests",
        "",
        "| Platform | Contest | Prize | Time Left | Chain | Deadline |",
        "|----------|---------|-------|-----------|-------|----------|",
    ]
    for c in qualifying:
        days = c["days_left"]
        dl = c["deadline"]
        link = c["link"]
        name = (c["name"][:45] + "…") if len(c["name"]) > 45 else c["name"]
        lines.append(
            f"| {c['platform']} | [{name}]({link}) | {c['prize']} | {days}d | {c['chain'][:6]} | {dl} |"
        )

    lines.extend([
        "",
        "## Sprint Priorities (May 2–17, 2026)",
        "1. **Solana Frontier** (May 11) — AgentEscrow — DMOB (registered)",
        "2. **Kite AI** (May 17) — AAE Hybrid Brain — DMOB + Creative",
        "3. **Reserve Governor** — Cantina — $30K, 8 days left",
        "4. **IGNITION** — Devpost — $5.12M, deadline TBD",
        "",
        "#bug-bounties #security #automation"
    ])

    new_content = "\n".join(lines) + "\n"
    BOUNTIES_FILE.write_text(new_content)
    log(f"Updated: {BOUNTIES_FILE}")

    # Telegram HQ notification
    try:
        top3 = qualifying[:3]
        summary = "\\n".join(f"• {c['name'][:40]} — {c['prize']} ({c['days_left']}d)" for c in top3)
        msg = f"🧭 **Opportunity Scan — {TODAY}**\\n\\n{summary}\\n\\nUpdated bounties file."
        subprocess.run([
            "hermes", "send", "message",
            "--target", "telegram:-1003872552815",
            "--message", msg
        ], timeout=15)
        log("Telegram HQ notified")
    except Exception as e:
        log(f"Telegram skip: {e}")

    log("=== Scan complete ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
