#!/usr/bin/env python3
"""GTA Arb Monitor — Cross-venue basis scanner (Hyperliquid perp vs Coinbase spot)."""

import os, sys
# Quiet hours: 11pm-6:30am ET = 3:00-10:30 UTC
from datetime import datetime, timezone
_hr = datetime.now(timezone.utc).hour
if 3 <= _hr < 10 or (_hr == 10 and datetime.now(timezone.utc).minute < 30):
    sys.exit(0)  # Quiet mode — no output
import json
import os
import sys
import subprocess
import time
from datetime import datetime, timezone
import urllib.request
import urllib.error

# Config
WATCHER_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(WATCHER_DIR, ".gta-arb-state.json")
ARB_THRESHOLD_BPS = 5  # 5 bps = 0.05% minimum spread to flag

# Assets to monitor (the A-list)
WATCHLIST = [
    "BTC", "ETH", "SOL", "AVAX", "LINK", "ONDO", "PAXG"
]

# CoinGecko ID mapping for spot prices (free, no API key)
CG_IDS = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
    "AVAX": "avalanche-2", "LINK": "chainlink", "ONDO": "ondo-finance"
}

# ── Hyperliquid Connector ────────────────────────────────────────────────────

def get_hl_prices() -> dict:
    """Fetch perpetual mid-prices from Hyperliquid via direct API (no SDK timeout issues)."""
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = json.dumps({"type": "allMids"})
        cmd = ["curl", "-s", url, "-X", "POST", "-H", "Content-Type: application/json", "-d", payload, "--max-time", "8"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return {}
        data = json.loads(result.stdout)
        return {asset: float(price) for asset, price in data.items()}
    except Exception as e:
        return {}

# ── Coinbase Spot Prices ────────────────────────────────────────────────────

def get_coinbase_prices() -> dict:
    """Fetch spot prices from Coinbase public API (free, no auth needed for prices)."""
    prices = {}
    for sym in WATCHLIST:
        pair = f"{sym}-USD"
        try:
            url = f"https://api.coinbase.com/v2/prices/{pair}/spot"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read())
                price = float(data["data"]["amount"])
                prices[sym] = price
        except Exception:
            # Fallback to CoinGecko for this asset
            try:
                cg_id = CG_IDS.get(sym)
                if cg_id:
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={cg_id}&vs_currencies=usd"
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=8) as resp:
                        data = json.loads(resp.read())
                        if cg_id in data:
                            prices[sym] = data[cg_id]["usd"]
            except:
                pass
    return prices

# ── Funding Rate ────────────────────────────────────────────────────────────

def get_hl_funding() -> dict:
    """Fetch current funding rates from Hyperliquid."""
    try:
        sys.path.insert(0, "/root/repos/hyperliquid-python-sdk")
        from hyperliquid.info import Info
        from hyperliquid.utils import constants
        info = Info(constants.MAINNET_API_URL)
        # Get all funding data
        funding_data = info.funding_history("BTC", 1)
        # This gives us the latest funding for BTC
        
        # For a broader view, get metadata which includes funding
        meta = info.meta()
        asset_ctx = info.all_mids()  # Used as a fallback
        
        # Try to get funding rates from the exchange info
        # The SDK exposes funding through exchange state
        exchange_state = info.exchange_state() if hasattr(info, 'exchange_state') else None
        
        rates = {}
        if exchange_state:
            for asset in exchange_state.get("assetStates", []):
                name = asset.get("name", "")
                if name in WATCHLIST or True:  # Get all we can
                    funding = asset.get("funding", None)
                    if funding:
                        rates[name] = float(funding)
        
        return rates, funding_data
    except Exception as e:
        return {}, []

