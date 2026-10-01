#!/usr/bin/env python3
"""Can we actually SWAP WAVAX -> USDC on Avalanche right now?

Why it matters: our idle $11.12 is 1.49 WAVAX with $0.00 USDC. A Blackhole
WAVAX/USDC CL position is TWO-SIDED, so "putting it back" needs a USDC leg.
Every direct-router attempt reverts (ISTF), but the chain shows real swaps DO
happen on our pool — executed by aggregators.

So ask the aggregators directly for a quote. A live quote = a real route =
the blocker is not a wall, it's just the wrong door.
"""
import json
import urllib.parse
import urllib.request

WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
AMOUNT_IN = str(int(0.744 * 1e18))   # half the idle WAVAX


def get(url, headers=None, timeout=25):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode()


def main():
    print("=" * 64)
    print("AGGREGATOR QUOTE HUNT — WAVAX -> USDC (0.744 WAVAX)")
    print("=" * 64)

    # 1. KyberSwap
    try:
        u = ("https://aggregator-api.kyberswap.com/avalanche/api/v1/routes?"
             + urllib.parse.urlencode({"tokenIn": WAVAX, "tokenOut": USDC,
                                       "amountIn": AMOUNT_IN}))
        d = json.loads(get(u))
        if d.get("code") == 0:
            rd = d["data"]["routeSummary"]
            print(f"  ✅ KyberSwap: {int(rd['amountOut'])/1e6:.4f} USDC "
                  f"via {rd.get('routeID','?')[:24]}")
            print(f"     router: {d['data'].get('routerAddress')}")
            for hop in (rd.get("route") or [])[:1]:
                for leg in hop:
                    print(f"     hop: {leg.get('exchange')} "
                          f"{leg.get('tokenIn','')[:10]}->{leg.get('tokenOut','')[:10]}")
        else:
            print(f"  ❌ KyberSwap: code={d.get('code')} {str(d.get('message'))[:60]}")
    except Exception as e:
        print(f"  ❌ KyberSwap: {type(e).__name__} {str(e)[:70]}")

    # 2. OpenOcean
    try:
        u = ("https://open-api.openocean.finance/v3/avax/quote?"
             + urllib.parse.urlencode({"inTokenAddress": WAVAX,
                                       "outTokenAddress": USDC,
                                       "amountDecimals": "0.744",
                                       "gasPrice": "1"}))
        d = json.loads(get(u))
        if d.get("code") == 200:
            print(f"  ✅ OpenOcean: {d['data'].get('outAmount')} USDC "
                  f"via {str(d['data'].get('dexes'))[:40]}")
        else:
            print(f"  ❌ OpenOcean: {str(d)[:90]}")
    except Exception as e:
        print(f"  ❌ OpenOcean: {type(e).__name__} {str(e)[:70]}")

    # 3. ParaSwap
    try:
        u = ("https://apiv5.paraswap.io/prices?"
             + urllib.parse.urlencode({"srcToken": WAVAX, "destToken": USDC,
                                       "amount": AMOUNT_IN, "srcDecimals": 18,
                                       "destDecimals": 6, "side": "SELL",
                                       "network": 43114}))
        d = json.loads(get(u))
        p = d.get("priceRoute") or {}
        if p:
            print(f"  ✅ ParaSwap: {int(p['destAmount'])/1e6:.4f} USDC "
                  f"via {str(p.get('exchange'))[:40]} (gas {p.get('gasCost')})")
        else:
            print(f"  ❌ ParaSwap: {str(d)[:90]}")
    except Exception as e:
        print(f"  ❌ ParaSwap: {type(e).__name__} {str(e)[:70]}")

    # 4. 1inch (public tier)
    try:
        u = ("https://api.1inch.dev/swap/v6.0/43114/quote?"
             + urllib.parse.urlencode({"src": WAVAX, "dst": USDC,
                                       "amount": AMOUNT_IN}))
        d = json.loads(get(u))
        if d.get("dstAmount"):
            print(f"  ✅ 1inch: {int(d['dstAmount'])/1e6:.4f} USDC")
        else:
            print(f"  ❌ 1inch: {str(d)[:90]}")
    except Exception as e:
        print(f"  ❌ 1inch: {type(e).__name__} {str(e)[:70]}")


if __name__ == "__main__":
    main()
