"""
Birdeye Token Radar — New token discovery with AI safety scoring.
Uses Birdeye Data Services API (x402 pay-per-request compatible).

Endpoints:
  - GET /defi/v3/token/new_listing  — new tokens on Solana
  - GET /defi/token_security        — safety signals per token
  - GET /defi/v3/token/overview     — price/volume/market data
"""

import os
import sys
import json
import time
import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
BIRDEYE_BASE = "https://public-api.birdeye.so"
API_KEY = os.getenv("BIRDEYE_API_KEY", "")
CHAIN = "solana"
POLL_INTERVAL = 60  # seconds between scans in watch mode
OUTPUT_DIR = Path(__file__).parent.parent / "output"
SEEN_FILE = OUTPUT_DIR / "seen_tokens.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("radar")


# --- Birdeye API Client ---
class BirdeyeClient:
    """Thin wrapper around Birdeye REST API."""

    def __init__(self, api_key: str, chain: str = "solana"):
        self.api_key = api_key
        self.chain = chain
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": api_key,
            "x-chain": chain,
            "accept": "application/json",
        })
        self.call_count = 0

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated GET request."""
        url = f"{BIRDEYE_BASE}{endpoint}"
        self.call_count += 1
        resp = self.session.get(url, params=params, timeout=15)

        if resp.status_code == 402:
            log.warning("402 Payment Required — x402 flow triggered (call #%d)", self.call_count)
            # In x402 mode, the client SDK handles payment automatically.
            # For this demo, we use API key auth. x402 integration noted for v2.
            return {"error": "payment_required", "status": 402}

        resp.raise_for_status()
        return resp.json()

    def get_new_listings(self, limit: int = 20, time_from: int = None) -> list:
        """Fetch newly listed tokens on Solana."""
        params = {"limit": limit, "meme_platform_enabled": "true"}
        if time_from:
            params["time_from"] = time_from

        data = self._get("/defi/v3/token/new_listing", params)
        if "error" in data:
            return []

        items = data.get("data", {}).get("items", [])
        log.info("Fetched %d new listings", len(items))
        return items

    def get_token_security(self, address: str) -> dict:
        """Fetch safety signals for a token."""
        params = {"address": address}
        data = self._get("/defi/token_security", params)
        if "error" in data:
            return {}
        return data.get("data", {})

    def get_token_overview(self, address: str) -> dict:
        """Fetch price, volume, market cap for a token."""
        params = {"address": address}
        data = self._get("/defi/v3/token/overview", params)
        if "error" in data:
            return {}
        return data.get("data", {})


# --- Safety Scorer ---
class SafetyScorer:
    """
    Score a token 0-100 based on on-chain safety signals.

    Factors (total = 100 pts):
      - Mint authority revoked:    25 pts
      - Freeze authority revoked:  15 pts
      - LP locked or burned:       25 pts
      - Top 10 holder % < 50%:     20 pts
      - Age > 1 hour:              15 pts
    """

    WEIGHTS = {
        "mint_revoked": 25,
        "freeze_revoked": 15,
        "lp_locked": 25,
        "holder_distribution": 20,
        "age_bonus": 15,
    }

    @staticmethod
    def score(security: dict, listing_time: int = None) -> dict:
        """
        Returns dict with:
          - total: int (0-100)
          - grade: str (🟢/🟡/🔴)
          - flags: list[str] — warning flags
          - breakdown: dict — per-factor scores
        """
        score = 0
        flags = []
        breakdown = {}

        if not security:
            return {
                "total": 0,
                "grade": "🔴",
                "flags": ["No security data available"],
                "breakdown": {},
            }

        # 1. Mint authority
        mint_revoked = security.get("mintAuthority") is None or security.get("mintAuthority") == "null"
        if mint_revoked:
            score += 25
            breakdown["mint_revoked"] = 25
        else:
            flags.append("⚠️ Mint authority ACTIVE — can mint unlimited tokens")
            breakdown["mint_revoked"] = 0

        # 2. Freeze authority
        freeze_revoked = security.get("freezeAuthority") is None or security.get("freezeAuthority") == "null"
        if freeze_revoked:
            score += 15
            breakdown["freeze_revoked"] = 15
        else:
            flags.append("⚠️ Freeze authority ACTIVE — can freeze accounts")
            breakdown["freeze_revoked"] = 0

        # 3. LP status
        lp_locked = security.get("isLpTokenBurned", False) or security.get("lpLocked", False)
        if lp_locked:
            score += 25
            breakdown["lp_locked"] = 25
        else:
            flags.append("⚠️ LP NOT locked/burned — rug pull risk")
            breakdown["lp_locked"] = 0

        # 4. Holder distribution (top 10 < 50% is healthy)
        top10_pct = security.get("top10HolderPercent", 100)
        if isinstance(top10_pct, str):
            try:
                top10_pct = float(top10_pct)
            except ValueError:
                top10_pct = 100

        if top10_pct < 50:
            score += 20
            breakdown["holder_distribution"] = 20
        elif top10_pct < 70:
            score += 10
            breakdown["holder_distribution"] = 10
            flags.append(f"⚡ Top 10 holders own {top10_pct:.1f}% — moderate concentration")
        else:
            breakdown["holder_distribution"] = 0
            flags.append(f"🔴 Top 10 holders own {top10_pct:.1f}% — high concentration")

        # 5. Age bonus
        if listing_time:
            age_hours = (int(time.time()) - listing_time) / 3600
            if age_hours > 1:
                score += 15
                breakdown["age_bonus"] = 15
            elif age_hours > 0.25:  # 15 min
                score += 5
                breakdown["age_bonus"] = 5
                flags.append("⚡ Very new token (< 1 hour)")
            else:
                breakdown["age_bonus"] = 0
                flags.append("🔴 Brand new token (< 15 min) — extreme risk")
        else:
            breakdown["age_bonus"] = 0

        # Grade
        if score >= 80:
            grade = "🟢"
        elif score >= 50:
            grade = "🟡"
        else:
            grade = "🔴"

        return {
            "total": score,
            "grade": grade,
            "flags": flags,
            "breakdown": breakdown,
        }


# --- Telegram Alert Formatter ---
def format_alert(token: dict, security: dict, score: dict, overview: dict = None) -> str:
    """Format a token alert for Telegram (Markdown)."""
    name = token.get("name", "Unknown")
    symbol = token.get("symbol", "???")
    address = token.get("address", "")
    chain = token.get("chain", "solana")

    # Short address for display
    short_addr = f"{address[:6]}...{address[-4:]}" if len(address) > 10 else address

    lines = [
        f"{score['grade']} **{name}** (${symbol})",
        f"🛡️ Safety Score: **{score['total']}/100**",
        f"📍 `{short_addr}`",
    ]

    # Market data if available
    if overview:
        price = overview.get("priceUsd") or overview.get("value")
        mcap = overview.get("mc")
        liquidity = overview.get("liquidity")
        if price:
            lines.append(f"💰 Price: ${price:,.8f}" if price < 0.01 else f"💰 Price: ${price:,.4f}")
        if mcap:
            lines.append(f"📊 MCap: ${mcap:,.0f}")
        if liquidity:
            lines.append(f"💧 Liquidity: ${liquidity:,.0f}")

    # Flags
    if score["flags"]:
        lines.append("")
        for flag in score["flags"]:
            lines.append(flag)

    # Links
    lines.append("")
    lines.append(f"[Birdeye](https://birdeye.so/token/{address}?chain={chain})")
    lines.append(f"[Solscan](https://solscan.io/account/{address})")

    # Timestamp
    lines.append(f"\n⏰ {datetime.now(timezone.utc).strftime('%H:%M:%S UTC')}")

    return "\n".join(lines)


# --- Telegram Sender ---
def send_telegram(message: str, chat_id: str = None, bot_token: str = None) -> bool:
    """Send alert to Telegram. Returns True on success."""
    bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = chat_id or os.getenv("TELEGRAM_ALERT_CHAT_ID", "")

    if not bot_token or not chat_id:
        log.warning("Telegram not configured (missing bot token or chat ID)")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(url, json=payload, timeout=10)
        if resp.ok:
            log.info("Telegram alert sent ✓")
            return True
        else:
            log.error("Telegram error: %s", resp.text)
            return False
    except Exception as e:
        log.error("Telegram send failed: %s", e)
        return False


# --- State Management ---
def load_seen() -> set:
    """Load previously seen token addresses."""
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set):
    """Save seen token addresses."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SEEN_FILE.write_text(json.dumps(list(seen)[-500:]))  # keep last 500