def get_funding_rate() -> dict:
    """Fetch current funding rates from Hyperliquid via direct API.

    Real endpoint: `metaAndAssetCtxs` returns per-asset funding (prevFunding,
    fractional per-hour). Annualized APR% = funding * 24 * 365 * 100.
    Fixed 2026-09-14 — was a hardcoded 0 placeholder (no stale data).
    """
    rates = {}
    try:
        url = "https://api.hyperliquid.xyz/info"
        payload = json.dumps({"type": "metaAndAssetCtxs"})
        cmd = ["curl", "-s", url, "-X", "POST", "-H", "Content-Type: application/json",
               "-d", payload, "--max-time", "8"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # data = [meta, assetCtxs]; universe[0..n], ctxs[0..n] align 1:1
            meta, ctxs = data[0], data[1]
            universe = meta.get("universe", [])
            for i, asset in enumerate(universe):
                name = asset.get("name", "")
                if name not in WATCHLIST:
                    continue
                if i >= len(ctxs):
                    continue
                fund_frac = ctxs[i].get("funding")
                if fund_frac is None:
                    continue
                # funding is fractional per hour -> annualized APR %
                rates[name] = round(float(fund_frac) * 24 * 365 * 100, 2)
    except Exception:
        pass
    return rates

# ── Basis Calculation ──────────────────────────────────────────────────────

def calc_basis(perp_price: float, spot_price: float) -> dict:
    """Calculate basis between perp and spot in bps."""
    if not perp_price or not spot_price or spot_price == 0:
        return None
    
    basis_bps = ((perp_price - spot_price) / spot_price) * 10000  # Convert to bps
    basis_pct = basis_bps / 100  # Convert to %
    
    return {
        "perp": perp_price,
        "spot": spot_price,
        "basis_bps": round(basis_bps, 2),
        "basis_pct": round(basis_pct, 3),
        "type": "CONTANGO" if basis_bps > 0 else "BACKWARDATION"
    }

# ── Report ─────────────────────────────────────────────────────────────────

def generate_report(opportunities: list, all_basis: list, funding: dict):
    """Generate arb monitor report. Silent if nothing interesting."""
    now = datetime.now(timezone.utc)
    
    lines = []
    lines.append(f"🔁 ARBITRAGE SCAN — {now.strftime('%H:%M UTC')}")
    lines.append("")
    
    if opportunities:
        lines.append("⚡ ARB OPPORTUNITY DETECTED ⚡")
        lines.append("")
        for opp in opportunities:
            symbol = opp["symbol"]
            b = opp["basis"]
            lines.append(f"**{symbol}** — {b['type']} {b['basis_bps']:+.1f} bps")
            lines.append(f"  Perp: ${b['perp']:,.2f} | Spot: ${b['spot']:,.2f}")
            lines.append(f"  Trade: {'Short perp + Long spot' if b['type'] == 'CONTANGO' else 'Long perp + Short spot'}")
            if symbol in funding:
                lines.append(f"  Funding: {funding[symbol]:+.2f}% APR")
            lines.append("")
    
    if not opportunities:
        # Only print if there are notable spreads
        notable = [b for b in all_basis if b and abs(b["basis"]["basis_bps"]) > ARB_THRESHOLD_BPS]
        if notable:
            lines.append("📊 Notable spreads (above 5bps):")
            for item in notable:
                s = item["symbol"]
                b = item["basis"]
                lines.append(f"  {s}: {b['basis_bps']:+.1f} bps ({b['type']})")
            lines.append("")
        else:
            # Total silence when nothing to report
            return None
    
    # Summary (mobile-safe: one data point per line, no fixed-width columns)
    lines.append("━━━ FULL SCAN ━━━")
    for item in all_basis:
        if not item:
            continue
        s = item["symbol"]
        b = item["basis"]
        lines.append(f"{s} — perp ${b['perp']:,.2f} · spot ${b['spot']:,.2f} · "
                     f"{b['basis_bps']:+.1f} bps · {b['type']}")
    
    lines.append("")
    lines.append("🟢 Contango = perp above spot (short perp, buy spot)")
    lines.append("🔴 Backwardation = perp below spot (long perp, sell spot)")
    
    return "\n".join(lines)

def main():
    now = datetime.now(timezone.utc)
    
    # Fetch data
    hl_prices = get_hl_prices()
    cb_prices = get_coinbase_prices()
    funding = get_funding_rate()
    
    if not hl_prices or not cb_prices:
        print("🔁 ARBITRAGE SCAN — price feeds unavailable")
        return
    
    # Calculate basis for each asset
    all_basis = []
    opportunities = []
    
    for symbol in WATCHLIST:
        perp = hl_prices.get(symbol)
        spot = cb_prices.get(symbol)
        
        if not perp or not spot:
            continue
        
        basis = calc_basis(perp, spot)
        if not basis:
            continue
        
        item = {"symbol": symbol, "basis": basis}
        all_basis.append(item)
        
        if abs(basis["basis_bps"]) >= ARB_THRESHOLD_BPS:
            opportunities.append(item)
    
    # Save state
    state = {
        "last_scan": now.isoformat(),
        "opportunities": [
            {"symbol": o["symbol"], "basis_bps": o["basis"]["basis_bps"],
             "perp": o["basis"]["perp"], "spot": o["basis"]["spot"]}
            for o in opportunities
        ]
    }
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    
    # Generate and print report
    report = generate_report(opportunities, all_basis, funding)
    if report:
        print(report)

if __name__ == "__main__":
    main()
