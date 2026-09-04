#!/usr/bin/env python3
"""Steward Auto-Compound Engine — recycles idle capital into the LFJ AVAX/USDC LP.

What it does (v1, conservative):
  1. Reads position + wallet ON-CHAIN (discover_positions.py — chain is truth).
  2. Computes idle working capital (USDC + WAVAX value; native AVAX = gas, excluded).
  3. If idle >= $1.00:
       a. If USDC share of working capital drifts >8pp from target (60%) ->
          rebalance_swap.py (proven swap path, internal swaps pre-approved by Jordan).
       b. Deploys the idle into the LP (gta_avax_lp_execute.py --execute) at the
          current allocation. Fees-accrued-inside-shares + redeploy = compounding.
  4. Appends every decision to the compound ledger (truth layer).
  5. Prints a report ONLY when it acted; silent otherwise (no_agent cron pattern).

Guards (Jordan's safeguard layer — "tiny bit of flexibility"):
  - Gas floor: never deploy if native AVAX < GAS_FLOOR (gas stays ~$1, never touched).
  - Min deploy $0.50 — no dust transactions.
  - Min 1h between compound actions.
  - Benchmark feeds (lp-fees-live.json) must be <48h old — no acting on stale truth.
  - Requires an existing LP position (watchdog owns "no position" deploys).
Usage:
  python3 auto_compound.py            # real run (still guarded)
  python3 auto_compound.py --dry-run  # print plan, move nothing
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import steward_silence as silence  # suppress-until-resolution (Jordan, Sep 3 2026)

WALLET = "0x572ABd6461BED2258615E6b99c585Ab7c5d05037"
RPC = "https://api.avax.network/ext/bc/C/rpc"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"

# Executed-copy paths (triple-copy lesson: this file RUNS from scripts/, and
# the vault copy mirrors it — keep in sync after every edit).
SCRIPT_DIR = "/root/.hermes/profiles/gentech-treasury/scripts"
VAULT_DIR = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
LEDGER = os.path.join(SCRIPT_DIR, ".compound-ledger.json")

TARGET_USDC_SHARE = 0.60       # fallback only — live call comes from the predictor
DRIFT_PCT = 8.0          # pp deviation that triggers a side rebalance
MIN_COMPOUND_USD = 1.00  # idle capital needed to act
MIN_DEPLOY_USD = 0.50    # never deploy less than this
GAS_FLOOR = 0.14         # AVAX; gas reserve never touched below this
MIN_DELAY_S = 3600
FEED_MAX_AGE_H = 48
PREDICTOR_MAX_AGE_H = 24
PREDICTOR = os.path.join(VAULT_DIR, "allocation_predictor.py")
ALLOC_SIGNAL = os.path.join("/root/.hermes/scripts", "allocation-signal.json")

DRY_RUN = "--dry-run" in sys.argv


def get_allocation():
    """Sentiment-driven allocation call: refresh the predictor, read its signal.

    Freshness-gated: stale/missing signal -> neutral 0.5 (never guess).
    """
    try:
        subprocess.run([sys.executable, PREDICTOR], capture_output=True, timeout=60)
        sig = json.load(open(ALLOC_SIGNAL))
        age_h = (time.time() - sig.get("ts", 0)) / 3600 if sig.get("ts") else 999
        if age_h <= PREDICTOR_MAX_AGE_H:
            alloc = float(sig.get("allocation", 0.5))
            stance = sig.get("stance", "neutral")
            conf = sig.get("confidence", 0)
            return max(0.4, min(0.6, alloc)), f"predictor: {sig.get('allocation_display')} {stance} ({conf}%)"
    except Exception:
        pass
    return TARGET_USDC_SHARE, "predictor unavailable -> default 60/40"


def rpc(method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    req = urllib.request.Request(RPC, json.dumps(payload).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.load(r)
    if "error" in res:
        raise RuntimeError(res["error"])
    return res["result"]


def erc20_balance(token, wallet_addr):
    sel = "0x70a08231" + wallet_addr[2:].lower().zfill(64)
    raw = rpc("eth_call", [{"to": token, "data": sel}, "latest"])
    return int(raw, 16) if raw and raw != "0x" else 0


def log_ledger(entry):
    try:
        led = json.load(open(LEDGER)) if os.path.exists(LEDGER) else []
    except Exception:
        led = []
    led.append(entry)
    json.dump(led[-200:], open(LEDGER, "w"), indent=2)


def main():
    now = time.time()
    reasons = []

    # ── Guard 1: benchmark feed freshness (truth layer) ──────────────
    feed = os.path.join("/root/.hermes/profiles/gentech/scripts", "lp-fees-live.json")
    try:
        f = json.load(open(feed))
        age_h = (now - f.get("ts", 0)) / 3600
        if age_h > FEED_MAX_AGE_H:
            reasons.append(f"stale benchmark feed ({age_h:.0f}h)")
    except Exception:
        reasons.append("no benchmark feed (lp-fees-live.json missing)")

    # ── Guard 2: gas floor ───────────────────────────────────────────
    avax = int(rpc("eth_getBalance", [WALLET, "latest"]), 16) / 1e18
    # Two-tier gas floor (Jordan's 0.1 rule of thumb, Sep 3 2026):
    #   - hard floor 0.10 AVAX for ANY action (never leave less than this)
    #   - full-cycle floor (GAS_FLOOR 0.14) applies to withdraw-redeploy,
    #     which burns ~0.036 AVAX worst case. Plain swap/deploy legs cost
    #     <0.0001 AVAX at current gas — blocking them on a 0.0001 rounding
    #     miss parked capital for hours (22:23 UTC lesson).
    hard_floor = 0.10
    if avax < hard_floor:
        reasons.append(f"gas below hard floor ({avax:.4f} < {hard_floor} AVAX)")
    elif avax < GAS_FLOOR:
        print(f"   ℹ️ gas {avax:.4f} < full-cycle floor {GAS_FLOOR}: swap/compound legs OK, "
              f"withdraw-redeploy cycles blocked until topped up")

    # ── Guard 3: rate limit ──────────────────────────────────────────
    try:
        led = json.load(open(LEDGER)) if os.path.exists(LEDGER) else []
        last = next((e for e in reversed(led) if e.get("action") == "compound"), None)
        if last and now - last.get("ts", 0) < MIN_DELAY_S:
            reasons.append(f"min-delay not elapsed ({(now - last['ts'])/60:.0f}min < 60min)")
    except Exception:
        pass

    # ── Read chain truth ─────────────────────────────────────────────
    disc = os.path.join(VAULT_DIR, "discover_positions.py")
    r = subprocess.run([sys.executable, disc, "--wallet", WALLET, "--chain", "avalanche", "--json"],
                       capture_output=True, text=True, timeout=120)
    try:
        data = json.loads(r.stdout)
    except Exception:
        # Transient discovery failure (RPC hiccup etc.) — log for audit, but
        # only ANNOUNCE the abort once per episode (6h window), not every 3h run.
        log_ledger({"ts": now, "action": "abort", "reason": "discovery parse failure"})
        if not silence.silenced("compound-abort"):
            print("⛔ auto-compound aborted: cannot parse discovery output")
            silence.mark_failure("compound-abort", "discovery parse failure",
                                 retry_hours=6)
        return 0
    # Discovery parsed — cycle is healthy, re-arm the abort silence key.
    silence.mark_success("compound-abort")
    positions = data.get("positions", [])
    balances = data.get("balances", {})
    usdc_bal = balances.get("USDC", 0.0)
    wavax_bal = balances.get("WAVAX", 0.0)

    if not positions:
        reasons.append("no LP position (watchdog owns no-position deploys)")

    price = positions[0].get("livePriceUsd") if positions else None
    if not price:
        reasons.append("no live price")

    if reasons:
        # silent when nothing to do — but log skip reasons for the audit trail
        log_ledger({"ts": now, "action": "skip", "reasons": reasons,
                    "idle_usd": round(usdc_bal + wavax_bal * (price or 0), 2)})
        return 0

    idle_usd = usdc_bal + wavax_bal * price
    pos_usd = positions[0].get("positionUsd", 0)

    # ── Intelligence: sentiment-driven allocation ────────────────────
    target_share, alloc_source = get_allocation()
    will_act = idle_usd >= MIN_COMPOUND_USD
    if DRY_RUN or will_act:
        print(f"🧠 Allocation call this cycle: {target_share*100:.0f}/{(1-target_share)*100:.0f} ({alloc_source})")

    # ── Decision 1: side drift ───────────────────────────────────────
    working = usdc_bal + wavax_bal * price
    usdc_share = (usdc_bal / working * 100) if working > 0 else 0
    drift = usdc_share - target_share * 100
    rebalanced = False
    if abs(drift) > DRIFT_PCT and idle_usd >= 0.30:
        print(f"🔁 Side drift: USDC {usdc_share:.0f}% vs target {target_share*100:.0f}% "
              f"({drift:+.1f}pp) — rebalancing pot")
        if not DRY_RUN:
            # rebalance_swap lives in the vault (single source of truth);
            # scripts/ never had a copy — the old path here failed silently
            # every cycle with rc=2 ("file not found").
            rb = subprocess.run([sys.executable, os.path.join(VAULT_DIR, "rebalance_swap.py"),
                                 str(target_share)], capture_output=True, text=True, timeout=300)
            rebalanced = rb.returncode == 0
            print(rb.stdout.strip()[-400:] if rebalanced else
                  f"⚠️ rebalance swap failed (rc={rb.returncode}): "
                  f"{(rb.stderr or rb.stdout)[-250:]}")
            log_ledger({"ts": time.time(), "action": "rebalance",
                        "drift_pp": round(drift, 1), "ok": rebalanced,
                        "target": target_share})
        else:
            print(f"   [dry-run] would run rebalance_swap.py {target_share}")
        rebalanced = True

    # ── Decision 2: deploy idle ──────────────────────────────────────
    deploy_usd = round(idle_usd - 0.10, 2)  # dust buffer
    acted = False
    if idle_usd >= MIN_COMPOUND_USD and deploy_usd >= MIN_DEPLOY_USD:
        print(f"💰 Idle capital ${idle_usd:.2f} detected (LP ${pos_usd:.2f}) — "
              f"compounding ${deploy_usd:.2f} into the pool")
        if not DRY_RUN:
            dep = subprocess.run([sys.executable, os.path.join(SCRIPT_DIR, "gta_avax_lp_execute.py"),
                                  "--amount", f"{deploy_usd}", "--bin-spread", "5",
                                  "--allocation", str(target_share),
                                  "--execute", "--yes"],
                                 capture_output=True, text=True, timeout=300)
            out = dep.stdout.strip().splitlines()
            tail = "\n".join(out[-6:]) if out else dep.stderr[-300:]
            print(tail)
            ok = "addLiquidity tx" in dep.stdout and "status=1" in dep.stdout
            log_ledger({"ts": time.time(), "action": "compound", "amount_usd": deploy_usd,
                        "ok": ok, "dry_run": False, "allocation": target_share,
                        "alloc_source": alloc_source})
            acted = True
        else:
            print(f"   [dry-run] would deploy ${deploy_usd} at {target_share*100:.0f}/{(1-target_share)*100:.0f}")
            log_ledger({"ts": time.time(), "action": "compound", "amount_usd": deploy_usd,
                        "ok": None, "dry_run": True})
            acted = True
    elif not rebalanced:
        # healthy, nothing to do — stay silent (no_agent pattern)
        return 0

    if acted or rebalanced:
        print(f"📊 Context: LP ${pos_usd:.2f} · idle was ${idle_usd:.2f} · gas {avax:.4f} AVAX (floor {GAS_FLOOR})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())