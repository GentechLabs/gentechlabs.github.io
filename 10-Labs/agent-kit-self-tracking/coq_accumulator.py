#!/usr/bin/env python3
"""COQ accumulator — dip-aware buy & hold (Jordan's design).

Jordan (Sep 12 2026): "you'll make the purchase at the right time... because
you'll always be looking at the markets and be able to catch the pullbacks."

So this is NOT a blind weekly buy. It holds a WEEKLY BUDGET and spends it when
the market gives a good entry — with a fallback so it can never silently skip
forever.

Design:
  Budget      $5/week, resets each ISO week. Never exceeds it.
  Runs        daily. Scores every day; only fires when there is a reason to.
  Buy when    COQ is down >= DIP_PCT over 24h (a pullback), OR
              it is the last day of the week and budget is unspent (fallback).
  Capital     idle WAVAX + native AVAX above the gas reserve. AVAX is wrapped
              to WAVAX as needed. NEVER touches farm position #3479882.

Silence doctrine: quiet unless it bought, or unless something changed that
Jordan needs to know. The unfunded reminder re-arms on a slow cycle so a
never-funded leg cannot fail silently.

Gas floor (Jordan's rule, 2026-09-25): the reserve is computed by gas_reserve.py from the LIVE gas
price and the LIVE AVAX price (max of one full exit+re-entry cycle and $0.10), and THIS path may
only spend what is ABOVE it — it is the one path here that can eat the reserve, because it WRAPS
NATIVE AVAX into WAVAX to fund a buy.
"""
import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

from web3 import Web3
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)
import steward_identity as _SI   # ONE signing path: asserts the tenant + decrypts

# Shared rotating providers. Single hardcoded host = one 1015 and the accumulator cannot read
# gas price / balances at all. FAIL CLOSED: this script signs, so it must never act on a
# degraded read.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avax_rpc import connect as _rpc_connect, RpcUnavailable
CHAIN_ID = 43114
COQ = "0x420FcA0121DC28039145009570975747295f2329"
WAVAX = "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"
USDC = "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
WALLET = _sw_wallet()
STEWARD_KEY = _sw_keypath()   # canonical signer
KYBER = "https://aggregator-api.kyberswap.com/avalanche/api/v1"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     ".coq-accumulator-state.json")
LOG = "/root/vaults/gentech/01-HANDOFFS/treasury-to-gentech/coq-dca-log.md"
COQ_PAIR = "0x41aB86EEcBd110a82cA602D032a461f453066F1E"  # deepest COQ/WAVAX

WEEKLY_BUDGET_USD = 5.0
DIP_PCT = 3.0              # buy a pullback this deep (24h)
# GAS_FLOOR_USD = 0.20 is RETIRED (2026-09-25): it was this file's own invented floor, competing
# with the real one. The reserve comes from gas_reserve.py now (LIVE gas price, LIVE AVAX price,
# max of one exit+re-entry cycle and $0.10) — one implementation, no second number.
MIN_BUY_USD = 1.0          # don't bother with dust buys
UNFUNDED_REPORT_DAYS = 30
WAVAX_USD_FALLBACK = 7.44

QUIET = False


def say(*a, **k):
    if not QUIET:
        print(*a, **k)


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
          "stateMutability": "nonpayable", "type": "function"},
         {"constant": False, "inputs": [], "name": "deposit",
          "outputs": [], "stateMutability": "payable", "type": "function"}]

try:
    w3 = _rpc_connect(timeout=30)
except RpcUnavailable as _e:
    print(f"❌ COQ accumulator ABORTED — no AVAX RPC provider: {_e}")
    raise SystemExit(3)


def iso_week():
    y, w, _ = time.strftime("%Y-%W-%w").split("-")
    return f"{y}-W{w}"


def load_state():
    try:
        with open(STATE) as f:
            s = json.load(f)
    except Exception:
        s = {}
    s.setdefault("week_spent", {})
    s.setdefault("buys", [])
    s.setdefault("total_usd", 0.0)
    s.setdefault("total_coq", 0.0)
    s.setdefault("last_report", None)
    return s


def save_state(s):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w") as f:
        json.dump(s, f, indent=2)


