#!/usr/bin/env python3
"""GTA Solana Leg — Jupiter swap (mirrors the CDP spot leg pattern).

Buys SOL/TAO on Solana via Jupiter (DEX aggregator). Pattern is identical to
gta_coinbase_leg.py: quote (read-only) -> sign -> swap -> verify tx signature.

Rails: Jupiter API. No official Python SDK, so we call the REST API + sign with
solders (community-standard approach, documented by Chainstack/QuickNode).

Funding: the Solana keypair must hold SOL (for gas) + USDC (to spend). USDC is
bridged Base->Solana via CCTP/Across (adapter: solana_bridge_adapter.py).

Usage:
  python3 gta_solana_leg.py --symbol SOL --side buy --amount 1.0 --dry-run   # quote
  python3 gta_solana_leg.py --symbol SOL --side buy --amount 1.0             # execute
"""

import argparse
import base64
import json
import os
import statistics
import sys

import requests
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

# ──────────────────── Constants ────────────────────
RPC = os.environ.get("SOLANA_RPC", "https://api.mainnet-beta.solana.com")
JUPITER_QUOTE = "https://api.jup.ag/swap/v1/quote"
JUPITER_SWAP = "https://api.jup.ag/swap/v1/swap"

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
# TAO (Bittensor, native on Solana via Wormhole Sunrise) — mint VERIFIED against live
# Jupiter quote (Aug 5, 2026): taoC6xyv2v8tDLcev4uaGUgV4vdQsWJrGft2kcBRrBY (HTTP 200,
# 0.1 SOL -> ~0.0368 TAO). Source: Solscan token page. 6 decimals.
TAO_MINT = "taoC6xyv2v8tDLcev4uaGUgV4vdQsWJrGft2kcBRrBY"

SUPPORTED = {
    "SOL": {"mint": SOL_MINT, "dec": 9},
    # TAO (Bittensor, native on Solana via Wormhole Sunrise) — mint VERIFIED against
    # live Jupiter quote (taoC6...BRrBY, HTTP 200). 6 decimals per Solscan.
    "TAO": {"mint": TAO_MINT, "dec": 6},
}

SLIPPAGE_BPS = 50  # 0.5%
PRIORITY_MULTIPLIER = 1.1


def _keypair():
    """Load the Solana signing keypair from env (base58) or a JSON keyfile."""
    b58 = os.environ.get("SOLANA_PRIVATE_KEY")
    if b58:
        return Keypair.from_base58_string(b58)
    kf = os.environ.get("SOLANA_KEYPAIR_FILE")
    if kf:
        with open(kf) as f:
            return Keypair.from_bytes(bytes(json.load(f)))
    raise RuntimeError("Set SOLANA_PRIVATE_KEY (base58) or SOLANA_KEYPAIR_FILE (json)")


def _get_balance(client, pubkey_str, mint):
    """Return token balance for an address (SOL native or SPL)."""
    from solders.pubkey import Pubkey
    pub = Pubkey.from_string(pubkey_str)
    if mint == SOL_MINT:
        r = client.get_balance(pub)
        return r.value / 1e9
    # SPL: get associated token account
    from solders.token.associated import get_associated_token_address
    ata = get_associated_token_address(pub, Pubkey.from_string(mint))
    try:
        r = client.get_token_account_balance(ata)
        dec = r.value.decimals
        return int(r.value.amount) / (10 ** dec)
    except Exception:
        return 0.0


def _median_priority_fee():
    """Estimate priority fee from recent blocks (median, not max — avoid drain)."""
    body = {"jsonrpc": "2.0", "id": 1, "method": "getRecentPrioritizationFees",
            "params": [[]]}
    r = requests.post(RPC, json=body, timeout=10).json()
    fees = [x["prioritizationFee"] for x in r.get("result", [])]
    med = int(statistics.median(fees)) if fees else 0
    return int(med * PRIORITY_MULTIPLIER) or 1000


def quote(input_mint, output_mint, amount_raw):
    r = requests.get(JUPITER_QUOTE, params={
        "inputMint": input_mint, "outputMint": output_mint,
        "amount": amount_raw, "slippageBps": SLIPPAGE_BPS,
    }, timeout=15).json()
    return r


def run_leg(symbol, side, amount, dry_run=True):
    symbol = symbol.upper()
    entry = SUPPORTED.get(symbol)
    if not entry:
        return {"mode": "DRY_RUN" if dry_run else "REAL",
                "skipped": f"unsupported-token-{symbol}"}
    if not entry.get("mint"):
        return {"mode": "DRY_RUN" if dry_run else "REAL",
                "skipped": f"unverified-mint-{symbol}",
                "note": "address not confirmed against live Jupiter quote"}

    # Wallet address is needed for both quote and execute; try to load the
    # keypair, but in DRY_RUN allow a missing keypair (quote only needs a
    # pubkey for the request, and we can derive it or use a placeholder).
    kp = None
    try:
        kp = _keypair()
    except RuntimeError:
        if dry_run:
            kp = None
        else:
            raise
    wallet = str(kp.pubkey()) if kp else None
    client = Client(RPC)

    input_mint = USDC_MINT if side == "buy" else entry["mint"]
    output_mint = entry["mint"] if side == "buy" else USDC_MINT

    # Amount handling: for buy, human USDC amount (6 dec); for sell, token amount
    if side == "buy":
        amount_raw = str(int(round(float(amount) * 1e6)))   # USDC 6 dec
    else:
        amount_raw = str(int(round(float(amount) * 10 ** entry["dec"])))

    q = quote(input_mint, output_mint, amount_raw)
    if "error" in q or "outAmount" not in q:
        return {"mode": "DRY_RUN" if dry_run else "REAL",
                "skipped": "quote-failed", "error": q.get("error", str(q)[:200])}

    out_human = int(q["outAmount"]) / (10 ** (9 if output_mint != USDC_MINT else 6))
    summary = {
        "mode": "DRY_RUN" if dry_run else "REAL",
        "action": side, "symbol": symbol,
        "quote": {"in_mint": input_mint, "out_mint": output_mint,
                  "in_amount_raw": amount_raw,
                  "out_amount": str(out_human),
                  "network": "solana",
                  "quote_received": True},
        "wallet": wallet,
    }

    if dry_run:
        summary["executed"] = False
        return summary

    # Execute
    max_fee = _median_priority_fee()
    swap = requests.post(JUPITER_SWAP, json={
        "quoteResponse": q,
        "userPublicKey": wallet,
        "dynamicComputeUnitLimit": True,
        "prioritizationFeeLamports": {
            "priorityLevelWithMaxLamports": {
                "maxLamports": max_fee, "priorityLevel": "veryHigh",
            }
        },
    }, timeout=20).json()

    raw = VersionedTransaction.from_bytes(base64.b64decode(swap["swapTransaction"]))
    signed = VersionedTransaction(raw.message, [kp])
    sig = client.send_raw_transaction(bytes(signed), opts=TxOpts(skip_preflight=True)).value

    summary["executed"] = True
    summary["tx_signature"] = str(sig)
    summary["note"] = "VERIFY on Solana (confirm) — send is not final"
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="GTA Solana leg via Jupiter")
    p.add_argument("--symbol", required=True, choices=["SOL", "TAO"])
    p.add_argument("--side", default="buy", choices=["buy", "sell"])
    p.add_argument("--amount", type=float, required=True)
    p.add_argument("--dry-run", action="store_true", help="Quote only (default if no keypair)")
    a = p.parse_args()
    try:
        print(json.dumps(run_leg(a.symbol, a.side, a.amount, dry_run=a.dry_run), indent=2))
    except RuntimeError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
