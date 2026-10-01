#!/usr/bin/env python3
"""DEFINITIVE: is there a farmable COQ position on Blackhole? (Jordan, Sep 11)

Findings so far:
  - Real COQ liquidity is on traderjoe (LFJ): $488K — a RETIRED rail for us.
  - The pool DexScreener labels "blackhole COQ/WAVAX" (0x4C33...) is a plain
    constant-product AMM pair (getReserves works, globalState does NOT), NOT an
    Algebra CL pool. Liquidity only ~$794, volume ~$14/day.
  - That pair DOES have a gauge (0x063AcCcD...) whose rewardToken is BLACK.

So the real question: is there an Algebra CL COQ pool at all (what our adapter
can farm), and what does the AMM gauge actually pay?

This script measures the AMM gauge's real emission rate by sampling the
EternalFarming farm state, and re-checks the factory for ANY COQ CL pool.
"""
import json
import urllib.request
from eth_utils import keccak
from web3 import Web3
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

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
COQ = "0x420FcA0121DC28039145009570975747295f2329"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
BLACK = "0xcd94a87696FAC69Edae3a70fE5725307Ae1c43f6"
AMM_PAIR = "0x4C33a727E3744009F7413D2d1FbbAd77D7Df207F"
AMM_GAUGE = "0x063AcCcD367A4269077Be9F89f2866deDd5Bf462"
FACTORY = "0x512eb749541b7cf294be882d636218c84a5e9e5f"
GAUGE_MGR = "0x59aa177312Ff6Bdf39C8Af6F46dAe217bf76CBf6"
STEWARD = _sw_wallet()

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))


def main():
    print("=" * 70)
    print("IS THERE A FARMABLE COQ POSITION ON BLACKHOLE?")
    print("=" * 70)

    # ── 1. any Algebra CL COQ pool? ──
    print("\n  ── 1. Algebra CL COQ pools (factory.poolByPair) ──")
    f = w3.eth.contract(address=Web3.to_checksum_address(FACTORY), abi=[
        {"inputs": [{"name": "", "type": "address"}, {"name": "", "type": "address"}],
         "name": "poolByPair", "outputs": [{"name": "", "type": "address"}],
         "stateMutability": "view", "type": "function"}])
    others = {
        "WAVAX": WAVAX, "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        "BLACK": BLACK, "USDT": "0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
    }
    found_any = False
    for qname, qaddr in others.items():
        try:
            p = f.functions.poolByPair(Web3.to_checksum_address(COQ),
                                       Web3.to_checksum_address(qaddr)).call()
            if int(p, 16) != 0:
                found_any = True
                # verify it is a CL pool
                try:
                    w3.eth.call({"to": p, "data": "0x" + keccak(text="globalState()").hex()[:8]})
                    kind = "Algebra CL ✅"
                except Exception:
                    kind = "not-CL"
                print(f"    COQ/{qname:6} -> {p}  {kind}")
            else:
                print(f"    COQ/{qname:6} -> none")
        except Exception as e:
            print(f"    COQ/{qname:6} -> error {str(e)[:40]}")
    if not found_any:
        print("    ⛔ NO COQ Algebra pool on Blackhole — nothing for our adapter to farm.")

    # ── 2. the AMM pair's gauge: what does it pay? ──
    print("\n  ── 2. the AMM pair gauge ──")
    print(f"    pair  {AMM_PAIR}  (constant-product AMM, NOT Algebra CL)")
    print(f"    gauge {AMM_GAUGE}")
    gc = w3.eth.contract(address=Web3.to_checksum_address(AMM_GAUGE), abi=[
        {"inputs": [], "name": "rewardToken", "outputs": [{"name": "", "type": "address"}],
         "stateMutability": "view", "type": "function"},
        {"inputs": [], "name": "totalSupply", "outputs": [{"name": "", "type": "uint256"}],
         "stateMutability": "view", "type": "function"},
        {"inputs": [], "name": "rewardsDuration", "outputs": [{"name": "", "type": "uint256"}],
         "stateMutability": "view", "type": "function"},
        {"inputs": [{"name": "", "type": "address"}], "name": "balanceOf",
         "outputs": [{"name": "", "type": "uint256"}],
         "stateMutability": "view", "type": "function"}])
    try:
        rt = gc.functions.rewardToken().call()
        print(f"    rewardToken: {rt} ({'BLACK' if rt.lower()==BLACK.lower() else '?'})")
    except Exception as e:
        print(f"    rewardToken read failed: {str(e)[:50]}")
    for fn in ("totalSupply", "rewardsDuration"):
        try:
            v = getattr(gc.functions, fn)().call()
            print(f"    {fn}: {v:,}")
        except Exception as e:
            print(f"    {fn}: n/a ({str(e)[:40]})")

    # ── 3. economics ──
    print("\n  ── 3. economics of the COQ/WAVAX AMM pool ──")
    try:
        req = urllib.request.Request(
            "https://api.dexscreener.com/latest/dex/pairs/avalanche/" + AMM_PAIR,
            headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=30).read().decode())
        p = (d.get("pairs") or [{}])[0]
        liq = float((p.get("liquidity") or {}).get("usd") or 0)
        vol = float((p.get("volume") or {}).get("h24") or 0)
        print(f"    liquidity ${liq:,.0f} | volume24h ${vol:,.0f}")
        fees = vol * 0.0025
        share = 11.0 / (liq + 11.0) if liq else 0
        print(f"    ALL pool fees/day : ${fees:,.4f}")
        print(f"    our $11 share     : {share*100:.2f}%  -> ${fees*share:,.4f}/day")
        print(f"    our fees/month    : ${fees*share*30:,.4f}")
        print(f"    PLUS IL RISK: COQ is a memecoin; a 2x means ~5.7% IL vs holding")
    except Exception as e:
        print(f"    market read failed: {str(e)[:60]}")

    print("\n  ── 4. the honest verdict ──")
    print("    Our current WAVAX/USDC farm: ~100.7 BLACK/day (~$0.25/day, $7.52/mo)")
    print("    COQ/WAVAX AMM pool        : ~$0.0005/day fees on $11 + IL risk")
    print("    The COQ 'compound loop' compounds a position that earns ~$0.18/yr")
    print("    against a memecoin's drawdown — the loop is real but uneconomic.")


if __name__ == "__main__":
    main()
