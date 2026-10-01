#!/usr/bin/env python3
"""bridge_quote.py — LIVE EVM->Solana bridge quotes, fail-closed.

WHY THIS EXISTS (2026-09-24)
----------------------------
`solana_homebase.py action_bridge()` was a STUB: it wrote a ledger line and returned the
literal string "dry-run (Across, sub-5s, ~0.08% fee)" with exit 0. It was printed as a working
bridge by `tranche2_demo.py` L63 and claimed in the Tranche-2 submission L19/L32. Nothing was
ever quoted, and the "~0.08%" was not a venue number at all — it was literally the sum of two
constants in our own source (`ACROSS_LP_FEE_PCT` 0.06 + `ACROSS_RELAYER_FEE_PCT` 0.02).

MEASURED on 2026-09-24 (with controls):
  Across suggested-fees, EVM -> Solana:
    base -> solana       400 ROUTE_NOT_ENABLED      "Route is not enabled."
    arbitrum -> solana   400 ROUTE_NOT_ENABLED
    ethereum -> solana   400 ROUTE_NOT_ENABLED
  CONTROLS (prove the endpoint is live and our payload is well-formed):
    base -> arbitrum     200 ENABLED (estimatedFillTimeSec 1)
    base -> ethereum     200 ENABLED (estimatedFillTimeSec 2)
  => Every EVM->Solana route Across serves is DISABLED. Across cannot carry this leg.

  deBridge DLN (GET https://dln.debridge.finance/v1.0/dln/quote): LIVE, returns a real
  quote with a real fee. This module uses that.

THE RULE THIS MODULE ENFORCES
-----------------------------
Fail CLOSED. A quote is either a live venue number or it is an explicit UNAVAILABLE.
There is no third state. If the venue cannot be reached we do NOT fall back to a constant —
that fallback is the whole defect this file replaces. `agentic_bridge.get_across_quote()`
silently degrades to an estimate on failure, so a dead route reads as a working quote; do not
route this leg through it until That fallback is removed.

USAGE
  python3 bridge_quote.py --selftest
  python3 bridge_quote.py --from base --amount 20
"""
import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

# ── deBridge DLN ─────────────────────────────────────────────────────────────
DLN_QUOTE = "https://dln.debridge.finance/v1.0/dln/quote"
SOLANA_CHAIN_ID = 7565164            # deBridge's chain id for Solana (not a public chain id)
SOLANA_USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
SOLANA_TREASURY = "BE815V7ojVz63PDxFFSEQyGSe5PZE2fAdKUU6Rd5pUvP"

# Source EVM chains we can bridge FROM (chain_id, USDC address).
SOURCE_CHAINS = {
    "base":      (8453,  "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"),
    "avalanche": (43114, "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"),
    "arbitrum":  (42161, "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"),
    "ethereum":  (1,     "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"),
}

_B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58_to_hex(address):
    """Base58 -> 0x-prefixed hex, as deBridge requires for Solana ids.

    deBridge validates Solana token/recipient fields against /^0x(?:.{40}|.{64})$/ — a raw
    base58 mint is REJECTED with INVALID_QUERY_PARAMETERS. Sending base58 was my first attempt
    and it failed; the 0x-hex form is the correct encoding.
    """
    n = 0
    for ch in address:
        n = n * 58 + _B58.index(ch)
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    pad = len(address) - len(address.lstrip("1"))
    return "0x" + (b"\x00" * pad + body).hex()


class QuoteUnavailable(Exception):
    """Raised when no LIVE venue quote can be obtained. Never converted into a number."""


