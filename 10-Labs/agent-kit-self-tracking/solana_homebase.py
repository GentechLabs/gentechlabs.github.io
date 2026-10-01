#!/usr/bin/env python3
"""Solana Homebase — Agentic Treasury Orchestrator (Superteam Tranche-2 MVP).

Ties the pieces of the Solana-as-homebase treasury into one command:
  earn (x402) -> bridge (EVM->Solana) -> deploy/yield (Jupiter) -> pay (Solana)

Mirrors the venue-agnostic engine pattern from the Agentic Treasury
(yield_lp_engine -> decide -> plan -> act), DRY_RUN by default — moves NO
funds unless SOLANA_REAL=1 AND a funded keypair + USDC balance exist, else it
refuses to fake a success.

Pieces it orchestrates:
  - gta_solana_leg.py    — Jupiter swap (SOL/TAO), live quotes verified
  - bridge_quote.py      — LIVE EVM->Solana quote (deBridge DLN), fail-closed
  - yield_lp_engine.py   — regime-driven allocation target (NOT wired in here yet)

CORRECTED 2026-09-24: this docstring previously claimed solana_bridge_adapter.py carried
"Across USDC Base/Avalanche -> Solana". That adapter is never imported (grep: one hit, the
line above) AND Across serves no EVM->Solana route at all — every route returns
ROUTE_NOT_ENABLED. deBridge DLN is the venue that actually quotes today.

Usage (dry-run by default):
  python3 solana_homebase.py --action status                # wallet balances
  python3 solana_homebase.py --action bridge --amount 10    # quote-only (dry)
  python3 solana_homebase.py --action buy --symbol SOL --amount 5 --dry-run
  python3 solana_homebase.py --action pay --to <addr> --amount 2

Set SOLANA_REAL=1 + SOLANA_PRIVATE_KEY to execute (Jordan greenlight only).
"""
import os, sys
sys.path.insert(0, "/root/.hermes/profiles/gentech-treasury/scripts")
import argparse
import json
from datetime import datetime, timezone

# ── State / ledger ───────────────────────────────────────────────────────────
_STATE = os.environ.get("AAE_STATE_DIR", os.path.expanduser("~/.hermes/scripts"))
LEDGER = os.path.join(_STATE, "solana-homebase-ledger.jsonl")


def _log(action, detail):
    rec = {"ts": datetime.now(timezone.utc).isoformat(),
           "action": action, "detail": detail,
           "mode": "REAL" if os.environ.get("SOLANA_REAL") == "1" else "DRY_RUN"}
    os.makedirs(os.path.dirname(LEDGER), exist_ok=True)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def _keypair():
    from solders.keypair import Keypair
    b58 = os.environ.get("SOLANA_PRIVATE_KEY")
    if b58:
        return Keypair.from_base58_string(b58)
    kf = os.environ.get("SOLANA_KEYPAIR_FILE")
    if kf:
        with open(kf) as f:
            return Keypair.from_bytes(bytes(json.load(f)))
    return None  # dry-run: no keypair is OK


def _real():
    return os.environ.get("SOLANA_REAL") == "1"


def action_status():
    """Wallet balances (SOL + USDC). Read-only, always safe."""
    kp = _keypair()
    if not kp:
        return {"status": "no_keypair", "note": "set SOLANA_PRIVATE_KEY or SOLANA_KEYPAIR_FILE",
                "action": "status", "mode": "DRY_RUN"}
    import sys as _s
    _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from gta_solana_leg import _get_balance, Client, SOL_MINT, USDC_MINT, RPC
    client = Client(RPC)
    wallet = str(kp.pubkey())
    sol = _get_balance(client, wallet, SOL_MINT)
    usdc = _get_balance(client, wallet, USDC_MINT)
    rec = _log("status", {"wallet": wallet, "sol": sol, "usdc": usdc})
    return rec["detail"]