# --- Main Scan Loop ---
def scan_once(client: BirdeyeClient, seen: set, telegram: bool = True) -> int:
    """
    Single scan cycle. Returns number of new tokens found.
    """
    listings = client.get_new_listings(limit=20)
    new_count = 0

    for token in listings:
        address = token.get("address", "")
        if not address or address in seen:
            continue

        seen.add(address)
        new_count += 1

        log.info("New token: %s ($%s) — %s",
                 token.get("name", "?"),
                 token.get("symbol", "?"),
                 address[:12] + "...")

        # Fetch security data
        security = client.get_token_security(address)
        time.sleep(0.5)  # rate limit buffer

        # Fetch overview (price/mcap)
        overview = client.get_token_overview(address)
        time.sleep(0.5)

        # Score it
        listing_time = token.get("liquidityAddedAt") or token.get("createdAt")
        score = SafetyScorer.score(security, listing_time)

        # Format and send
        alert = format_alert(token, security, score, overview)
        log.info("Score: %d/100 %s — %s",
                 score["total"], score["grade"],
                 token.get("name", "?"))

        if telegram:
            send_telegram(alert)

        # Also save to local file
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        log_file = OUTPUT_DIR / f"alerts_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "token": token,
                "security": security,
                "score": score,
                "overview": overview,
            }) + "\n")

    return new_count


def main():
    parser = argparse.ArgumentParser(description="Birdeye Token Radar")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring mode")
    parser.add_argument("--interval", type=int, default=POLL_INTERVAL, help="Seconds between scans")
    parser.add_argument("--no-telegram", action="store_true", help="Skip Telegram alerts")
    parser.add_argument("--limit", type=int, default=20, help="Tokens per scan")
    args = parser.parse_args()

    if not API_KEY:
        log.error("BIRDEYE_API_KEY not set. Get one at https://bds.birdeye.so")
        sys.exit(1)

    client = BirdeyeClient(API_KEY)
    seen = load_seen()
    use_telegram = not args.no_telegram

    log.info("🛰️ Birdeye Token Radar starting (chain=%s, interval=%ds)", CHAIN, args.interval)
    log.info("API calls will count toward Birdeye usage (min 50 for BIP competition)")

    try:
        while True:
            new = scan_once(client, seen, telegram=use_telegram)
            save_seen(seen)

            log.info("Scan complete. %d new tokens. Total API calls: %d", new, client.call_count)

            if not args.watch:
                break

            time.sleep(args.interval)

    except KeyboardInterrupt:
        log.info("Shutting down. Total API calls: %d", client.call_count)
        save_seen(seen)


if __name__ == "__main__":
    main()
