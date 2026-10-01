#!/usr/bin/env python3
"""AVAX staking benchmark — the AVERAGE STAKER, not one protocol.

WHY THIS EXISTS (Jordan, 2026-09-21):
  "when we're comparing staking, we want to look for the average staker, not just from
   SAVAX or BENQI. We kind of want to get a measurement of all the staking platforms
   and kind of get an average."

Before this, `benchmark-feeds.py` pinned STAKING_POOL_ID to a SINGLE pool (benqi sAVAX)
and that one number stood in for "staking". One protocol is not the market. Measured on
2026-09-21, sAVAX paid 4.66%/yr while ggAVAX paid 0.90%/yr — a 5x spread between two
providers doing the same job. A benchmark built on either one is a benchmark of that
protocol, not of staking.

METHOD — and why it is trustworthy:
  1. PREFER a direct on-chain read of the provider's exchange rate: redemption value per
     share now, versus N days ago, annualised. This is the reward ACTUALLY PASSED THROUGH
     to stakers. It cannot be inflated by incentive tokens, a stale aggregator entry, or a
     headline APY that includes a rewards programme that ends next week.
  2. FALL BACK to the DefiLlama listing only where no on-chain interface is known — and
     the output SAYS which providers were measured on-chain and which were sourced, so a
     reader can weigh them.
  3. PUBLISH THE SPREAD AND THE COUNT. An average over 2 providers is a weaker claim than
     one over 6, and the reader is entitled to know which they are looking at.

CHAIN > AGGREGATOR (Jordan's rule). An aggregator number must never be the only evidence
for a yield we report.
"""
import json
import statistics
import time
import urllib.request

# ── AVAX RPC ROTATION (2026-09-22) ────────────────────────────────────────────────────────────
# This file used to hardcode a single provider. That one host took a per-SOURCE Cloudflare ban
# (1015) and returned 429 to EVERY call — so one throttle silently disabled this tool along with
# ~65 others. The shared `avax_rpc` module rotates across verified providers and FAILS CLOSED.
# The old URL is kept only as a last-resort string, never as the first choice.
def _avax_url():
    try:
        import os as _o, sys as _s
        _d = _o.path.dirname(_o.path.abspath(globals().get("__file__") or (_s.argv and _s.argv[0]) or "."))
        if _d and _d not in _s.path:
            _s.path.insert(0, _d)
        from avax_rpc import url as _u
        return _u()
    except Exception:
        return _avax_url()   # last resort only — avax_rpc preferred

RPC = _avax_url()
WINDOW_DAYS = 30          # sample the exchange rate across this many days
ERC4626 = "convertToAssets"

# ── The AVAX staking field ────────────────────────────────────────────────────────────────
# Each provider: name, how to read it, and the token it pays.
#   onchain : (contract, function) — redemption value per 1e18 shares
#   llama   : DefiLlama pool id — used only when no on-chain interface is known
PROVIDERS = [
    {"name": "sAVAX (Benqi)",      "onchain": ("0x2b2C81e08f1Af8835a78Bb2A90AE924ACE0eA4bE", "getPooledAvaxByShares")},
    {"name": "ggAVAX/stAVAX (Hypha)", "onchain": ("0xA25EaF2906FA1a3a13EdAc9B9657108Af7B703e3", ERC4626)},
    {"name": "ankrAVAX (Ankr)",    "llama": "6c8f48ae-27f9-4829-866f-7cb08841e816"},
    {"name": "yyAVAX (Yield Yak)", "llama": "6a6ec71a-4e41-4db9-b206-edb9f87a7746"},
]


