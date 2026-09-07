#!/usr/bin/env python3
"""
Live LP Shape Detector — GenTech Original (v2, on-chain truth)

Reads the ACTUAL on-chain bin distribution of the Steward's LFJ V2.2 position
and classifies the shape (Curve / Bid-Ask / Spot / Asymmetric).

WHY v2: the v1 detector read a stale `defi-data.json` cache (price $6.42, old
bins) and classified a GHOST position. On-chain data is king — this reads the
live position via balanceOf(addr, bin) over the active-bin window, exactly like
discover_positions.py, and classifies the REAL distribution.

Usage:
  python3 lp-shape-detector-live.py                 # classify live position
  python3 lp-shape-detector-live.py --json           # machine-readable
  python3 lp-shape-detector-live.py --wallet <addr>  # any wallet
"""
import json, os, sys, math
from datetime import datetime, timezone

# ── Config ──────────────────────────────────────────────────────────────────
WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
POOL = "0x864d4e5ee7318e97483db7eb0912e09f161516ea"
RPC = "https://api.avax.network/ext/bc/C/rpc"
BIN_STEP = 10
LFJ_SHIFT = 2**23  # 8388608

def rpc_call(method, params):
    import urllib.request
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read())["result"]

def eth_call(to, data):
    try:
        return rpc_call("eth_call", [{"to": to, "data": data}, "latest"])
    except Exception:
        return None

def _bin_price(bin_id):
    return (1 + BIN_STEP / 10000) ** (bin_id - LFJ_SHIFT) * 10**12

def read_live_bins(wallet, pool, half_width=40):
    """Read the wallet's actual per-bin liquidity over a window around active."""
    active_raw = eth_call(pool, "0xdbe65edc")  # getActiveId()
    if not active_raw or active_raw == "0x":
        return {"error": "could not read active bin"}
    active = int(active_raw, 16)
    addr_hex = wallet.lower().replace("0x", "")
    bins = []
    for offset in range(-half_width, half_width + 1):
        bin_id = active + offset
        data = "0x00fdd58e" + addr_hex.zfill(64) + hex(bin_id)[2:].zfill(64)
        try:
            b = int(eth_call(pool, data) or "0x0", 16)
        except Exception:
            b = 0
        if b > 0:
            bins.append({"id": bin_id, "depth": b / 1e18, "price": _bin_price(bin_id)})
    return {"active": active, "bins": bins}

def analyze_bin_distribution(bins):
    if not bins or len(bins) < 3:
        return {"shape": "unknown", "confidence": 0, "reason": "insufficient bins"}
    depths = [b["depth"] for b in bins]
    total = sum(depths)
    if total == 0:
        return {"shape": "unknown", "confidence": 0, "reason": "no liquidity"}
    n = len(depths)
    center_idx = n // 2
    max_depth = max(depths)
    norm = [d / max_depth for d in depths]
    # Center concentration (middle 30%)
    cs, ce = int(n * 0.35), int(n * 0.65)
    center_pct = sum(depths[cs:ce]) / total * 100
    # Edge concentration (outer 25%)
    el, eh = int(n * 0.25), int(n * 0.75)
    edge_pct = (sum(depths[:el]) + sum(depths[eh:])) / total * 100
    # Peak position
    peak_idx = depths.index(max(depths))
    peak_pos = peak_idx / (n - 1)
    peak_from_center = abs(peak_pos - 0.5)
    # Symmetry
    left = sum(depths[:center_idx]); right = sum(depths[center_idx:])
    symmetry = 1 - abs(left - right) / total
    skew = (right - left) / total
    return {
        "n_bins": n, "total_depth": round(total, 6),
        "center_pct": round(center_pct, 1), "edge_pct": round(edge_pct, 1),
        "peak_position": round(peak_pos, 3), "peak_from_center": round(peak_from_center, 3),
        "symmetry": round(symmetry, 3), "skew": round(skew, 3),
        "norm_depths": norm,
    }

def classify_shape(m):
    if m.get("shape") == "unknown":
        return m
    scores = {"curve": 0, "bid-ask": 0, "spot": 0, "asymmetric": 0}
    reasons = []
    n = m["n_bins"]
    if n <= 3 or m["center_pct"] > 85:
        scores["spot"] = 90
        reasons.append(f"Spot: {n} bins, {m['center_pct']:.0f}% in center")
    if m["center_pct"] > 40:
        scores["curve"] += 30; reasons.append(f"Curve: {m['center_pct']:.0f}% center")
    if m["peak_from_center"] < 0.15:
        scores["curve"] += 25; reasons.append(f"Curve: peak near center")
    if m["symmetry"] > 0.7:
        scores["curve"] += 20; reasons.append(f"Curve: symmetric ({m['symmetry']:.0%})")
    if m["edge_pct"] < 30:
        scores["curve"] += 15; reasons.append(f"Curve: low edge ({m['edge_pct']:.0f}%)")
    if m["edge_pct"] > 45:
        scores["bid-ask"] += 35; reasons.append(f"Bid-Ask: {m['edge_pct']:.0f}% edge")
    if m["center_pct"] < 25:
        scores["bid-ask"] += 25; reasons.append(f"Bid-Ask: low center ({m['center_pct']:.0f}%)")
    if m["peak_from_center"] > 0.3:
        scores["bid-ask"] += 20; reasons.append(f"Bid-Ask: peak far from center")
    if m["symmetry"] > 0.6:
        scores["bid-ask"] += 10
    if abs(m["skew"]) > 0.25:
        scores["asymmetric"] += 40; scores["curve"] -= 20; scores["bid-ask"] -= 20
        reasons.append(f"Asymmetric: skew={m['skew']:.2f}")
    shape = max(scores, key=scores.get)
    conf = min(scores[shape], 95)
    if n < 10:
        conf = int(conf * 0.8); reasons.append(f"Warning: only {n} bins")
    return {"shape": shape, "confidence": conf, "scores": scores, "reasons": reasons, **m}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--wallet", default=WALLET)
    ap.add_argument("--pool", default=POOL)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    live = read_live_bins(args.wallet, args.pool)
    if "error" in live:
        print(f"❌ {live['error']}", file=sys.stderr); sys.exit(1)
    m = analyze_bin_distribution(live["bins"])
    result = classify_shape(m)
    result["activeBin"] = live["active"]
    if args.json:
        out = {k: v for k, v in result.items() if k != "norm_depths"}
        print(json.dumps(out, indent=2))
        return
    shape = result["shape"]
    emoji = {"curve": "📈", "bid-ask": "📊", "spot": "🎯", "asymmetric": "⚖️", "unknown": "❓"}.get(shape, "❓")
    name = {"curve": "Curve (center-weighted)", "bid-ask": "Bid-Ask (edge-weighted)",
            "spot": "Spot (single bin)", "asymmetric": "Asymmetric (skewed)", "unknown": "Unknown"}.get(shape)
    print(f"{emoji} **Live LP Shape** — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"   Active bin: {live['active']} | Bins: {result['n_bins']}")
    print(f"   Detected: {name} — {result['confidence']}% confidence")
    print(f"   Center {result['center_pct']}% | Edge {result['edge_pct']}% | Peak {result['peak_position']} | Sym {result['symmetry']}")
    for r in result.get("reasons", []):
        print(f"   • {r}")

if __name__ == "__main__":
    main()
