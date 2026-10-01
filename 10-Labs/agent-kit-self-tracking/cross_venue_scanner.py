#!/usr/bin/env python3
"""Cross-Venue Price-Gap Scanner — Phase 0 signal source.

Scans DEX spot (LFJ, Blackhole, Meteora, Orca, Raydium) vs CEX spot/perp
(Hyperliquid, OKX, Coinbase) for the same asset and logs any price gap above
a threshold to the arb log. This is the "true arbitrage across rails" signal
layer Jordan asked for (Sep 10).

Read-only + keyless (free public APIs). No orders — detection only.

Venue price sources:
  - Hyperliquid perp  : api.hyperliquid.xyz/info (allMids)
  - Coinbase spot     : api.coinbase.com/v2/prices/{SYM}-USD/spot
  - OKX spot          : www.okx.com/api/v5/market/ticker?instId={SYM}-USDT
  - DEX spot (LFJ/Blackhole/Meteora/Orca/Raydium): DexScreener pair search
    (free, no key) — resolves the best-liquidity pair per venue+asset.

Usage:
  python3 cross_venue_scanner.py            # scan + log gaps
  python3 cross_venue_scanner.py --dry      # scan + print, no log write
"""
from __future__ import annotations

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arb_log import log_signal, LOG_ROOT  # noqa: E402

# ── Tunables ─────────────────────────────────────────────────────────────
GAP_THRESHOLD_BPS = 10.0   # log a signal when |gap| >= 10 bps
# Asset -> DexScreener search term (best-liquidity pair per venue)
WATCHLIST = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "AVAX": "avalanche",
    "LINK": "chainlink",
    "ONDO": "ondo",
}
# DEX venues we want to resolve via DexScreener (chain -> venue label)
DEX_CHAINS = {
    "solana": ["Meteora", "Orca", "Raydium"],
    "avalanche": ["LFJ", "Blackhole"],
}
# CEX spot/perp venues (direct API)
CEX_VENUES = ["Hyperliquid", "OKX", "Coinbase"]

# ── Canonical token identity (fail-closed) ─────────────────────────────────
# The base-symbol check below is NOT an identity check. DexScreener's keyword
# search happily returns IMPOSTOR tokens that share a symbol and report billions
# in fake "liquidity.usd" off a ~$6k stablecoin reserve. Measured 2026-09-14:
# the scanner picked a frozen fake SOL/USDC "Raydium" pair at $103.75 (real
# Raydium SOL was $102.6-102.8) and logged 35 fabricated cross-venue "gaps" in
# one day — gaps that existed on no real venue. The old 1% consensus filter did
# not catch it: the fake sat ~0.95% off consensus, just inside the band.
# Two independent gates now, both fail-closed:
#   1. ADDRESS allowlist   — base token must be a canonical address for that chain.
#   2. RESERVE consistency — reported liquidity.usd must be ~2x the ACTUAL
#      stablecoin reserve, and that reserve must be real money.
# Gate fails, or asset/chain not in the allowlist => pair dropped => no price
# => no signal. Better to report nothing than to log a gap that cannot be traded.
CANONICAL_TOKENS = {
    ("solana", "SOL"):  {"So11111111111111111111111111111111111111112"},
    ("solana", "BTC"):  {"3NZ9JMVBmGAqocybic2c7LQCJScmgsAZ6vQqTDzcqmJh"},
    ("solana", "ETH"):  {"7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs"},
    ("solana", "LINK"): {"LinkhB3afbBKb2EQQu7s7umdZceV3wcvAUJhQAfQ23L"},
    ("avalanche", "AVAX"): {"0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7"},
    ("avalanche", "LINK"): {"0x5947bb275c521040051d82396192181b413227a3"},
}
MIN_QUOTE_RESERVE_USD = 25000.0     # real stablecoin reserve floor
LIQ_USD_RATIO_BAND = (0.5, 2.5)     # liquidity.usd must be ~2x the quote reserve

DEXSCREENER_SEARCH = "https://api.dexscreener.com/latest/dex/search"
HL_INFO = "https://api.hyperliquid.xyz/info"
OKX_TICKER = "https://www.okx.com/api/v5/market/ticker"
CB_PRICE = "https://api.coinbase.com/v2/prices/{sym}-USD/spot"


def fetch_json(url: str, timeout: int = 12) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (cross-venue-scanner)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[xvenue] fetch failed {url}: {e}\n")
        return None