def coq_market():
    """Live COQ price + 24h change from the deepest pair."""
    u = f"https://api.dexscreener.com/latest/dex/pairs/avalanche/{COQ_PAIR}"
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
    p = (d.get("pairs") or [{}])[0]
    return (float(p.get("priceUsd") or 0),
            float((p.get("priceChange") or {}).get("h24") or 0))


def wavax_price():
    try:
        u = f"{KYBER}/routes?" + urllib.parse.urlencode(
            {"tokenIn": WAVAX, "tokenOut": USDC, "amountIn": str(10 ** 18)})
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode())
        return int(d["data"]["routeSummary"]["amountOut"]) / 1e6
    except Exception:
        return WAVAX_USD_FALLBACK


def balances():
    wc = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20)
    wav = wc.functions.balanceOf(Web3.to_checksum_address(WALLET)).call() / 1e18
    avax = w3.eth.get_balance(Web3.to_checksum_address(WALLET)) / 1e18
    return wav, avax


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
                       "source": "steward-coq-accumulator"}).encode()
    req = urllib.request.Request(f"{KYBER}/route/build", data=body,
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "Mozilla/5.0"})
    return json.loads(urllib.request.urlopen(req, timeout=25).read().decode())["data"]


def signer():
    if not os.path.exists(STEWARD_KEY):
        return None
    try:
        return _SI.signer()
    except Exception:
        return None


_NONCE_STATE = {"next": None}


def _next_nonce():
    """Allocate the next nonce for THIS process, incrementing locally.

    PERMANENT FIX (2026-09-24, Permanent-Fix Rule). Root cause of the recurring
    `Web3RPCError -32000 'replacement transaction underpriced'` on the daily fire:

    the script sent up to THREE transactions (wrap -> approve -> swap) and each one called
    `w3.eth.get_transaction_count(WALLET)` — which defaults to the **LATEST** block, not
    `pending`. Between two sends the previous tx can still be unmined, so the second read returns
    the SAME nonce the first tx already used. Re-sending a nonce that is already in the mempool is
    exactly what the node rejects as a "replacement" — and it rejects it unless the gas price beats
    the tx it is trying to displace, which our fixed 1.3x does not guarantee.

    Measured 2026-09-24: the wallet's `latest` and `pending` counts were EQUAL (1329 == 1329), so
    there was NO stuck tx — the "still-pending tx holding the nonce" reading was wrong. The defect
    is self-inflicted, inside the script, and it recurs whenever two sends land close together.

    A re-read cannot fix this (the chain genuinely does not know yet). The fix is to stop re-reading:
    take the count ONCE per process and increment locally, so two sends in one run can never collide.
    """
    if _NONCE_STATE["next"] is None:
        _NONCE_STATE["next"] = w3.eth.get_transaction_count(WALLET, "pending")
    n = _NONCE_STATE["next"]
    _NONCE_STATE["next"] = n + 1
    return n


def selfcheck_nonce_allocator():
    """Regression check (Permanent-Fix Rule step 3): prove the allocator INCREMENTS.

    The defect this guards is 'three sends, one nonce'. If someone reverts to
    `w3.eth.get_transaction_count(WALLET)` per send, this check fails loudly instead of the
    failure reappearing as an opaque node error during a live buy.
    """
    _NONCE_STATE["next"] = None
    a = _next_nonce(); b = _next_nonce(); c = _next_nonce()
    if not (a + 1 == b and b + 1 == c):
        raise SystemExit(f"❌ nonce allocator NOT incrementing ({a},{b},{c}) — "
                         f"two sends would collide and the node will reject the second")
    return a, b, c


def wrap_avax(acct, amount_wei, gas_price):
    wc = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20)
    tx = wc.functions.deposit().build_transaction(
        {"from": WALLET, "value": amount_wei,
         "nonce": _next_nonce(),
         "gas": 60000, "gasPrice": int(gas_price * 1.3), "chainId": CHAIN_ID})
    h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
    r = w3.eth.wait_for_transaction_receipt(h, timeout=180)
    return r["status"] == 1, h.hex()


def log_buy(row):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    exists = os.path.exists(LOG)
    with open(LOG, "a") as f:
        if not exists:
            f.write("# COQ Accumulator — dip-aware buy & hold\n\n")
            f.write("| date | usd | COQ | price | why | tx |\n")
            f.write("|---|---|---|---|---|---|\n")
        f.write(row + "\n")


