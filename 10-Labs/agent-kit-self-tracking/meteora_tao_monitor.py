#!/usr/bin/env python3
"""Meteora TAO rail monitor — READ-ONLY (Sep 12 2026).

Step 3 of the Meteora safe path. Zero capital, zero writes: it watches the TAO
pools and tells us when this rail is worth acting on.

Why it exists:
  - The DexScreener numbers for these pools were junk (billions of TVL, ~0
    volume). Meteora's own Data API is the authoritative source, so we read THAT.
  - The venue's `apy` field annualises a short window and printed 36,738% on a
    $4k pool. Annualising one day of fees is the fantasy-APR trap, so this tool
    computes its own fee-based APR and reports the venue number only for contrast.
  - The Solana wallet is empty; the rail is capability-complete and capital-gated.
    This monitor watches for the moment that changes.

Silence doctrine: silent unless something CHANGED (pool set, TVL/volume shift,
TAO price move, or the wallet getting funded).

API contract (from the official Meteora skill, references/data-and-apis.md):
  base  https://dlmm.datapi.meteora.ag   (30 RPS)
  sort key is flat (`volume_24h`) but the VALUE is nested (`.volume["24h"]`)
  wallet portfolio uses `?user=<wallet>`
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

API = "https://dlmm.datapi.meteora.ag"
PRICE_API = "https://lite-api.jup.ag/price/v3?ids="
TAO_MINT = "taoC6xyv2v8tDLcev4uaGUgV4vdQsWJrGft2kcBRrBY"
SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
WALLET = "BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP"
RPC = "https://api.mainnet-beta.solana.com"

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     ".meteora-tao-state.json")

MIN_TVL = 500.0        # ignore dust pools
QUIET = "--quiet" in sys.argv
FORCE = "--force" in sys.argv


def get(url, timeout=30):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1,
                       "method": method, "params": params}).encode()
    req = urllib.request.Request(
        RPC, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def tao_pools():
    """TAO pools on Meteora DLMM, sorted by TVL."""
    d = get(f"{API}/pools?query=TAO&page_size=100")
    rows = d.get("data") if isinstance(d, dict) else d
    out = []
    for p in rows or []:
        if not isinstance(p, dict):
            continue
        if TAO_MINT not in json.dumps(p):
            continue
        tvl = p.get("tvl") or 0
        if tvl < MIN_TVL:
            continue
        fees = p.get("fees") or {}
        vol = p.get("volume") or {}
        f24 = float(fees.get("24h") or 0)
        v24 = float(vol.get("24h") or 0)
        cfg = p.get("pool_config") or {}
        out.append({
            "name": p.get("name"),
            "address": p.get("address"),
            "tvl": round(float(tvl), 2),
            "vol24": round(v24, 2),
            "fees24": round(f24, 2),
            "bin_step": cfg.get("bin_step"),
            "base_fee": cfg.get("base_fee_pct"),
            "has_farm": bool(p.get("has_farm")),
            "price": p.get("current_price"),
            # OUR honest measure: only 24h of fee data, so this is a SNAPSHOT
            # annualisation, not a forecast. Labelled as such on output.
            "fee_apr_snapshot": round(f24 / tvl * 365 * 100, 1) if tvl else 0.0,
            "venue_apr": p.get("apr"),
        })
    out.sort(key=lambda x: -x["tvl"])
    return out


def tao_price():
    try:
        d = get(PRICE_API + TAO_MINT)
        for k, v in (d or {}).items():
            if k.lower() == TAO_MINT.lower():
                return float(v.get("usdPrice") or 0)
    except Exception:
        pass
    return 0.0


def wallet_funding():
    """SOL / USDC / TAO in our Solana wallet — the actual gate."""
    res = {"sol": 0.0, "usdc": 0.0, "tao": 0.0}
    try:
        res["sol"] = rpc("getBalance", [WALLET])["result"]["value"] / 1e9
    except Exception:
        res["sol"] = -1
    for key, mint in (("usdc", USDC_MINT), ("tao", TAO_MINT)):
        try:
            r = rpc("getTokenAccountsByOwner",
                    [WALLET, {"mint": mint}, {"encoding": "jsonParsed"}])
            tot = 0.0
            for a in r["result"]["value"]:
                tot += float(a["account"]["data"]["parsed"]["info"]
                             ["tokenAmount"]["uiAmount"] or 0)
            res[key] = tot
        except Exception:
            res[key] = -1
    return res


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(s):
    try:
        with open(STATE, "w") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass


def main():
    pools = tao_pools()
    px = tao_price()
    fund = wallet_funding()

    snap = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "price": round(px, 2),
        "pools": {p["address"]: p["tvl"] for p in pools},
        "funded": round(fund["sol"], 4),
    }
    prev = load_state()

    # ── what CHANGED? (silence doctrine) ────────────────────────────────
    changes = []
    if not prev:
        changes.append("first run — baseline")
    else:
        new_pools = set(snap["pools"]) - set(prev.get("pools", {}))
        gone = set(prev.get("pools", {})) - set(snap["pools"])
        if new_pools:
            changes.append(f"{len(new_pools)} new pool(s) above ${MIN_TVL:,.0f} TVL")
        if gone:
            changes.append(f"{len(gone)} pool(s) dropped out")
        pp = prev.get("price") or 0
        if pp and abs(px - pp) / pp >= 0.05:
            changes.append(f"TAO moved {((px-pp)/pp)*100:+.1f}% to ${px:,.2f}")
        if prev.get("funded", 0) <= 0 < fund["sol"]:
            changes.append("🎉 SOLANA WALLET FUNDED — rail can go live")
        for addr, tvl in snap["pools"].items():
            old = prev.get("pools", {}).get(addr, 0)
            if old and abs(tvl - old) / old >= 0.25:
                changes.append(f"TVL moved {((tvl-old)/old)*100:+.0f}% on a pool")

    save_state(snap)

    if QUIET and not changes and not FORCE:
        return 0
    if not changes and not FORCE:
        return 0

    # ── report ───────────────────────────────────────────────────────────
    print("🌊 METEORA TAO RAIL — monitor (read-only)")
    if changes:
        print("CHANGE: " + "; ".join(changes))
    print(f"\nTAO ${px:,.2f}   |   {len(pools)} pools above ${MIN_TVL:,.0f} TVL\n")
    for p in pools[:6]:
        farm = "farm" if p["has_farm"] else "fees-only"
        print(f"  {p['name']:<12} bin={p['bin_step']} fee={p['base_fee']}% {farm}")
        print(f"    TVL ${p['tvl']:>10,.0f}  vol24 ${p['vol24']:>10,.0f}  "
              f"fees24 ${p['fees24']:>8,.2f}")
        print(f"    fee-APR snapshot {p['fee_apr_snapshot']:>8,.1f}%  "
              f"(venue says {p['venue_apr']})")
    print("\n  ⚠️  APRs are a ONE-DAY snapshot annualised — a smell test, not a")
    print("     forecast. Sustained volume is what pays.")
    print(f"\nWallet {WALLET}")
    print(f"  SOL {fund['sol']:.6f} | USDC {fund['usdc']:.2f} | TAO {fund['tao']:.6f}")
    if fund["sol"] <= 0:
        print("  🚧 EMPTY — the rail is capital-gated. This is the only blocker.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
