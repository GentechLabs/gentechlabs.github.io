#!/usr/bin/env python3
"""Value the current Blackhole CL position from chain truth.

Hand-rolled tuple encoding produced garbage (2.3e10 USDC), so use the real
contract object to encode — the validated approach (see pitfall: never hand-roll
ABI encoding when the library can do it).
"""
import sys, json, urllib.request, time
sys.path.insert(0, '/root/.hermes/profiles/gentech-treasury/scripts')
from web3 import Web3
import blackhole_cl_adapter as A

# Rotating providers via the shared module (single hardcoded host = one Cloudflare 1015
# took every reader dark on 2026-09-22).
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from avax_rpc import connect as _rpc_connect, rpc_call as _rpc_call, RpcUnavailable
W = A.STEWARD_WALLET
# AVAX/USD — LIVE, never a standing constant. A hardcoded 7.46 here silently
# understated the WAVAX leg by ~32% (live $11.11) and was labelled "chain-read"
# upstream, which is a fabricated provenance claim. Fetch it; if the fetch
# fails, fall back to the last-known value and SAY SO in the output.
AVAX_USD_FALLBACK = 7.46


def _live_avax_usd():
    """Return (price_usd, source_string) for WAVAX."""
    try:
        u = ('https://coins.llama.fi/prices/current/'
             'avax:0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')
        with urllib.request.urlopen(u, timeout=15) as r:
            coins = json.load(r).get('coins', {})
        for _k, v in coins.items():
            price = float(v.get('price', 0) or 0)
            if price > 0:
                return price, 'defillama live WAVAX/USD (confidence %s)' % v.get('confidence')
    except Exception as e:
        return AVAX_USD_FALLBACK, 'FALLBACK constant %s (live fetch failed: %s)' % (AVAX_USD_FALLBACK, str(e)[:60])
    return AVAX_USD_FALLBACK, 'FALLBACK constant %s (no price in response)' % AVAX_USD_FALLBACK


AVAX_USD, AVAX_USD_SOURCE = _live_avax_usd()
print('AVAX/USD: $%.4f  [%s]' % (AVAX_USD, AVAX_USD_SOURCE))
try:
    w3 = _rpc_connect(timeout=40)
except RpcUnavailable as _e:
    print(f'❌ no AVAX RPC provider: {_e}')
    raise SystemExit(3)

nfpm = w3.eth.contract(address=Web3.to_checksum_address(A.LEGACY_NFPM), abi=A.NFPM_ABI)
fc = w3.eth.contract(address=Web3.to_checksum_address(A.LEGACY_FARMING_CENTER),
                     abi=A.FARMING_CENTER_ABI)

n = nfpm.functions.balanceOf(W).call()
print(f'wallet owns {n} CL NFTs\n')

total = 0.0
for i in range(n):
    tid = nfpm.functions.tokenOfOwnerByIndex(W, i).call()
    p = nfpm.functions.positions(tid).call()
    liq = p[7]
    tl, tu = p[5], p[6]
    owed0, owed1 = p[10], p[11]   # tokensOwed0 (USDC 6dp), tokensOwed1 (WAVAX 18dp)
    # staking: read deposits(tokenId) raw (not always in the bundled ABI)
    from web3 import Web3 as _W
    _sel = '0x' + _W.keccak(text='deposits(uint256)').hex()[:8]
    _r = w3.eth.call({'to': _W.to_checksum_address(A.LEGACY_FARMING_CENTER),
                      'data': _sel + format(tid, '064x')})
    staked = int.from_bytes(_r, 'big') != 0

    if liq == 0:
        v = owed0 / 1e6 + owed1 / 1e18 * AVAX_USD
        print(f'  #{tid}: liq=0 (drained) owed=${v:.4f} staked={staked}')
        total += v
        continue

    # simulate decreaseLiquidity using the contract object (correct encoding)
    params = {
        'tokenId': tid,
        'liquidity': liq,
        'amount0Min': 0,
        'amount1Min': 0,
        'deadline': int(time.time()) + 600,
    }
    try:
        out = nfpm.functions.decreaseLiquidity(params).call({'from': W})
        # amount0/amount1 follow token0/token1 ORDER, not a fixed USDC/WAVAX
        # assumption. Reading amount0 as USDC when token0 is WAVAX produced a
        # nonsense ~$9e11 valuation. Resolve decimals by token identity.
        t0, t1 = p[2].lower(), p[3].lower()
        if t0 == A.WAVAX.lower():
            aw, au = out[0] / 1e18, out[1] / 1e6
        else:
            au, aw = out[0] / 1e6, out[1] / 1e18
        v = aw * AVAX_USD + au
        print(f'  #{tid}: liq={liq:,} -> {aw:.6f} WAVAX + {au:.4f} USDC = ${v:.2f}  staked={staked}')
        total += v
    except Exception as e:
        print(f'  #{tid}: liq={liq:,} sim failed: {str(e)[:90]}  staked={staked}')

print(f'\nCL positions total: ${total:.2f}')

# ---- loose balances ----
def erc20_bal(addr, dec):
    c = w3.eth.contract(address=Web3.to_checksum_address(addr), abi=A.ERC20_ABI)
    return c.functions.balanceOf(W).call() / 10 ** dec

avax = w3.eth.get_balance(W) / 1e18
wav = erc20_bal(A.WAVAX, 18)
usd = erc20_bal(A.USDC, 6)
print(f'loose WAVAX: {wav:.6f} = ${wav*AVAX_USD:.2f}')
print(f'loose USDC : {usd:.4f} = ${usd:.2f}')
print(f'loose AVAX : {avax:.6f} = ${avax*AVAX_USD:.2f}')
grand = total + wav*AVAX_USD + usd + avax*AVAX_USD
print(f'\nTOTAL TREASURY: ${grand:.2f}')

# ── machine-readable truth (Sep 15 2026) ─────────────────────────────────
# WHY: refresh_state_capital.py used to HARDCODE these figures while labelling
# them "chain-read". That is a fabricated provenance claim — the exact class we
# refuse. Any consumer that needs the numbers must take them from here.
if '--json' in sys.argv:
    import json as _json
    print("__JSON__" + _json.dumps({
        "deployed_usd": round(total, 2),          # CL positions
        "loose_wavax_usd": round(wav*AVAX_USD, 2),
        "loose_usdc_usd": round(usd, 2),
        "loose_avax_usd": round(avax*AVAX_USD, 2),
        "dry_powder_usd": round(wav*AVAX_USD + usd + avax*AVAX_USD, 3),
        "total_usd": round(grand, 2),
        "avax_usd": AVAX_USD,
        "avax_usd_source": AVAX_USD_SOURCE,
        "source": "chain-read (value_now.py, settled)",
        "measured_at": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
    }))
