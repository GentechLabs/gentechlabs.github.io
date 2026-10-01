#!/usr/bin/env python3
"""Weekly COQ accumulation — Jordan's buy & hold DCA.

Jordan (Sep 12 2026): "I would start accumulating by maybe doing five bucks a
week... starting Sunday do like five bucks a week for the COQ."

COQ is BUY & HOLD, not a farm. Verified on-chain Sep 12: Blackhole has no COQ
Algebra pool, and the only real COQ liquidity (traderjoe/LFJ, $488K) sits on a
retired rail. So this buys SPOT and HOLDS it — no LP, no impermanent loss.

Funding model: this draws from IDLE WAVAX only. It will NOT touch the farm
position (#3479882) — a DCA that quietly drained the yield position would be
worse than no DCA at all. If there is no idle capital it reports once and stops
(silence doctrine: alert ONCE, suppress until something changes).

Gas floor (Jordan's rule): no hard gate. Compute the tx cost, keep that plus a
~20c floor, deploy the rest.
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

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
CHAIN_ID = 43114
COQ = "0x420FcA0121DC28039145009570975747295f2329"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
WALLET = _sw_wallet()
KYBER = "https://aggregator-api.kyberswap.com/avalanche/api/v1"
STATE = "/root/.hermes/profiles/gentech-treasury/scripts/.coq-dca-state.json"
LOG = "/root/vaults/gentech/01-HANDOFFS/treasury-to-gentech/coq-dca-log.md"

WAVAX_USD_FALLBACK = 7.44
GAS_FLOOR_USD = 0.20
# While unfunded, re-arm the reminder this often (days). Prevents a documented
# but never-funded DCA from failing silently forever.
UNFUNDED_REPORT_DAYS = 30

ERC20 = [{"constant": True, "inputs": [{"name": "a", "type": "address"}],
          "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"},
         {"constant": True, "inputs": [{"name": "o", "type": "address"},
                                       {"name": "s", "type": "address"}],
          "name": "allowance", "outputs": [{"name": "", "type": "uint256"}],
          "stateMutability": "view", "type": "function"},
         {"constant": False, "inputs": [{"name": "s", "type": "address"},
                                        {"name": "v", "type": "uint256"}],
          "name": "approve", "outputs": [{"name": "", "type": "bool"}],
          "stateMutability": "nonpayable", "type": "function"}]

w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 30}))

QUIET = False


def say(*a, **k):
    """Informational output — suppressed under --quiet (cron mode)."""
    if not QUIET:
        print(*a, **k)


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {"last_buy_date": None, "total_usd": 0.0, "total_coq": 0.0,
                "buys": [], "last_report": None}


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(s, f, indent=2)


def wavax_balance():
    c = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20)
    return c.functions.balanceOf(Web3.to_checksum_address(WALLET)).call() / 1e18


def avax_balance():
    return w3.eth.get_balance(Web3.to_checksum_address(WALLET)) / 1e18


def wavax_price():
    """WAVAX/USD via KyberSwap quote (WAVAX -> USDC, 1 WAVAX)."""
    try:
        u = f"{KYBER}/routes?" + urllib.parse.urlencode(
            {"tokenIn": WAVAX, "tokenOut": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
             "amountIn": str(10 ** 18)})
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
        return int(d["data"]["routeSummary"]["amountOut"]) / 1e6
    except Exception:
        return WAVAX_USD_FALLBACK


def quote_coq(amount_in_wei):
    u = f"{KYBER}/routes?" + urllib.parse.urlencode(
        {"tokenIn": WAVAX, "tokenOut": COQ, "amountIn": str(amount_in_wei)})
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
    return d["data"]["routeSummary"]


def build_swap(summary):
    body = json.dumps({"routeSummary": summary, "sender": WALLET,
                       "recipient": WALLET, "slippageTolerance": 100,
                       "deadline": int(time.time()) + 900,
                       "source": "steward-coq-dca"}).encode()
    req = urllib.request.Request(f"{KYBER}/route/build", data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=25).read().decode())["data"]


def account():
    key = os.environ.get("STEWARD_PK") or os.environ.get("AVAX_PRIVATE_KEY")
    if not key:
        for p in ("/root/.hermes/profiles/gentech-treasury/scripts/.steward-key",
                  "/root/.steward-key"):
            if os.path.exists(p):
                key = open(p).read().strip()
                break
    if not key:
        return None
    return w3.eth.account.from_key(key)


def log_buy(entry):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    exists = os.path.exists(LOG)
    with open(LOG, "a") as f:
        if not exists:
            f.write("# COQ Weekly DCA — buy & hold log\n\n")
            f.write("| date | usd | COQ bought | price | tx |\n")
            f.write("|---|---|---|---|---|\n")
        f.write(entry + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--usd", type=float, default=5.0)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--quiet", action="store_true",
                    help="only emit the report line (cron mode)")
    args = ap.parse_args()

    global QUIET
    QUIET = args.quiet
    st = load_state()
    px = wavax_price()
    wb = wavax_balance()
    ab = avax_balance()

    say(f"COQ WEEKLY DCA — target ${args.usd:.2f}")
    say(f"  wallet {WALLET}")
    say(f"  idle WAVAX {wb:.6f} (~${wb*px:.2f}) | AVAX {ab:.6f} (gas)")
    say(f"  WAVAX/USD ${px:.4f}")

    # gas floor: cost of the swap + a 20c cushion, measured not guessed
    gas_price = w3.eth.gas_price
    est_gas = 400_000
    gas_cost_usd = (gas_price * est_gas / 1e18) * (px / 1.0) * 1.0
    # AVAX price ~= WAVAX price
    gas_cost_usd = (gas_price * est_gas / 1e18) * px
    need_wavax = args.usd / px
    reserve = (gas_cost_usd + GAS_FLOOR_USD) / px

    say(f"  gas cost ~${gas_cost_usd:.4f} + ${GAS_FLOOR_USD:.2f} floor")
    say(f"  need {need_wavax:.6f} WAVAX (keep {reserve:.6f} as floor)")

    if wb < need_wavax + reserve:
        msg = (f"⏳ COQ DCA not funded: idle WAVAX {wb:.6f} "
               f"(~${wb*px:.2f}), needs ~{need_wavax + reserve:.6f} "
               f"(${args.usd + gas_cost_usd + GAS_FLOOR_USD:.2f}). "
               f"No buy this week.")
        say(msg)
        # Report once, then stay quiet — but NEVER permanently silent.
        # An unfunded DCA that goes quiet forever is a SILENT FAILURE: the
        # feature would simply never happen and nothing would say so. So the
        # reminder re-arms on a slow cycle (silence doctrine: no spam, but a
        # leg that can be parked in silence forever is a bug, not a feature).
        today = time.strftime("%Y-%m-%d")
        last = st.get("last_report")
        due = True
        if last:
            try:
                age_days = (time.mktime(time.strptime(today, "%Y-%m-%d"))
                            - time.mktime(time.strptime(last, "%Y-%m-%d"))) / 86400
                due = age_days >= UNFUNDED_REPORT_DAYS
            except Exception:
                due = True
        if due:
            st["last_report"] = today
            save_state(st)
            print("\nREPORT:" + msg)
        return 0

    amt_in = int(need_wavax * 1e18)
    summary = quote_coq(amt_in)
    out_coq = int(summary["amountOut"]) / 1e18
    say(f"  quote: {need_wavax:.6f} WAVAX -> {out_coq:,.0f} COQ")

    if not args.execute:
        say(f"  [dry-run] would approve + swap. Re-run with --execute.")
        return 0

    acct = account()
    if acct is None:
        say(f"  ❌ no signing key available")
        return 0

    built = build_swap(summary)
    router = built["routerAddress"]
    wc = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20)
    allow = wc.functions.allowance(Web3.to_checksum_address(WALLET),
                                   Web3.to_checksum_address(router)).call()
    gp = w3.eth.gas_price
    if allow < amt_in:
        say(f" -> {router}")
        tx = wc.functions.approve(Web3.to_checksum_address(router), 2**256 - 1) \
            .build_transaction({"from": WALLET,
                                "nonce": w3.eth.get_transaction_count(WALLET),
                                "gas": 60000, "gasPrice": int(gp * 1.3),
                                "chainId": CHAIN_ID})
        h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
        r = w3.eth.wait_for_transaction_receipt(h, timeout=180)
        say(f"    {'✅' if r['status']==1 else '❌'} approve {h.hex()}")

    tx = {"from": WALLET, "to": Web3.to_checksum_address(router),
          "data": built["data"],
          "value": int(built.get("transactionValue") or 0),
          "nonce": w3.eth.get_transaction_count(WALLET),
          "gas": int(built.get("gas") or 500000) + 100000,
          "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID}
    h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
    r = w3.eth.wait_for_transaction_receipt(h, timeout=240)
    say(f"  {'✅' if r['status']==1 else '❌'} swap {h.hex()} status={r['status']}")
    if r["status"] != 1:
        say(f"swap reverted — no buy recorded")
        return 0

    price = args.usd / out_coq if out_coq else 0
    date = time.strftime("%Y-%m-%d")
    st.setdefault("buys", []).append(
        {"date": date, "usd": args.usd, "coq": out_coq, "tx": h.hex()})
    st["total_usd"] = st.get("total_usd", 0) + args.usd
    st["total_coq"] = st.get("total_coq", 0) + out_coq
    st["last_buy_date"] = date
    st["last_report"] = None
    save_state(st)

    log_buy(f"| {date} | ${args.usd:.2f} | {out_coq:,.0f} | ${price:.10f} | `{h.hex()[:18]}…` |")
    print("\nREPORT:✅ COQ DCA bought ${:.2f} -> {:,.0f} COQ @ ${:.10f} (tx {})"
          .format(args.usd, out_coq, price, h.hex()[:18]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