def debridge_quote(source, amount_usdc, recipient=SOLANA_TREASURY, timeout=30):
    """Live deBridge DLN quote, EVM -> Solana. Raises QuoteUnavailable; NEVER estimates."""
    if source not in SOURCE_CHAINS:
        raise QuoteUnavailable(f"unknown source chain {source!r}; have {sorted(SOURCE_CHAINS)}")
    chain_id, usdc = SOURCE_CHAINS[source]
    amount = int(round(amount_usdc * 1_000_000))
    params = {
        "srcChainId": str(chain_id),
        "srcChainTokenIn": usdc,
        "srcChainTokenInAmount": str(amount),
        "dstChainId": str(SOLANA_CHAIN_ID),
        "dstChainTokenOut": b58_to_hex(SOLANA_USDC_MINT),
        "dstChainTokenOutRecipient": b58_to_hex(recipient),
        "srcChainOrderAuthorityAddress": "0x572ABd6461BED2258615E6b99c585Ab7c5d05037",
        "dstChainOrderAuthorityAddress": b58_to_hex(recipient),
    }
    url = f"{DLN_QUOTE}?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (GenTech Agentic Treasury; +https://gentechlabs.net)",
        })
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()[:200]
        except Exception:
            pass
        raise QuoteUnavailable(f"deBridge HTTP {e.code}: {body}") from e
    except Exception as e:
        raise QuoteUnavailable(f"deBridge unreachable: {type(e).__name__}: {e}") from e

    if "estimation" not in data:
        raise QuoteUnavailable(f"deBridge returned no estimation: {json.dumps(data)[:200]}")

    est = data["estimation"]
    give = int(est["srcChainTokenIn"]["amount"])            # includes operating expense
    receive = int(est["dstChainTokenOut"]["recommendedAmount"])
    cost = give - receive
    return {
        "venue": "debridge-dln",
        "source_chain": source,
        "destination_chain": "solana",
        "amount_requested_usdc": amount_usdc,
        "you_send_usdc": give / 1e6,
        "recipient_receives_usdc": receive / 1e6,
        "cost_usdc": cost / 1e6,
        "cost_pct": (cost / give * 100) if give else None,
        "fix_fee_wei": data.get("fixFee"),
        "protocol_fee": data.get("protocolFee"),
        "live": True,                    # this IS a venue quote, not an estimate
        "quote_ts_utc": None,
    }


def across_evm_to_solana_enabled(source, timeout=25):
    """Probe whether Across can carry EVM->Solana AT ALL. Returns (enabled, detail).

    Kept as a live check rather than a hardcoded 'Across is dead', because a route can be
    re-enabled by the venue at any time and a stale constant would then wrongly block it.
    """
    from datetime import datetime, timezone
    chain_id, usdc = SOURCE_CHAINS[source]
    params = {
        "originChainId": str(chain_id),
        "destinationChainId": "34268394551451",   # Across's chain id for Solana
        "token": usdc,
        "amount": "20000000",
        "recipient": SOLANA_TREASURY,
    }
    url = f"https://app.across.to/api/suggested-fees?{urllib.parse.urlencode(params)}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json",
                                                   "User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            json.loads(resp.read().decode())
        return True, f"Across {source}->solana ENABLED at {datetime.now(timezone.utc).isoformat()}"
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {}
        return False, f"Across {source}->solana HTTP {e.code} {body.get('code','')} {body.get('message','')}".strip()
    except Exception as e:
        return False, f"Across probe failed: {type(e).__name__}: {e}"


def best_quote(amount_usdc, sources=("base", "avalanche"), recipient=SOLANA_TREASURY):
    """Cheapest LIVE quote across the source rails we actually hold. Fail-closed."""
    quotes, errors = [], {}
    for s in sources:
        try:
            quotes.append(debridge_quote(s, amount_usdc, recipient))
        except QuoteUnavailable as e:
            errors[s] = str(e)
    if not quotes:
        return {"status": "QUOTE UNAVAILABLE", "venues_tried": list(sources),
                "errors": errors,
                "note": "No live venue quote. Refusing to substitute an estimate — a fabricated "
                        "fee is exactly the defect this module replaces."}
    best = min(quotes, key=lambda q: q["cost_usdc"])
    best["compared"] = quotes
    best["status"] = "OK (live venue quote)"
    return best


def all_routes_measured(amount_usdc, recipient=SOLANA_TREASURY):
    """Every EVM->Solana route: which venues can ACTUALLY carry it, with live numbers.

    Written for the demo/submission: it must be impossible to print this and mistake an
    unavailable route for a working one. Every entry carries `venue_available` explicitly,
    so a caller that naively sums or prints the structure still cannot read a dead route
    as a working one — and the headline answer is pre-computed under `verdict`.
    """
    from datetime import datetime, timezone
    out = {"amount_usdc": amount_usdc, "destination": "solana",
           "measured_at_utc": datetime.now(timezone.utc).isoformat()}
    out["across"] = {}
    for s in SOURCE_CHAINS:
        ok, detail = across_evm_to_solana_enabled(s)
        out["across"][s] = {"venue_available": ok, "enabled": ok,
                            "can_carry_evm_to_solana": ok, "detail": detail}
    out["debridge"] = {}
    for s in ("base", "avalanche"):
        try:
            q = debridge_quote(s, amount_usdc, recipient)
            q["venue_available"] = True
            out["debridge"][s] = q
        except QuoteUnavailable as e:
            out["debridge"][s] = {"venue_available": False, "status": "QUOTE UNAVAILABLE",
                                  "reason": str(e)}
    live = [s for s, v in out["debridge"].items() if v.get("venue_available")]
    out["verdict"] = {
        "across_can_carry": any(v["venue_available"] for v in out["across"].values()),
        "debridge_can_carry": bool(live),
        "surviving_venues": (["debridge-dln"] if live else []),
        "source_rails_with_live_quotes": live,
        "note": ("Across EVM->Solana is not enabled on ANY route; deBridge is live. "
                 "A cost figure from a non-live venue is an estimate, not a quote."),
    }
    return out