def chain_healthy():
    """Is the chain safe to pull a position apart on?

    A degraded chain is the ONE condition that makes an LP-sourced buy worse than no buy:
    the exit can land while the redeploy fails, leaving the whole position idle -- far worse
    than missing a $5 purchase. Observed 2026-09-22 during the AVAX upgrade: a 12,125-block
    spread between three public nodes, and a redeploy leg whose receipt never arrived.
    Returns (healthy: bool, why: str).
    """
    import urllib.request, json as _j
    urls = ["https://avalanche-c-chain-rpc.publicnode.com",
            "https://avalanche.drpc.org",
            "https://1rpc.io/avax/c"]
    heights = []
    for u in urls:
        try:
            from web3 import Web3 as _W3
            _w = _W3(_W3.HTTPProvider(u, request_kwargs={"timeout": 20}))
            heights.append(_w.eth.block_number)
        except Exception:
            pass
    if len(heights) < 2:
        return False, f"only {len(heights)} of 3 nodes reachable -- cannot confirm health"
    spread = max(heights) - min(heights)
    # Avalanche produces ~1 block/sec. A few blocks of skew is normal; thousands is not.
    if spread > 50:
        return False, f"{spread:,} blocks of spread across {len(heights)} nodes (degraded)"
    return True, f"{spread} blocks of spread across {len(heights)} nodes"