def hl_perp_prices() -> dict:
    """Hyperliquid perp mid-prices for the watchlist (POST allMids)."""
    try:
        payload = json.dumps({"type": "allMids"}).encode()
        req = urllib.request.Request(HL_INFO, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            mids = json.loads(resp.read().decode())
        return {a: float(mids[a]) for a in WATCHLIST if a in mids}
    except Exception as e:
        sys.stderr.write(f"[xvenue] HL fetch failed: {e}\n")
        return {}


def okx_spot_prices() -> dict:
    """OKX spot USDT prices for the watchlist."""
    out = {}
    for sym in WATCHLIST:
        d = fetch_json(f"{OKX_TICKER}?instId={sym}-USDT", timeout=8)
        if d and d.get("data"):
            out[sym] = float(d["data"][0]["last"])
    return out


def coinbase_spot_prices() -> dict:
    """Coinbase spot USD prices for the watchlist."""
    out = {}
    for sym in WATCHLIST:
        d = fetch_json(CB_PRICE.format(sym=sym), timeout=8)
        if d and d.get("data"):
            out[sym] = float(d["data"]["amount"])
    return out


def dexscreener_prices() -> dict:
    """Resolve DEX spot prices per venue — by CANONICAL ADDRESS, not keyword.

    Returns {venue: {asset: price}}.

    WHY ADDRESS RESOLUTION (found live 2026-09-14): this function used to find
    pairs via DexScreener keyword SEARCH. Measured today, keyword search does
    NOT surface the canonical token for ANY of our six assets — it returns
    look-alike impostor tokens that copy the symbol and spoof "liquidity.usd"
    off a ~$6k stablecoin reserve. The old code ranked by that spoofable
    liquidity figure, so it picked the impostor every time and logged 35
    fabricated cross-venue "gaps" in a single day (a frozen fake Raydium
    SOL/USDC at $103.75 vs a real $102.6-102.8, logged as a 12-90 bps edge
    that existed on no real venue). The 1% consensus filter did not catch it —
    the fake sat ~0.95% off consensus, just inside the band.

    Now: resolve each (chain, asset) by its canonical base-token ADDRESS via
    the /tokens endpoint, then apply fail-closed gates:
      * canonical address must match (identity, not symbol)
      * chain must be one of our rails, venue must map to LFJ/Blackhole/
        Meteora/Orca/Raydium
      * quote must be a stablecoin with a real reserve (>= MIN_QUOTE_RESERVE_USD)
      * reported liquidity.usd must be ~2x that reserve (spoof detector)
    Rank by REAL reserve. Anything failing a gate is dropped — no price, no
    signal. Reporting nothing beats logging a gap that cannot be traded.
    """
    out = {v: {} for v in set(sum(DEX_CHAINS.values(), []))}
    for (chain, asset), addresses in CANONICAL_TOKENS.items():
        for addr in sorted(addresses):
            d = fetch_json(f"https://api.dexscreener.com/latest/dex/tokens/{addr}",
                           timeout=15)
            if not d or not d.get("pairs"):
                continue
            for pair in d["pairs"]:
                if (pair.get("chainId") or "").lower() != chain:
                    continue
                # Gate 1 — identity: canonical base address for this chain.
                base_addr = ((pair.get("baseToken") or {}).get("address") or "").lower()
                if base_addr != addr.lower():
                    continue
                quote = ((pair.get("quoteToken") or {}).get("symbol") or "").upper()
                if quote not in ("USDC", "USDT", "USD"):
                    continue
                venue = _map_dex_to_venue((pair.get("dexId") or "").lower(),
                                          DEX_CHAINS.get(chain, []))
                if not venue:
                    continue
                # Gate 2 — reserve consistency (spoof detector).
                liq = pair.get("liquidity") or {}
                usd = float(liq.get("usd") or 0)
                qres = float(liq.get("quote") or 0)
                price = float(pair.get("priceUsd") or 0)
                if not price or usd <= 0 or qres <= 0:
                    continue
                if qres < MIN_QUOTE_RESERVE_USD:
                    continue
                ratio = usd / (2.0 * qres)
                if not (LIQ_USD_RATIO_BAND[0] <= ratio <= LIQ_USD_RATIO_BAND[1]):
                    continue
                # Rank by REAL reserve, never by the spoofable reported usd.
                cur = out[venue].get(asset)
                if cur is None or qres > cur[1]:
                    out[venue][asset] = (price, qres)
    return {v: {a: p[0] for a, p in prices.items()}
            for v, prices in out.items()}


def _map_dex_to_venue(dex: str, venues: list) -> str | None:
    """Map a DexScreener dexId to our venue label."""
    mapping = {
        "traderjoe": "LFJ", "trader-joe": "LFJ", "joe": "LFJ",
        "blackhole": "Blackhole", "blackhole-cl": "Blackhole",
        "meteora": "Meteora", "meteora-dlmm": "Meteora",
        "orca": "Orca", "orca-v2": "Orca",
        "raydium": "Raydium", "raydium-cl": "Raydium",
    }
    return mapping.get(dex)


def _recent_signals(strategy: str, window_s: int = 3600) -> set:
    """Set of (strategy, signal) tuples logged in the last window_s seconds.
    Used to avoid re-logging the same signal on every cron tick."""
    import glob
    seen = set()
    cutoff = datetime.now(timezone.utc).timestamp() - window_s
    for path in glob.glob(os.path.join(LOG_ROOT, "*.jsonl")):
        try:
            with open(path) as f:
                for line in f:
                    if not line.strip():
                        continue
                    row = json.loads(line)
                    if row.get("strategy") != strategy:
                        continue
                    try:
                        ts = datetime.fromisoformat(row["ts"]).timestamp()
                    except Exception:
                        continue
                    if ts >= cutoff:
                        seen.add((strategy, row.get("signal")))
        except (OSError, json.JSONDecodeError):
            continue
    return seen


def main() -> int:
    dry = "--dry" in sys.argv
    now = datetime.now(timezone.utc)

    # Gather all venue prices
    hl = hl_perp_prices()
    okx = okx_spot_prices()
    cb = coinbase_spot_prices()
    dex = dexscreener_prices()

    # Build a price map: venue -> {asset: price}
    price_map = {"Hyperliquid": hl, "OKX": okx, "Coinbase": cb}
    price_map.update(dex)

    # ── Sanity filter (honesty guardrail) ────────────────────────────────
    # DexScreener keyword search can resolve a WRONG token with the same
    # symbol (e.g. a fake "ONDO" at $1.44 vs the real ~$0.35). Real
    # cross-venue arb gaps are small (< a few %). So we compute a CEX
    # consensus median per asset and DROP any venue price that deviates
    # more than SANITY_BAND from it — those are wrong pairs, not arb
    # opportunities. Never log a fabricated-looking gap.
    SANITY_BAND = 0.01  # 1% — real cross-venue gaps are bps, not %; anything
    # deviating >1% from CEX consensus is a wrong pair, not an arb edge
    cex_assets = set(hl) | set(okx) | set(cb)
    consensus = {}
    for asset in cex_assets:
        vals = [p for p in (hl.get(asset), okx.get(asset), cb.get(asset))
                if p]
        if vals:
            vals.sort()
            consensus[asset] = vals[len(vals) // 2]  # median
    # Drop implausible DEX prices (wrong pairs) from the map
    for venue, prices in list(price_map.items()):
        for asset in list(prices):
            med = consensus.get(asset)
            if med and abs(prices[asset] - med) / med > SANITY_BAND:
                del price_map[venue][asset]

    # Compare every venue pair for the same asset; log gaps above threshold.
    venues = [v for v in price_map if price_map[v]]
    seen = _recent_signals("cross-venue")
    signals = 0
    for asset in WATCHLIST:
        for i, v1 in enumerate(venues):
            p1 = price_map[v1].get(asset)
            if p1 is None:
                continue
            for v2 in venues[i + 1:]:
                p2 = price_map[v2].get(asset)
                if p2 is None or p2 == 0:
                    continue
                gap_bps = ((p1 - p2) / p2) * 10000
                if abs(gap_bps) < GAP_THRESHOLD_BPS:
                    continue
                direction = "premium" if gap_bps > 0 else "discount"
                signal = (f"{asset} {v1} {direction} {abs(gap_bps):.1f}bps "
                          f"vs {v2} (${p1:.4f} vs ${p2:.4f})")
                if ("cross-venue", signal) in seen:
                    continue  # already logged recently — don't duplicate
                if dry:
                    print(f"[DRY] {signal}")
                else:
                    path = log_signal(
                        strategy="cross-venue",
                        signal=signal,
                        taken=False,
                        not_taken_reason="threshold",
                        venues=[v1, v2],
                        realized_pnl=None,
                        meta={"asset": asset, "gap_bps": round(gap_bps, 2),
                              "price_a": p1, "price_b": p2},
                    )
                    if path:
                        signals += 1
                        print(f"[LOG] {signal} -> {path}")

    if dry:
        print(f"[DRY] {signals} gap(s) above {GAP_THRESHOLD_BPS}bps (not logged)")
    else:
        print(f"[xvenue] {now.isoformat()} — {signals} gap(s) logged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