def format_for_demo(amount_usdc, recipient=SOLANA_TREASURY):
    """Human-readable block for the demo/submission — unavailable routes stated AS unavailable."""
    d = all_routes_measured(amount_usdc, recipient)
    lines = [f"## EVM->Solana bridge — LIVE venue measurement (${amount_usdc:g} USDC)", ""]
    lines.append("Across (the venue our docs name):")
    for s, v in d["across"].items():
        lines.append(f"  {s:9s} -> solana : {'ENABLED' if v['venue_available'] else 'NOT ENABLED'}")
    lines.append("")
    lines.append("deBridge DLN (the venue that actually works today):")
    for s, v in d["debridge"].items():
        if v.get("venue_available"):
            lines.append(f"  {s:9s} -> solana : ${v['you_send_usdc']:.4f} -> "
                         f"${v['recipient_receives_usdc']:.4f}  cost ${v['cost_usdc']:.4f} "
                         f"({v['cost_pct']:.3f}%)  [LIVE]")
        else:
            lines.append(f"  {s:9s} -> solana : QUOTE UNAVAILABLE - {v.get('reason', '')[:60]}")
    lines.append("")
    lines.append(f"  surviving venue: {', '.join(d['verdict']['surviving_venues']) or 'NONE'}")
    lines.append(f"  measured at    : {d['measured_at_utc']}")
    return "\n".join(lines)


def _selftest():
    print("=== bridge_quote.py selftest ===")
    print("\n1. Across EVM->Solana (expect DISABLED — this is the finding, not a failure):")
    for s in ("base", "arbitrum", "ethereum"):
        ok, detail = across_evm_to_solana_enabled(s)
        print(f"   {s:9s} -> solana : {'ENABLED' if ok else 'DISABLED'}  {detail[:90]}")

    print("\n2. deBridge DLN (expect a LIVE quote with a real fee):")
    try:
        q = debridge_quote("base", 20)
        print(f"   base -> solana : LIVE  send ${q['you_send_usdc']:.6f} -> "
              f"recv ${q['recipient_receives_usdc']:.6f}  cost ${q['cost_usdc']:.4f} "
              f"({q['cost_pct']:.4f}%)")
    except QuoteUnavailable as e:
        print(f"   deBridge FAILED: {e}")

    print("\n3. FAIL-CLOSED: an unreachable venue must return UNAVAILABLE, never a number:")
    global DLN_QUOTE
    _saved = DLN_QUOTE
    DLN_QUOTE = "https://dln-debridge-nonexistent-host.invalid/v1.0/dln/quote"
    try:
        q = debridge_quote("base", 20, timeout=5)
        print(f"   ❌ FAILED: returned a number on a dead host -> {q}")
    except QuoteUnavailable as e:
        print(f"   ✅ raises QuoteUnavailable (no fabricated fee): {str(e)[:70]}")
    finally:
        DLN_QUOTE = _saved

    print("   and an unknown chain must also refuse rather than guess:")
    try:
        debridge_quote("dogecoin", 20)
        print("   ❌ FAILED: accepted an unknown chain")
    except QuoteUnavailable as e:
        print(f"   ✅ {str(e)[:70]}")

    print("\n4. Cost vs SIZE (the number that matters for our $20-150 tranche):")
    for amt in (20, 50, 150, 1000):
        try:
            q = debridge_quote("base", amt)
            print(f"   ${amt:>5} -> cost ${q['cost_usdc']:>8.4f} = {q['cost_pct']:>7.3f}%")
        except QuoteUnavailable as e:
            print(f"   ${amt:>5} -> {e}")
    print("\n5. b58 encoding (base58 is REJECTED by deBridge; 0x-hex is required):")
    print(f"   {SOLANA_USDC_MINT} -> {b58_to_hex(SOLANA_USDC_MINT)}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--from", dest="src", default="base")
    p.add_argument("--amount", type=float, default=20.0)
    a = p.parse_args()
    if a.selftest:
        _selftest()
        return
    try:
        print(json.dumps(debridge_quote(a.src, a.amount), indent=2))
    except QuoteUnavailable as e:
        print(json.dumps({"status": "QUOTE UNAVAILABLE", "reason": str(e)}, indent=2))
        raise SystemExit(3)          # non-zero: a failed quote is NOT a success


if __name__ == "__main__":
    main()