def main():
    global QUIET
    ap = argparse.ArgumentParser()
    ap.add_argument("--usd", type=float, default=WEEKLY_BUDGET_USD)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="buy now regardless of dip/fallback logic")
    ap.add_argument("--source", choices=["wallet", "lp"], default="wallet",
                    help="where the buy is funded from. 'wallet' = idle capital only "
                         "(default, never touches the farm). 'lp' = if idle capital is short, "
                         "take the buy out of the farm (exit -> buy -> redeploy).")
    args = ap.parse_args()
    QUIET = args.quiet

    st = load_state()
    wk = iso_week()
    spent = st["week_spent"].get(wk, 0.0)
    remaining = max(0.0, args.usd - spent)

    px_wavax = wavax_price()
    coq_px, coq_chg = coq_market()
    wav, avax = balances()

    say(f"COQ ACCUMULATOR — budget ${args.usd:.2f}/wk · this week spent ${spent:.2f}")
    say(f"  wallet {WALLET}")
    say(f"  idle WAVAX {wav:.6f} (~${wav*px_wavax:.2f}) | AVAX {avax:.6f}")
    say(f"  COQ ${coq_px:.10f} (24h {coq_chg:+.2f}%) · WAVAX/USD ${px_wavax:.4f}")

    if remaining < MIN_BUY_USD:
        say(f"  budget exhausted this week (${spent:.2f} of ${args.usd:.2f})")
        return 0

    # ── why buy? dip, or end-of-week fallback ──────────────────────────────
    is_dip = coq_chg <= -DIP_PCT
    is_week_end = time.strftime("%w") == "0"      # Sunday
    reason = None
    if args.force:
        reason = "manual force"
    elif is_dip:
        reason = f"dip: COQ {coq_chg:+.2f}% in 24h"
    elif is_week_end and remaining > 0:
        reason = "week-end fallback: budget unspent, no dip came"

    if not reason:
        say(f"  no buy: 24h {coq_chg:+.2f}% (need <= -{DIP_PCT:.1f}% or week-end)")
        return 0
    say(f"  trigger: {reason}")

    # ── fundable? THE GAS RESERVE IS THE FLOOR (Jordan, 2026-09-25) ───────────────────────────
    # This used to keep `gas_cost + GAS_FLOOR_USD ($0.20)` of the wallet's own terms — a SECOND
    # floor, in a second file, priced off its own gas constant, with no idea what the rest of the
    # treasury considered its reserve. The reserve now comes from gas_reserve.py (ONE
    # implementation, LIVE gas price, LIVE AVAX price) and this path may only spend what is ABOVE
    # it: the accumulator WRAPS NATIVE AVAX into WAVAX to fund a buy, and that is the one way a
    # buy can spend the gas reserve itself.
    # FAIL CLOSED: an unmeasurable floor is not spendable. The buy is a $5 discretionary purchase
    # — skipping it costs nothing; spending the reserve costs the NEXT repair (the 2026-09-25
    # stranding, where a wallet with 0.000025 AVAX could not pay for its own re-deploy).
    try:
        import gas_reserve as _GR
        _ri = _GR.reserve_info(w3=w3, balance_avax=avax, avax_usd=px_wavax)
        if not _ri.get("measured"):
            raise RuntimeError(_ri.get("unmeasured_reason") or "unmeasured")
        reserve_avax = _ri["reserve_avax"]
        # The tx gas price comes from the SAME live read the floor used, not a second one: two
        # gas reads for one action is how two numbers start disagreeing (bug class #10).
        gas_price = int(_ri["gas_price_wei"])
        say(f"  {_GR.floor_line(_ri)}")
    except Exception as _e:
        print(f"\nREPORT:⚠️  COQ accumulator: the gas floor is UNMEASURABLE "
              f"({type(_e).__name__}: {_e}) — NOT buying. A reserve that cannot be sized must not "
              f"be spent, and the wrap step is the one way this path can spend it.")
        return 0

    usable_wavax = wav
    usable_avax = max(0.0, avax - reserve_avax)
    total_usable_usd = (usable_wavax + usable_avax) * px_wavax
    deploy_usd = min(remaining, total_usable_usd)

    say(f"  usable: {usable_wavax:.6f} WAVAX + {usable_avax:.6f} AVAX "
        f"= ${total_usable_usd:.2f} → deploy ${deploy_usd:.2f}  "
        f"(reserve {reserve_avax:.6f} AVAX is NOT spendable)")

    if deploy_usd < MIN_BUY_USD:
        # ── SELF-FUNDING: pull the shortfall from the farm instead of giving up ───────
        # Structural bug this fixes: the rail needs IDLE capital, but the watchdog deploys
        # 100% of it -- so idle WAVAX is ~0 forever and this rail could NEVER buy. It
        # reported "not funded" every day for 30 days while the treasury was fully invested.
        # Jordan's rule is no idle capital, so the fix is not to reserve cash: it is to
        # TAKE the buy out of the farm when the signal actually fires.
        # Jordan, 2026-09-22: "put $5 into COQ and then the rest of the money can go right
        # back into my pool."
        # Guards: only on a REAL trigger, only on a HEALTHY chain, and never without
        # --execute. On a degraded chain the exit can land while the redeploy fails, which
        # would leave the whole position idle -- strictly worse than missing a $5 buy.
        shortfall = max(0.0, min(remaining, WEEKLY_BUDGET_USD) - total_usable_usd)
        if args.source == "lp" and shortfall >= MIN_BUY_USD:
            healthy, why = chain_healthy()
            say(f"  idle capital short by ${shortfall:.2f} — LP-sourced buy requested")
            say(f"  chain health: {'✅ ' + why if healthy else '⛔ ' + why}")
            if not healthy:
                # LOUD, not `say()`: with the cron's --quiet this refusal used to be silent, so
                # a skipped buy looked exactly like a healthy no-buy.
                print(f"\nREPORT:⛔ COQ buy SKIPPED — chain degraded ({why}). "
                      f"The $5 buy needs a healthy chain; it will retry tomorrow.")
                return 0
            say("  plan: withdraw position → buy COQ → redeploy the remainder")
            # ── THE RESERVE THIS SEQUENCE MUST LEAVE BEHIND (Jordan, 2026-09-25) ────────────────
            # exit -> buy -> redeploy spends gas three times and then re-deploys the remainder, so
            # it is the path with the most opportunities to eat the gas reserve. The requirement is
            # STATED HERE, with LIVE numbers, for whoever implements it: the redeploy must leave
            # `reserve_avax` (computed above from the live gas price) untouched. This is the honest
            # limit of the enforcement — see the stub note below: there is nothing to gate yet,
            # because this branch does not move capital.
            say(f"  reserve  : {reserve_avax:.6f} AVAX ({_ri['floor_cycles']} cycle(s) / "
                f"${_ri['floor_usd']:.2f} @ {_ri['gas_price_navax']:.4f} nAVAX live) must remain "
                f"untouched by the redeploy")
            # ── THIS RAIL CANNOT BUY: SAY SO OUT LOUD, EVERY RUN (fixed 2026-09-25) ────────────
            # This branch IS the whole remediation for "the rail could never buy" -- and it is a
            # STUB. Even with --execute it prints and returns 0: nothing is withdrawn, nothing is
            # bought, nothing is redeployed. There is no by-hand route either -- the old message
            # named an exercise ("until it has been exercised once by hand") for which no command
            # exists -- so exit->buy->redeploy has never run and cannot run.
            #
            # And it was INVISIBLE: the cron calls this as `--execute --quiet --source lp`, every
            # line in this branch was `say()`, and --quiet silences say(). The daily run produced
            # ZERO output, so a dead money rail read as a healthy one -- this treasury's dominant
            # bug class, and why the $5/week COQ budget could sit unspent indefinitely.
            #
            # The report goes ABOVE the dry-run gate on purpose: the "plan" line directly above
            # prints a sequence that cannot run, so the correction has to be attached to the plan
            # in EVERY mode, not only when --execute happens to be passed.
            #
            # An audit cannot ship a money-moving path, so the honest fix is to make the dead rail
            # LOUD and PERSISTENT: report it unconditionally, record its age in state, and name the
            # smallest thing that would fix it.
            _now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            _mark = st.setdefault("lp_rail", {})
            _mark.setdefault("first_seen", _now)
            _mark["last_seen"] = _now
            _mark["runs"] = int(_mark.get("runs") or 0) + 1
            _mark["last_shortfall_usd"] = round(shortfall, 2)
            _mark["reason"] = ("exit->buy->redeploy not implemented: the LP-sourced path is a stub "
                               "that returns rc=0 without moving capital")
            # The floor's live numbers are recorded with the marker: when this branch is
            # implemented, the requirement it must satisfy is already written down with the values
            # that were true when the gap was measured.
            _mark["gas_reserve_avax"] = round(reserve_avax, 8)
            _mark["gas_floor_source"] = ("gas_reserve.py — live gas price, max(one exit+re-entry "
                                         "cycle, $0.10)")
            save_state(st)
            print(f"\nREPORT:⚠️  COQ LP-SOURCED BUY CANNOT RUN — the rail is a STUB. "
                  f"idle capital is short by ${shortfall:.2f}; this has been seen {_mark['runs']}x "
                  f"since {_mark['first_seen']}. The wallet path needs idle capital that the "
                  f"no-idle-capital rule never leaves, and the LP path is not implemented, so the "
                  f"accumulator CANNOT BUY. Smallest fix: implement exit→buy→redeploy behind a "
                  f"proven harness, or fund the wallet from outside.")
            if not args.execute:
                say("  [dry-run] would withdraw/buy/redeploy. Re-run with --execute.")
                return 0
            return 0
        msg = (f"⏳ COQ accumulator not funded: usable "
               f"${total_usable_usd:.2f}, need >= ${MIN_BUY_USD:.2f} "
               f"(week budget ${remaining:.2f} left). Send AVAX (C-Chain) to "
               f"{WALLET}.")
        say(msg)
        today = time.strftime("%Y-%m-%d")
        last = st.get("last_report")
        due = True
        if last:
            try:
                age = (time.mktime(time.strptime(today, "%Y-%m-%d"))
                       - time.mktime(time.strptime(last, "%Y-%m-%d"))) / 86400
                due = age >= UNFUNDED_REPORT_DAYS
            except Exception:
                due = True
        if due:
            st["last_report"] = today
            save_state(st)
            print("\nREPORT:" + msg)
        return 0

    if not args.execute:
        say("  [dry-run] would wrap/approve/swap. Re-run with --execute.")
        return 0

    acct = signer()
    if acct is None:
        say(f"  ❌ no signing key at {STEWARD_KEY}")
        return 0

    # ── wrap native AVAX if WAVAX is short ─────────────────────────────────
    # THE RESERVE IS SPENT HERE OR NOWHERE: `shortfall` is capped at `usable_avax`, which is the
    # wallet's AVAX MINUS the reserve computed above. So the wrap can never reach into the floor
    # (Jordan, 2026-09-25: "you never know when you'll need to make a swap or need to redeploy").
    need_wavax = deploy_usd / px_wavax
    if usable_wavax < need_wavax:
        shortfall = min(usable_avax, need_wavax - usable_wavax)
        say(f"  wrapping {shortfall:.6f} AVAX -> WAVAX   (reserve {reserve_avax:.6f} AVAX left "
            f"untouched)")
        ok, h = wrap_avax(acct, int(shortfall * 1e18), gas_price)
        say(f"    {'✅' if ok else '❌'} wrap {h}")
        if not ok:
            return 0
        wav, _ = balances()

    amt_in = int(min(need_wavax, wav) * 1e18)
    summary = quote_coq(amt_in)
    out_coq = int(summary["amountOut"]) / 1e18
    say(f"  quote: {amt_in/1e18:.6f} WAVAX -> {out_coq:,.0f} COQ")

    built = build_swap(summary)
    router = built["routerAddress"]
    wc = w3.eth.contract(address=Web3.to_checksum_address(WAVAX), abi=ERC20)
    allow = wc.functions.allowance(Web3.to_checksum_address(WALLET),
                                   Web3.to_checksum_address(router)).call()
    gp = w3.eth.gas_price
    # SECOND DEFECT FOUND 2026-09-24 — the "bounded approval" fix could never fire.
    # It was gated on `allow < amt_in`, but the FIRST COQ swap (before the bounded fix existed)
    # granted an UNLIMITED WAVAX allowance — measured live on-chain: allowance == 2**256-1. An
    # infinite allowance is never < amt_in, so the bounded branch was dead code and the script's
    # stated security posture was NOT in effect. A check that cannot fire is as unreadable as one
    # that cannot fail. Re-approve whenever the standing grant is BOTH insufficient AND oversized,
    # so the bounded amount is actually enforced and the redundant exposure is removed.
    SANE_MAX = int(amt_in * 4 * 8)      # anything far above a few weeks' needs is over-granted
    if allow < amt_in or allow > SANE_MAX:
        # BOUNDED approval (self-audit fix, Sep 12 2026). An unlimited grant to
        # a swap router is a standing permission we never actually need — we buy
        # ~$5 a week. Approve a few weeks' worth instead, so a compromised
        # router can only ever reach a small, self-limiting amount.
        approve_amt = int(amt_in * 4)
        if allow == 2 ** 256 - 1 or allow > SANE_MAX:
            say(f"  standing allowance is OVER-GRANTED ({'UNLIMITED' if allow == 2**256-1 else allow/1e18:.2f}) "
                f"-> re-approving to the bounded {approve_amt/1e18:.6f}")
        say(f"  approving WAVAX -> {router} (bounded {approve_amt/1e18:.6f})")
        tx = wc.functions.approve(Web3.to_checksum_address(router), approve_amt) \
            .build_transaction({"from": WALLET,
                                "nonce": _next_nonce(),
                                "gas": 60000, "gasPrice": int(gp * 1.3),
                                "chainId": CHAIN_ID})
        h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
        r = w3.eth.wait_for_transaction_receipt(h, timeout=180)
        say(f"    {'✅' if r['status']==1 else '❌'} approve {h.hex()}")

    tx = {"from": WALLET, "to": Web3.to_checksum_address(router),
          "data": built["data"],
          "value": int(built.get("transactionValue") or 0),
          "nonce": _next_nonce(),
          "gas": int(built.get("gas") or 500000) + 100000,
          "gasPrice": int(gp * 1.3), "chainId": CHAIN_ID}
    h = w3.eth.send_raw_transaction(acct.sign_transaction(tx).raw_transaction)
    r = w3.eth.wait_for_transaction_receipt(h, timeout=240)
    say(f"  {'✅' if r['status']==1 else '❌'} swap {h.hex()} status={r['status']}")
    if r["status"] != 1:
        say("  ❌ swap reverted — nothing recorded")
        return 0

    date = time.strftime("%Y-%m-%d")
    st["week_spent"][wk] = spent + deploy_usd
    st["buys"].append({"date": date, "usd": deploy_usd, "coq": out_coq,
                       "price": coq_px, "why": reason, "tx": h.hex()})
    st["total_usd"] += deploy_usd
    st["total_coq"] += out_coq
    st["last_report"] = None
    save_state(st)

    log_buy(f"| {date} | ${deploy_usd:.2f} | {out_coq:,.0f} | ${coq_px:.10f} "
            f"| {reason} | `{h.hex()[:18]}…` |")
    print(f"\nREPORT:✅ COQ ${deploy_usd:.2f} → {out_coq:,.0f} COQ @ "
          f"${coq_px:.10f} ({reason}). Week: ${spent+deploy_usd:.2f}/"
          f"${args.usd:.2f}. tx {h.hex()[:18]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
