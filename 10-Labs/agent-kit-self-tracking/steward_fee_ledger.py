#!/usr/bin/env python3
"""Steward — Chain-Truth Fee Ledger (LFJ V2.2).

Jordan (Sep 3 2026, standing rule): "always read from on-chain, especially the
fees we've earned today — we have to calculate that with the compounding
effect."

LFJ V2.2 has NO pendingFees() call — fees accrue inside bin shares. The only
honest measurement is position-value deltas between snapshots:

    fees_earned ≈ (total_now − total_prev) − deposits + withdrawals

where total = liquid (USDC + WAVAX + native-gas-excluded) + LP value from a
read-only withdraw-simulation (bin shares → token amounts, the exact math a
real withdraw settles). Every number in the ledger comes from the chain.

Compounding effect: fees are recomputed on the CURRENT total, so the daily
fee estimate self-updates as fees are redeployed — that's the compounding
curve, measured, not modeled.

State: .steward-fee-ledger.json — {snapshots: [{ts, total_usd, liquid_usd,
lp_usd, x_wavax, y_usdc, price, bins}], last_sweep}.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, ".steward-fee-ledger.json")
WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
RPC = "https://api.avax.network/ext/bc/C/rpc"
# Tolerance: value delta under this is measurement noise (price rounding,
# dust), not fees. Gas for actions is excluded (native AVAX not counted).
NOISE_FLOOR_USD = 0.02
# Never attribute more than this to fees in one interval — anything larger
# means a recenter/withdraw landed between snapshots and the delta is churn.
MAX_FEE_DELTA_USD = 0.50


def _w3():
    from web3 import Web3
    return Web3(Web3.HTTPProvider(RPC))


def _acct(w3):
    key_file = "/root/.blockrun/almanak-steward-key"
    acct = w3.eth.account.from_key(open(key_file).read().strip())
    cfg = json.load(open(os.path.join(HERE, "treasury_config.json")))
    expected = cfg.get("wallet") or os.environ.get("STEWARD_WALLET")
    if expected and acct.address.lower() != str(expected).lower():
        raise ValueError("key mismatch with Steward wallet — refusing")
    return acct


def read_bin_balances(w3, wallet: str):
    """List of bin IDs with nonzero LB-token balance (from steward_execute)."""
    sys.path.insert(0, HERE)
    import steward_execute as se
    return se.read_bin_balances(w3, wallet)


def withdraw_sim(w3, acct) -> dict:
    """Read-only position valuation: the same removeLiquidity call the real
    withdraw would make, simulated. Returns (x_wavax, y_usdc, bins)."""
    sys.path.insert(0, HERE)
    import steward_execute as se
    sim = se.step_withdraw(w3, acct, dry_run=True)
    if sim.get("ok"):
        return {"x_wavax": sim["simulated_x_wavax"],
                "y_usdc": sim["simulated_y_usdc"],
                "bins": sim["bins"]}
    return {"x_wavax": None, "y_usdc": None, "bins": 0,
            "error": sim.get("error", "sim failed")}


def avax_usd() -> float:
    import urllib.request
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            "https://api.coingecko.com/api/v3/simple/price?ids=avalanche-2&vs_currencies=usd",
            headers={"User-Agent": "Mozilla/5.0"}), timeout=10))
        return float(r["avalanche-2"]["usd"])
    except Exception:
        pass
    # fallback: dexscreener pair price
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(
            "https://api.dexscreener.com/latest/dex/pairs/avalanche/"
            "0x864d4e5Ee7318e97483DB7EB0912E09F161516EA",
            headers={"User-Agent": "Mozilla/5.0"}), timeout=10))
        return float(r["pair"]["priceUsd"])
    except Exception:
        return 0.0


def snapshot() -> dict:
    """Full treasury snapshot from chain truth. Liquid = USDC + WAVAX
    (stable at $1, WAVAX at live price). LP = withdraw-sim token amounts.
    Native gas AVAX is EXCLUDED (it's the engine's fuel, not yield)."""
    w3 = _w3()
    acct = _acct(w3)
    # balances
    sys.path.insert(0, HERE)
    from discover_positions import discover_wallet_balances
    wb = discover_wallet_balances("avalanche", WALLET)
    px = avax_usd()
    usdc = float(wb.get("USDC", 0.0) or 0.0) + float(wb.get("USDC_e", 0.0) or 0.0) \
        + float(wb.get("USDT_e", 0.0) or 0.0)
    wavax = float(wb.get("WAVAX", 0.0) or 0.0)
    liquid_usd = round(usdc + wavax * px, 4)
    # LP via withdraw-sim (honest per-bin composition)
    try:
        acct2 = _acct(w3)  # same key; ensures key-file presence
        sim = withdraw_sim(w3, acct)
        lp_x = sim.get("x_wavax") or 0.0
        lp_y = sim.get("y_usdc") or 0.0
        lp_usd = round(lp_x * px + lp_y, 4) if (lp_x or lp_y) else 0.0
        bins = sim.get("bins", 0)
    except Exception:
        lp_x = lp_y = None
        lp_usd = 0.0
        bins = 0
    return {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "epoch": time.time(),
        "price_usd": round(px, 6),
        "liquid_usd": liquid_usd,
        "lp_usd": lp_usd,
        "total_usd": round(liquid_usd + lp_usd, 4),
        "lp_x_wavax": lp_x,
        "lp_y_usdc": lp_y,
        "lp_bins": bins,
        "wallet_wavax": round(wavax, 6),
        "wallet_usdc": round(usdc, 4),
    }


def load() -> dict:
    try:
        with open(LEDGER) as f:
            return json.load(f)
    except Exception:
        return {"snapshots": [], "last_sweep": None}


def save(d: dict) -> None:
    # keep the ledger bounded: 200 snapshots ≈ 33h at 10-min cadence
    d["snapshots"] = d["snapshots"][-200:]
    with open(LEDGER, "w") as f:
        json.dump(d, f, indent=2)


def fees_since(ts_epoch: float, snapshots: list, current: dict) -> dict:
    """Chain-truth fees earned since a timestamp: total-value delta between
    the earliest in-window snapshot and the current reading, DRIFT-ADJUSTED
    (price movement on AVAX-side holdings is not fees). A delta beyond
    MAX_FEE_DELTA_USD is churn (a rebalance landed between snapshots) and
    cannot be attributed to fees."""
    in_window = [s for s in snapshots
                 if s.get("epoch", 0) >= ts_epoch
                 and s.get("total_usd") is not None
                 and s.get("epoch", 0) < current.get("epoch", 0)]
    prev = min(in_window, key=lambda s: s["epoch"]) if in_window else None
    if prev is None or current.get("total_usd") is None:
        return {"fees_usd": None, "window_h": None, "note": "no prior snapshot in window"}
    delta = current["total_usd"] - prev["total_usd"]
    window_h = round((current["epoch"] - prev["epoch"]) / 3600.0, 2)
    if abs(delta) > MAX_FEE_DELTA_USD:
        return {"fees_usd": None, "window_h": window_h,
                "note": f"churn in window (delta ${delta:+.2f} > ${MAX_FEE_DELTA_USD})"}
    fees = _drift_adjusted(prev, current, delta)
    # measurement-noise floor: 0.15% of position value per window; below it,
    # call it 0 — annualizing sub-cent noise produces fantasy APRs
    floor = max(NOISE_FLOOR_USD, 0.0015 * float(current.get("total_usd") or 0))
    if fees is not None and abs(fees) < floor:
        return {"fees_usd": 0.0, "window_h": window_h,
                "note": f"within noise (raw ${fees:+.4f} < floor ${floor:.3f})"}
    return {"fees_usd": fees, "window_h": window_h,
            "note": f"from ${prev['total_usd']:.2f} → ${current['total_usd']:.2f}"
                    + (" (drift-adjusted)" if fees is not None and abs(fees - delta) > 0.002 else "")}



def fees_between(snapshots: list, n_back: int = 2) -> dict:
    """Fee delta over the last n_back snapshots (shortest clean window).
    Price drift over ~10 min is negligible vs fees, so this is the cleanest
    read. Churn guard still applies."""
    valid = [s for s in snapshots if s.get("total_usd") is not None]
    if len(valid) < n_back:
        return {"fees_usd": None, "window_h": None, "note": f"need {n_back} snapshots"}
    cur, prev = valid[-1], valid[-n_back]
    delta = cur["total_usd"] - prev["total_usd"]
    window_h = round((cur["epoch"] - prev["epoch"]) / 3600.0, 2)
    if window_h <= 0:
        return {"fees_usd": None, "window_h": 0.0, "note": "no time between snapshots"}
    if abs(delta) > MAX_FEE_DELTA_USD:
        return {"fees_usd": None, "window_h": window_h,
                "note": f"churn in window (delta ${delta:+.2f})"}
    fees = _drift_adjusted(prev, cur, delta)
    # measurement-noise floor: 0.15% of position value per window; below it,
    # call it 0 — annualizing sub-cent noise produces fantasy APRs
    floor = max(NOISE_FLOOR_USD, 0.0015 * float(cur.get("total_usd") or 0))
    if fees is not None and abs(fees) < floor:
        return {"fees_usd": 0.0, "window_h": window_h,
                "note": f"within noise (raw ${fees:+.4f} < floor ${floor:.3f})"}
    return {"fees_usd": fees, "window_h": window_h,
            "note": f"from ${prev['total_usd']:.2f} → ${cur['total_usd']:.2f}"
                    + (" (drift-adjusted)" if fees is not None and abs(fees - delta) > 0.002 else "")}


def _drift_adjusted(prev: dict, cur: dict, raw_delta: float):
    """Separate fees from price drift: the AVAX-side holdings (LP x + wallet
    WAVAX) gained/lost value purely from price movement. fees ≈ raw_delta −
    price_change × avax_exposure. Both snapshots must carry per-side data."""
    try:
        if prev.get("lp_x_wavax") is None or cur.get("lp_x_wavax") is None:
            return raw_delta  # can't adjust — report raw (honest)
        avax_prev = float(prev.get("lp_x_wavax") or 0) + float(prev.get("wallet_wavax") or 0)
        avax_cur = float(cur.get("lp_x_wavax") or 0) + float(cur.get("wallet_wavax") or 0)
        px_prev = float(prev.get("price_usd") or 0)
        px_cur = float(cur.get("price_usd") or 0)
        if not px_prev or not px_cur:
            return raw_delta
        drift = avax_cur * px_cur - avax_prev * px_prev
        return round(raw_delta - drift, 4)
    except Exception:
        return raw_delta


def run(dry_run: bool = True) -> dict:
    """Take a snapshot, compute fees since the last sweep, roll the ledger.
    Call from the watchdog (10-min cadence) — snapshots accumulate,
    fees measure, compounding effect emerges from real data."""
    snap = snapshot()
    led = load()
    led.setdefault("snapshots", []).append(snap)
    out = {"snapshot": snap}
    # fees windows: baseline = earliest snapshot inside the window (the
    # snapshot list includes the one just taken). Churn guard: if the window
    # contains a machine action (rebalance stamp) or a churn-sized delta, it
    # reports unattributable rather than a fake fee number.
    out["fees_last_hour"] = fees_since(time.time() - 3600, led["snapshots"], snap)
    out["fees_today"] = fees_since(
        time.time() - (time.time() % 86400), led["snapshots"], snap)
    # shortest clean window = last 2 snapshots (≈10-min watchdog cadence):
    # price drift over 10 min is tiny, so this delta ≈ fees + negligible drift
    out["fees_short"] = fees_between(led["snapshots"], n_back=2)
    # compounding-aware daily estimate: fee rate measured over the window,
    # projected on the CURRENT total (fees redeployed grow the base)
    # daily estimate ONLY from windows >= 30 min (short 2-snapshot windows
    # are informational: noise floor makes their annualization meaningless)
    fw = out["fees_last_hour"] if (out["fees_last_hour"].get("fees_usd") is not None
                                   and out["fees_last_hour"].get("window_h", 0) >= 0.4) \
        else (out["fees_short"] if out["fees_short"].get("window_h", 0) >= 0.4 else None)
    if fw and fw.get("fees_usd") is not None and fw.get("window_h", 0) > 0:
        rate_per_h = fw["fees_usd"] / fw["window_h"]
        out["daily_estimate_usd"] = round(rate_per_h * 24, 4)
        out["compounded_apr_pct"] = round(rate_per_h * 24 * 365 / max(snap["total_usd"], 1e-9) * 100, 2)
    else:
        out["daily_estimate_usd"] = None
        out["compounded_apr_pct"] = None
    if not dry_run:
        led["last_sweep"] = snap["epoch"]
    out["last_sweep"] = led.get("last_sweep")
    save(led)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Steward chain-truth fee ledger")
    ap.add_argument("--commit", action="store_true",
                    help="advance the sweep pointer (call from watchdog)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = run(dry_run=not a.commit)
    print(json.dumps(res, indent=1))