#!/usr/bin/env python3
"""swap_readiness.py — WHY a tilt swap fails, and whether it is LAG or a REAL divergence.

Jordan, 2026-09-26: "sometimes I don't know if it's because of the lagging rpc or if they're
just things we got to fix within our own book. But sometimes me and age are not synced up."

That is two different questions that used to look identical:
  (a) a LAGGING NODE — the chain has the new value, this RPC has not applied it yet. Nothing
      is wrong; re-reading later fixes it. Acting on this is how a swap gets double-sent.
  (b) a REAL DIVERGENCE — the value genuinely is not what we need (an allowance never granted,
      a balance actually spent). No amount of waiting fixes it; it needs an action.

The cure is the same one this fleet uses everywhere else: never conclude from ONE reading.
Read the same facts from several INDEPENDENT providers and compare. If they disagree, it is
LAG and we must WAIT. If they agree, the number is real and we may ACT.

Read-only. No wallet, no key, no transaction path.
"""
import json
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/root/.hermes/profiles/gentech-treasury/scripts")

RPCS = [
    ("publicnode", "https://avalanche-c-chain-rpc.publicnode.com"),
    ("avax.network", "https://api.avax.network/ext/bc/C/rpc"),
    ("drpc", "https://avalanche.drpc.org"),
    ("1rpc", "https://1rpc.io/avax/c"),
]

WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC  = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
ROUTER = "0x18556DA13313f3532c54711497A8FedAC273220E"

TENANTS = {
    "jordan":  "0x572ABd6461BED2258615E6b99c585Ab7c5d05037",
    "dadrian": "0x6c69F8FD6C23A5b6b3ccbCB0d638AA6D527812Fe",
}

HDR = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}


def rpc(url, method, params=None, timeout=20):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method,
                       "params": params or []}).encode()
    req = urllib.request.Request(url, data=body, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def pad(a):
    return "0" * 24 + a[2:].lower()


def read_all(wallet):
    """(balances, allowances, head) from every provider that answers."""
    out = {}
    for name, url in RPCS:
        try:
            row = {}
            row["head"] = int(rpc(url, "eth_blockNumber")["result"], 16)
            for tok, sym, dec in ((WAVAX, "WAVAX", 18), (USDC, "USDC", 6)):
                b = rpc(url, "eth_call", [{"to": tok, "data": "0x70a08231" + pad(wallet)},
                                          "latest"])["result"]
                row["bal_" + sym] = int(b, 16) / 10 ** dec
                a = rpc(url, "eth_call",
                        [{"to": tok, "data": "0xdd62ed3e" + pad(wallet) + pad(ROUTER)},
                         "latest"])["result"]
                row["allow_" + sym] = int(a, 16) / 10 ** dec
            row["nonce"] = int(rpc(url, "eth_getTransactionCount",
                                   [wallet, "latest"])["result"], 16)
            row["ok"] = True
            out[name] = row
        except Exception as e:
            out[name] = {"ok": False, "err": f"{type(e).__name__}"}
    return out


def verdict(vals):
    """Given {provider: value}, decide LAG vs REAL vs UNREADABLE.

    Returns (status, payload): status in AGREE/ DISAGREE / UNREADABLE.
    AGREE -> payload is the single agreed float. DISAGREE -> payload is a dict.
    """
    good = {k: v for k, v in vals.items() if v is not None}
    if not good:
        return "UNREADABLE", None
    uniq = set(round(v, 6) for v in good.values())
    if len(uniq) == 1:
        return "AGREE", float(list(good.values())[0])
    return "DISAGREE", good


def main():
    print("=" * 96)
    print("  SWAP READINESS — is a failing tilt swap LAG, or a REAL divergence?")
    print("=" * 96)
    for tenant, wallet in TENANTS.items():
        print(f"\n═══ {tenant.upper()}  {wallet}")
        d = read_all(wallet)
        heads = [v["head"] for v in d.values() if v.get("ok")]
        if heads:
            print(f"  block height : min {min(heads)}  max {max(heads)}  "
                  f"spread {max(heads)-min(heads)} blocks across {len(heads)} providers")
        for metric, label in (("allow_USDC", "USDC allowance -> LBRouter"),
                              ("allow_WAVAX", "WAVAX allowance -> LBRouter"),
                              ("bal_USDC", "USDC balance"),
                              ("bal_WAVAX", "WAVAX balance")):
            vals = {k: v.get(metric) for k, v in d.items() if v.get("ok")}
            st, val = verdict(vals)
            if st == "AGREE" and isinstance(val, float):
                mark = "✅" if val > 0 else "⛔"
                print(f"  {mark} {label:30} {val:>16,.6f}   AGREED on all "
                      f"{len(vals)} providers → REAL")
            elif st == "DISAGREE" and isinstance(val, dict):
                spread = " | ".join(f"{k}={v:,.6f}" for k, v in sorted(val.items()))
                print(f"  ⚠️  {label:30} DISAGREED (LAG, do not act): {spread}")
            else:
                print(f"  ❓ {label:30} UNREADABLE — no provider answered")
        # the actionable conclusion
        au = [v.get("allow_USDC") for v in d.values() if v.get("ok")]
        ab = [v.get("bal_USDC") for v in d.values() if v.get("ok")]
        if au and ab and len(set(round(x, 6) for x in au)) == 1:
            a0, b0 = au[0], ab[0]
            if b0 > 1.0 and a0 < b0 * 0.5:
                print(f"\n  ➜ REAL DIVERGENCE: {b0:,.2f} USDC sits in the wallet but only "
                      f"{a0:,.6f} is approved to the router.")
                print(f"    A USDC->WAVAX tilt swap CANNOT execute. This is not lag — it needs "
                      f"an approve.")
            elif b0 > 1.0:
                print(f"\n  ➜ READY: {b0:,.2f} USDC with {a0:,.2f} approved — a USDC->WAVAX "
                      f"swap can execute.")
    print("\n" + "=" * 96)
    print("  RULE: one provider is never evidence. AGREE = real and actionable;")
    print("        DISAGREE = lag, wait and re-read. UNREADABLE is not a zero.")
    print("=" * 96)


if __name__ == "__main__":
    main()