def action_bridge(amount, recipient):
    """Bridge USDC EVM->Solana. Dry-run = a REAL live venue quote.

    WAS A STUB (fixed 2026-09-24). The old body wrote a ledger line and returned the literal
    string "dry-run (Across, sub-5s, ~0.08% fee)" with exit 0 — no quote, no venue call, and
    the "~0.08%" was the sum of two constants in our own source (ACROSS_LP_FEE_PCT 0.06 +
    ACROSS_RELAYER_FEE_PCT 0.02), not a venue figure. It was printed as a working bridge by
    tranche2_demo.py L63 and claimed in the Tranche-2 submission L19/L32.

    MEASURED 2026-09-24 with controls: Across serves NO EVM->Solana route (base/arbitrum/
    ethereum all return 400 ROUTE_NOT_ENABLED, while base->arbitrum and base->ethereum return
    200, proving the endpoint is live). So the venue the docs name cannot carry this leg.
    deBridge DLN IS live and is what we now quote.

    Fail-closed: if no live quote is available this reports QUOTE UNAVAILABLE and refuses to
    substitute a number. A fabricated fee that reads as a quote is the defect being replaced.
    """
    if not _real():
        _HERE = os.path.dirname(os.path.abspath(__file__))
        if _HERE not in sys.path:
            sys.path.insert(0, _HERE)
        try:
            from bridge_quote import best_quote
            _rcpt = recipient if recipient and recipient != "pending" \
                else "BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP"
            q = best_quote(amount, sources=("base", "avalanche"), recipient=_rcpt)
            if q.get("status", "").startswith("OK"):
                detail = {
                    "amount_usdc": amount, "recipient": recipient,
                    "status": "dry-run (LIVE quote, no funds move)",
                    "venue": q["venue"], "source_rail": q["source_chain"],
                    "you_send_usdc": round(q["you_send_usdc"], 6),
                    "recipient_receives_usdc": round(q["recipient_receives_usdc"], 6),
                    "cost_usdc": round(q["cost_usdc"], 6),
                    "cost_pct": round(q["cost_pct"], 4) if q.get("cost_pct") else None,
                    "live": True,
                }
            else:
                detail = {"amount_usdc": amount, "recipient": recipient,
                          "status": "dry-run — QUOTE UNAVAILABLE", "live": False,
                          "reason": q.get("note", "no live venue quote")}
        except Exception as e:
            detail = {"amount_usdc": amount, "recipient": recipient,
                      "status": "dry-run — QUOTE UNAVAILABLE", "live": False,
                      "error": f"{type(e).__name__}: {e}"}
    else:
        detail = {"amount_usdc": amount, "recipient": recipient,
                  "status": "pending-real",
                  "note": "real execution path not yet wired to a venue — see build-queue #38"}
    return _log("bridge", detail)["detail"]


def action_buy(symbol, amount):
    """Buy SOL/TAO via Jupiter. Dry-run = live quote."""
    import subprocess
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gta_solana_leg.py")
    cmd = [sys.executable, script, "--symbol", symbol.upper(), "--side", "buy",
           "--amount", str(amount)]
    if not _real():
        cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        out = {"error": r.stderr[-300:] or r.stdout[-300:]}
    rec = _log("buy", out)
    return rec["detail"]


def action_pay(to, amount):
    """Pay a recipient USDC on Solana. Requires REAL + funded keypair."""
    rec = _log("pay", {"to": to, "amount_usdc": amount,
                       "status": "queued — needs SOLANA_REAL=1 + funded keypair + greenlight"})
    return rec["detail"]


def main():
    p = argparse.ArgumentParser(description="Solana Homebase treasury orchestrator")
    p.add_argument("--action", required=True,
                   choices=["status", "bridge", "buy", "pay"])
    p.add_argument("--amount", type=float)
    p.add_argument("--symbol", choices=["SOL", "TAO"])
    p.add_argument("--to", help="recipient address (pay)")
    p.add_argument("--recipient", help="Solana recipient for bridge")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    if a.dry_run:
        os.environ.pop("SOLANA_REAL", None)  # force dry even if set

    if a.action == "status":
        out = action_status()
    elif a.action == "bridge":
        if not a.amount:
            raise SystemExit("bridge needs --amount (USDC)")
        out = action_bridge(a.amount, a.recipient or "pending")
    elif a.action == "buy":
        if not a.amount:
            raise SystemExit("buy needs --amount")
        out = action_buy(a.symbol or "SOL", a.amount)
    elif a.action == "pay":
        if not a.to or not a.amount:
            raise SystemExit("pay needs --to and --amount")
        out = action_pay(a.to, a.amount)
    else:
        out = {"error": "unknown action"}

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