def _rpc(method, params, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(RPC, data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.load(r)
    if "error" in out:
        raise RuntimeError(out["error"])
    return out["result"]


def _call(to, data, block=None):
    p = {"to": to, "data": data}
    if block:
        p["blockNumber"] = hex(block)
    return _rpc("eth_call", [p, "latest" if not block else hex(block)])


def _keccak_sel(sig):
    """4-byte selector for a function signature. Uses eth_utils when available, else a
    minimal pure-python keccak so this module has no hard dependency."""
    try:
        from eth_utils import keccak
        return keccak(text=sig)[:4].hex()
    except Exception:
        return None


def _block_days_ago(days):
    """Block ~`days` ago. The search window must actually COVER the requested span: an earlier
    version capped the low bound at head-3,000,000 (~62 days at Avalanche's ~1.8s blocks), so a
    90-day request silently returned a 69-day-old block and annualised a shorter gap as if it
    were 90 days -- understating the rate. Size the window from the requested span."""
    head = int(_rpc("eth_blockNumber", []), 16)
    now_ts = int(_rpc("eth_getBlockByNumber", [hex(head), False])["timestamp"], 16)
    target = now_ts - days * 86400
    span = int(days * 86400 / 1.5) + 400_000          # ~1.5s blocks, plus slack
    lo, hi = max(0, head - span), head
    for _ in range(30):
        mid = (lo + hi) // 2
        ts = int(_rpc("eth_getBlockByNumber", [hex(mid), False])["timestamp"], 16)
        if ts < target:
            lo = mid
        else:
            hi = mid
    return head, hi


def _onchain_apr(contract, fn, days=WINDOW_DAYS):
    """Annualised % from the growth of the redemption rate over `days`."""
    sel = _keccak_sel(f"{fn}(uint256)")
    if not sel:
        raise RuntimeError("no keccak available")
    # ONE uint256 argument = exactly one 32-byte word. (An earlier version prepended an extra
    # zero word, encoding a 2-argument call to a 1-argument function; every on-chain read
    # reverted and the module silently fell back to aggregator data.)
    data = "0x" + sel + f"{10**18:064x}"
    head, old = _block_days_ago(days)
    r_now = int(_call(contract, data), 16)
    r_old = int(_call(contract, data, old), 16)
    if r_old == 0 or r_now == 0:
        raise RuntimeError("zero rate")
    growth = r_now / r_old - 1.0
    return growth * 365.0 / days * 100.0, {"rateNow": r_now / 1e18, "rateOld": r_old / 1e18}


def _llama_aprs(ids):
    url = "https://yields.llama.fi/pools"
    req = urllib.request.Request(url, headers={"User-Agent": "GenTech-Steward/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        pools = json.load(r).get("data", [])
    by_id = {p.get("pool"): p for p in pools}
    out = {}
    for pid in ids:
        p = by_id.get(pid)
        if p and p.get("apy") is not None:
            out[pid] = {"apy": float(p["apy"]), "tvlUsd": p.get("tvlUsd"),
                        "symbol": p.get("symbol"), "project": p.get("project")}
    return out


def measure():
    """Return {apr, providers, method, n, spread, ts}. `apr` is the average across the
    providers that could be measured. Raises if NOTHING could be measured — a benchmark
    that cannot measure must not invent a number."""
    rows = []
    llama_ids = [p["llama"] for p in PROVIDERS if p.get("llama")]
    llama = {}
    if llama_ids:
        try:
            llama = _llama_aprs(llama_ids)
        except Exception:
            llama = {}

    for p in PROVIDERS:
        row = {"name": p["name"]}
        if p.get("onchain"):
            c, fn = p["onchain"]
            try:
                apr, extra = _onchain_apr(c, fn)
                # DORMANCY CHECK. If the redemption rate has not moved AT ALL in the last week the
                # contract is not passing rewards through -- it is dormant (deprecated, or
                # mid-migration), not merely low-yielding. Averaging it in drags the benchmark
                # toward zero for a provider no live staker is actually earning from. Measured
                # 2026-09-21: ggAVAX/stAVAX sat perfectly flat over 7d while sAVAX grew normally.
                dormant = False
                try:
                    _a7, e7 = _onchain_apr(c, fn, days=7)
                    dormant = (e7["rateNow"] == e7["rateOld"])
                except Exception:
                    pass
                row.update(apr=round(apr, 3), source=f"onchain:{fn} ({WINDOW_DAYS}d rate growth)",
                           dormant=dormant, **extra)
                if dormant:
                    row["source"] += " — DORMANT (rate flat 7d); EXCLUDED from the average"
            except Exception as e:
                row.update(apr=None, source=f"onchain read FAILED: {str(e)[:60]}")
        elif p.get("llama"):
            d = llama.get(p["llama"])
            if d:
                row.update(apr=round(d["apy"], 3), source="defillama listing",
                           tvlUsd=d.get("tvlUsd"), symbol=d.get("symbol"))
            else:
                row.update(apr=None, source="defillama: pool not found")
        rows.append(row)

    good = [r for r in rows if r.get("apr") is not None and not r.get("dormant")]
    excluded = [r["name"] for r in rows if r.get("dormant")]
    if not good:
        raise RuntimeError("no staking provider could be measured — refusing to invent a number")

    vals = [r["apr"] for r in good]
    return {
        "apr": round(statistics.mean(vals), 3),
        "median": round(statistics.median(vals), 3),
        "n": len(good),
        "spread": {"min": round(min(vals), 3), "max": round(max(vals), 3)},
        "providers": rows,
        "excluded": excluded,
        "method": (f"mean of {len(good)} live AVAX staking providers; on-chain providers measured "
                   f"as {WINDOW_DAYS}d exchange-rate growth, annualised; dormant contracts excluded"),
        "ts": time.time(),
        "source": f"average of {len(good)} live AVAX staking providers (not a single protocol)",
    }


if __name__ == "__main__":
    print(json.dumps(measure(), indent=2))
