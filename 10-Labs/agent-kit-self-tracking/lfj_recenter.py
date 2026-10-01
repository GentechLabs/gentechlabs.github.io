#!/usr/bin/env python3
"""
lfj_recenter.py — LFJ Liquidity Book RE-CENTER / REBALANCE.

Closes the gap the audit found: the Position Watchdog correctly detects
"OUT of range" and then reaches for a Blackhole CL adapter, because no LFJ
rebalancer existed. This is that rebalancer.

SEQUENCE
  1. SETTLE   3 reads, highest settled activeId
  2. SCAN     find every bin we hold and whether price is inside our band
  3. DECIDE   bid (USDC below spot) / ask (WAVAX above spot) / hold
  4. WITHDRAW call lfj_exit.py --execute --yes
  5. RE-DEPLOY call lfj_bid_deploy.py --side <bid|ask> at the NEW price
  6. VERIFY   re-read the chain: position exists, band brackets spot

TWO-SAMPLE CONFIRMATION (Jordan, 2026-09-20): a single reading is not a trend.
We were burned twice calling a snapshot a mechanism. The --confirm flag requires
the trigger to persist across N consecutive samples before acting.

SIDES (verified against lfj-addliquidity-dryrun.py's working single-sided bid):
  BID = deltaIds NEGATIVE (below spot), tokenY (USDC), distributionX = 0
  ASK = deltaIds POSITIVE (above spot), tokenX (WAVAX), distributionY = 0

THE GAS FLOOR — A FLOOR THE NO-IDLE RULE MUST RESPECT (Jordan, 2026-09-25)
  Jordan, restating it for the third time: "keeping like maybe 10 cents of the natural whatever the
  coin is for gas... You still got to have a little bit of gas."
  The no-idle rule ("deploy the whole balance — idle capital is the failure mode") and the gas rule
  FIGHT, and no-idle won by default: the reserve got deployed into the LP and the wallet was left
  unable to pay for the very next swap or redeploy. That is the mechanical cause of a book stranded
  out of the pool.
  THE FIX, ENFORCED IN THREE PLACES IN THIS FILE:
    1. the COMPOSITION step sizes the swap and the deploy against `deployable` = the wallet MINUS
       the reserve, so the reserve is never converted into the book;
    2. the flat-book RE-ENTRY is gated: a wallet at/below the floor does not re-enter;
    3. the PRE-WITHDRAW precondition (the old 3.5M-gas check) now asks gas_reserve.py for BOTH the
       cycle budget and the floor, priced off ONE live gas read — one source of truth, no competing
       numbers. A refusal happens BEFORE the withdraw, because "refusing to begin is free;
       abandoning halfway is not."
  The reserve itself (max of one full exit+re-entry cycle and $0.10) is computed in ONE place:
  gas_reserve.py, from the LIVE gas price and the LIVE AVAX price. Nothing here hardcodes a gas
  price or a dollar floor.
  IT CANNOT BLOCK A RESCUE: the exit (lfj_exit.py) is not gated by the floor at all, and --rescue
  forces these paths through with a loud line saying the floor did not gate them. A genuine
  emergency — a book stranded out of the pool with the capital idle — is worse than a thin gas
  balance, and the reserve exists precisely to pay for repairing that.

  ── BUT "CANNOT BLOCK" MUST NOT MEAN "CANNOT CHECK" (fixed 2026-09-27) ──────────────────────
  MEASURED LIVE, and it stranded jordan's book for hours: the rescue bypassed the floor, so the
  cycle was allowed to WITHDRAW without proving it could afford to RE-DEPLOY. At 07:33 the exit
  went through, the re-deploy then hit

      Web3RPCError: insufficient funds for gas * price + value:
          balance 4584049209086108, tx cost 6620230615071780, overshot 2036181405985672

  and from then on the watchdog repeated the SAME rescue **every 10 minutes for over two hours**,
  each attempt withdrawing-and-failing against a shrinking balance (0.01389 -> 0.00298 AVAX,
  ~$0.12 of gas) while the capital sat in the wallet earning nothing — the exact state the rescue
  exists to prevent, held open BY the rescue.
  The two rules collided: "don't gate the exit" was written for a book that is ALREADY idle (a
  no-op withdraw — the capital is in the wallet either way, so skipping the check is free), but it
  was applied to a book that is DEPLOYED, where the withdraw is real, irreversible within the
  cycle, and only half of a two-step move. So the split is now explicit:
    * ALREADY IDLE (0 bins, or out of range with nothing deployed) -> the rescue proceeds unchecked.
      There is nothing to lose: the capital is not earning and no withdraw is needed.
    * DEPLOYED -> the rescue still runs, but it must PROVE the whole cycle is affordable, because
      a half-finished cycle is strictly worse than not starting: it converts a book that is
      earning little into one that is earning NOTHING, and it burns gas to do it.
"""

# ── wallet resolution (wired 2026-09-22) ────────────────────────────────────
# This file used to hardcode the operator's address. Fine for one person, catastrophic
# for a fleet: a second tenant running this script with their own config would still act
# on the FIRST tenant's wallet, and would do it silently. Resolve it instead - and prove
# it, because steward_identity.signer() refuses a key that does not match the resolved
# wallet, and asserts the tenant boundary before handing one back.
import os as _os, sys as _sys
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from steward_identity import wallet as _steward_wallet, tenant as _steward_tenant
import sys, os, json, time, argparse, subprocess, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from web3 import Web3

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

RPC  = _avax_url()
PAIR = Web3.to_checksum_address("0x864d4e5ee7318e97483db7eb0912e09f161516ea")
ME   = _steward_wallet()
PAIR_ABI = json.loads('[{"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},{"name":"getBinStep","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint16"}]},{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"},{"type":"uint256"}],"outputs":[{"type":"uint256"}]},{"name":"balanceOfBatch","type":"function","stateMutability":"view","inputs":[{"name":"accounts","type":"address[]"},{"name":"ids","type":"uint256[]"}],"outputs":[{"type":"uint256[]"}]}]')
# ── PER-TENANT STATE (fixed 2026-09-22) ───────────────────────────────────────────────────────
# This used to be a single global file, `.steward-recenter-state.json`. With more than one tenant
# in the fleet that is not a cosmetic wart, it is a starvation bug: the file holds BOTH the
# two-sample confirmation streak AND the last-action timestamp (the cooldown).
#
#   * The streak is an AND across tenants — whoever runs first writes their own value, so an
#     in-range tenant writes out_streak=0 and wipes an out-of-range tenant's count. With Jordan
#     enumerated first in the watchdog, Dadrian could never exceed 1/2 and therefore NEVER ACTED.
#     His position sat 24+ bins out of range earning zero while every run printed a healthy 1/2.
#   * The cooldown was shared too, so one tenant's re-center could silence another's.
#
# A per-tenant file makes each tenant's confirmation and cooldown its own. The tenant name comes
# from steward_identity, the same resolver the signing path uses — not from a hardcoded list.
STATE = os.path.join(HERE, f".steward-recenter-state-{_steward_tenant()}.json")


def settled_active(c):
    """Highest of 3 reads — a lagging node under-reports, and an under-reported
    activeId looks exactly like 'we are out of range'."""
    r = []
    for _ in range(3):
        try: r.append(c.functions.getActiveId().call())
        except Exception: pass
        time.sleep(2)
    return max(r) if r else None


def scan(c, active, depth=400):
    """(ids, tot) — the bins this wallet holds around `active`, and their total balance.

    ── ONE CALL, NOT 801 (fixed 2026-09-27) ───────────────────────────────────────────────────
    This used to issue one `balanceOf` per candidate bin — up to 801 SEQUENTIAL RPC calls at the
    default depth. That is slow enough to look like a hung run, and a single rate-limited or
    timed-out call silently dropped a bin from the result. That matters more now than it used to:
    the count returned here is what sizes the withdraw's gas budget, so a truncated scan reads as
    "we hold fewer bins than we do" and under-budgets the very transaction the gate is protecting.

    ERC-1155 `balanceOfBatch` asks the identical question in ONE call. The per-bin loop is kept
    ONLY as a fallback for a pair that does not expose the batch read, so the function can never
    return an empty book merely because a batch call failed.
    """
    ids = list(range(max(0, active - depth), active + depth + 1))
    try:
        bal = c.functions.balanceOfBatch([ME] * len(ids), ids).call()
        held = [(i, b) for i, b in zip(ids, bal) if b > 0]
        return [i for i, _ in held], sum(b for _, b in held)
    except Exception:
        pass
    out, tot = [], 0
    for bid in ids:
        try:
            b = c.functions.balanceOf(ME, bid).call()
        except Exception:
            continue
        if b > 0:
            out.append(bid); tot += b
    return out, tot


def detect_direction():
    """Decide bid vs ask by READING THE TAPE, not by convention.

    ASK (sell into strength) when the rally is confirmed: still making higher highs and
    not rolling over.
    BID (buy the dip) when the pullback is confirmed: a LOWER HIGH on the recent window,
    or a run of red hours.

    Two-sample discipline: a single red hour is not a reversal, and a single green hour is
    not a rally. Mirrors the confirmation gate the rest of the treasury uses.
    Requires 2 agreeing signals to call a pullback, so noise does not flip the book.
    Falls back to ASK when the tape is unreadable -- the side that cannot lose the
    principal (it holds tokens, it does not buy at a falling price).
    """
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://api.exchange.coinbase.com/products/AVAX-USD/candles?granularity=3600",
            headers={"User-Agent": "GenTech-Steward/1.0"})
        d = json.loads(urllib.request.urlopen(req, timeout=25).read())
        d.sort(key=lambda x: x[0])
        cl = [x[4] for x in d]; hi = [x[2] for x in d]
        if len(cl) < 12:
            print("     (tape too short -- defaulting to ASK)"); return "ask"

        # signal A: lower high on the recent window
        recent_high = max(hi[-2:]); prior_high = max(hi[-5:-2])
        lower_high = recent_high <= prior_high

        # signal B: run of consecutive red hours
        reds = 0
        for i in range(len(cl)-1, 0, -1):
            if cl[i] < cl[i-1]: reds += 1
            else: break
        red_streak = reds >= 2

        r1 = (cl[-1]/cl[-2]-1)*100
        r3 = (cl[-1]/cl[-4]-1)*100
        print(f"     tape: 1h {r1:+.2f}%  3h {r3:+.2f}%   red-hours {reds}  "
              f"high {recent_high:.4f} vs prior {prior_high:.4f}")

        # require 2 agreeing signals to call a pullback
        # A RALLY must also be CONFIRMED, not assumed. "No pullback signal" is not a rally -
        # it is an unreadable tape, and the whole point of the two-sample rule is to not act
        # on an unreadable tape. Confirmed rally = still printing HIGHER highs.
        higher_high = recent_high > prior_high

        if lower_high and red_streak:
            print("     -> PULLBACK confirmed (lower high + red streak) -> BID")
            return "bid"
        if higher_high and not red_streak:
            print("     -> RALLY confirmed (higher high, no red streak) -> ASK")
            return "ask"
        print("     -> STABLE / RANGE-BOUND: no confirmed trend in either direction")
        print("        -> CURVE: liquidity both sides of spot, earning on chop")
        return "curve"
    except Exception as e:
        print(f"     (tape read failed: {str(e)[:60]}) -> HOLDING current structure")
        return None



def _assert_may_act(action):
    """Refuse to execute unless THIS tenant is licensed to do it ALONE.

    Wired 2026-09-22. Until now the autonomy levels were documentation - nothing consulted
    them, so any box holding a wallet could re-center capital regardless of its level. The
    check sits at the EXECUTION point because that is the one place it cannot be skipped,
    and it is placed AFTER the dry-run gate: a dry run needs no licence, a real action
    never escapes one.
    """
    import os as _o, sys as _s
    _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
    import steward_identity as _SI
    from tenant_guard import assert_autonomy
    assert_autonomy(_SI.tenant(), action)

def _held_shape(ids):
    """WHICH SHAPE IS ON CHAIN -- the ONE classifier, asked of lfj_shapes.

    ── THE GAP TEST WAS A MIRROR (fixed 2026-09-25, live churn) ──────────────────────────────
    This was `"bid-ask" if _bin_gaps else "curve"` -- a hole at spot. BOTH shapes this system
    deploys are two single-sided legs with a hole (lfj_shapes gives even the CURVE bid_near 2 /
    ask_near 1, leaving bins -1 and 0 empty), so the test named "bid-ask" for EVERY book. Three
    consequences, all of them live at once:
      * `shape_mismatch` (below) was TRUE for every in-range curve, so the SHAPE REBUILD trigger
        fired on a healthy book -- and it bypasses the cooldown AND the streak gates, which is
        how jordan's funded book was withdrawn on a 14.3-minute-old cooldown the re-deploy then
        failed to rebuild (cron 51bc9900e24d_20260925_120552: "since last re-center: 14.3 min
        (cooldown 60 min)" -> "🔄 SHAPE REBUILD" -> "[4] WITHDRAW" -> "curve exit=1" -> "RE-DEPLOY
        FAILED");
      * fee_efficiency scored the bell as a U ("33.9% -- bid-ask at its designed geometry" on a
        curve sitting at its peak), so the low-efficiency trigger fired on a book that was
        placed exactly as designed;
      * a REAL mismatch could never be named, because every book read "bid-ask".

    The classifier lives in lfj_shapes (the single source of truth for geometry) and matches the
    bin COUNT against the shape table: 25 => curve, 45 => bid-ask. If the table cannot be
    imported the old structural test is used, LOUDLY, so a degraded read is visible rather than
    silently believed.
    """
    if not ids:
        return ""           # no bins on chain: neither shape, and no default
    try:
        import lfj_shapes as _ls
        _got = _ls.shape_of_bins(ids)
    except Exception as _e:
        _s = sorted(ids)
        _gaps = [b - a for a, b in zip(_s, _s[1:]) if b - a > 1]
        print(f"     ⚠️  lfj_shapes unavailable ({type(_e).__name__}) — held shape from the "
              f"structural gap test (LESS reliable: both shapes have a hole at spot)")
        return "bid-ask" if _gaps else "curve"
    # An EMPTY answer means the bin count matches no deployable geometry (a PARTIAL book: a leg sold
    # off, a position partly drained). Falling back to the structural gap test would restore the
    # exact bug lfj_shapes fixed — both geometries have a hole at spot, so that test names every
    # book "bid-ask". The RECORD is the better authority: this book was BUILT from a chosen shape,
    # and a partial book is still that shape, just narrower.
    #
    # ── RETURNING "" HERE SILENTLY DISABLED THE SHAPE-MISMATCH BYPASS (fixed 2026-09-27) ───────
    # I introduced this two hours earlier and it deadlocked jordan's book. Line 842 is:
    #     shape_mismatch = bool(held_shape and a.shape and held_shape != a.shape)
    # `""` is FALSY, so `bool("")` is False and the mismatch could never be seen. Meanwhile
    # `eff_trigger` is also False for every shape on this book. BOTH routes to action were closed,
    # so the machine printed its own diagnosis and then did nothing:
    #     -> SHAPE OF RECORD: curve   [from the MARKET's own volatility read]
    #     -> SHAPE from the REGIME: CURVE
    #     ⏸  HOLDING — trigger needs 2 consecutive samples, have 0.
    # It KNEW the shape was wrong and held anyway. That is exactly the state Jordan named:
    # *"the biggest thing I'm worried about is sitting with low efficiency for too long and not
    # acting."* An empty string is not a shape — it is a MISSING READING being used as a VALUE,
    # which is the false-value family this codebase keeps re-learning.
    if _got:
        return _got
    try:
        import json as _json
        reg = os.environ.get("STEWARD_REGISTRY") or \
            "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
        with open(reg) as _fh:
            _rec = ((_json.load(_fh) or {}).get("tenants") or {}).get(
                (os.environ.get("STEWARD_TENANT") or "").strip()) or {}
        _lbl = str(_rec.get("shape") or "").strip().lower()
        if _lbl in ("curve", "bidask", "bid-ask"):
            print(f"     ℹ️  {len(ids)} bins matches no deployable geometry — using the RECORD "
                  f"label '{'bid-ask' if _lbl != 'curve' else 'curve'}' so a real shape mismatch "
                  f"can still be detected.")
            return "bid-ask" if _lbl != "curve" else "curve"
    except Exception:
        pass
    # Last resort: no classifier answer AND no record label. Name the shape by the DISTRIBUTION --
    # where the mass sits -- rather than returning empty, because an empty string is the one value
    # that guarantees no mismatch can ever be detected.
    _edge = sum(1 for b in ids if abs(b - min(ids)) <= 1 or abs(b - max(ids)) <= 1)
    return "bid-ask" if _edge >= max(2, len(ids) // 4) else "curve"


def _regime_canon(s):
    """The regime's shape name -> a geometry key, or None. BOTH spellings, or no shape.

    ── A HYPHEN AND AN UNDERSCORE: THE REGIME COULD NEVER DEPLOY A BID-ASK (fixed 2026-09-25) ─
    `shape_for()` returns "bid-ask" (HYPHEN); `_regime_shape = _want.upper()` made it "BID-ASK";
    and the test that guards the whole block read `if _regime_shape in ("CURVE", "BID_ASK")` --
    an UNDERSCORE. "BID-ASK" != "BID_ASK", so the membership test was False for every bid-ask
    the regime ever called for, the block was skipped, and control fell through to the tape
    (which returns one-sided directions or "curve"). The wide, volatility-driven book Jordan
    asked for ("if we're really moving a lot, we might want to consider a bid-ask especially
    overnight") was therefore unreachable through the regime's own path -- only the CURVE branch
    could fire, and that branch sets the shape the house default already sets.

    The inner canon() fix of 2026-09-23 lives INSIDE this block, so it could never run for the
    value it was written for: the guard failed before the fix was reached. Normalise FIRST, then
    test the normalised value, and refuse an unknown spelling instead of defaulting (canon() maps
    anything it does not know to bidask, and a shape nobody asked for is worse than no shape).
    """
    if not s:
        return None
    _t = str(s).strip().lower().replace("_", "-")
    if _t == "curve":
        return "curve"
    if _t in ("bid-ask", "bidask"):
        return "bidask"
    return None


def gas_trend(w3=None, lookback_blocks=12):
    """(direction, ratio, detail) — where gas is heading, read from the CHAIN, not remembered.

    JORDAN'S ASK (2026-09-27): *"aren't you guys able to look into the market and tell if the price
    of gas is going up or not anyway? ... if the bull market is going on and now the price of gas
    has gone up to 50 cents, isn't there a way you could find that out without having to hit that
    wall? So that way, you can adapt in real time."*

    THE WALL HE MEANT IS THE RIGHT ONE. The system already reads `eth_gasPrice` at call time, so
    it never misprices a cycle — but it has no idea whether it is about to be priced OUT. It finds
    out at the moment it refuses. That is discovering a trend one refusal too late.

    What was measured: Avalanche's base fee sat at 0.04-0.08 nAVAX for most of a week and then ran
    to ~5.2 — roughly 100x — and 25 nAVAX is the level the chain returns to under load, where the
    SAME cycle costs 5x more than it does today. A treasury that only reads the spot price will be
    solvent right up until it is not.

    So read the RECENT RANGE, not just the point: sample the last few blocks and compare the recent
    base fee against its own recent high. Rising gas means each deferred rebalance costs more than
    the last one — which argues for acting sooner, not later, and for topping the reserve up while
    it is still cheap.

    NEVER A GATE. This only reports and advises. (Jordan's standing rule: no invented stoppers.)
    An unreadable chain returns ("unknown", None, ...) — silence is not "stable".
    """
    try:
        import json as _json
        import urllib.request as _ur
        w = w3
        if w is None:
            w = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 20}))
        head = w.eth.block_number
        fees = []
        for i in range(lookback_blocks):
            try:
                b = w.eth.get_block(head - i)
                bf = b.get("baseFeePerGas")
                if bf:
                    fees.append(int(bf) / 1e9)
            except Exception:
                continue
        if len(fees) < 3:
            return "unknown", None, "not enough recent blocks could be read to see a trend"
        newest = fees[0]
        window_max = max(fees)
        window_min = min(fees)
        # compare the last 3 blocks against the window's own high — a spike shows up here
        recent = sum(fees[:3]) / 3.0
        ratio = (recent / window_max) if window_max > 0 else None
        if window_max > 0 and window_min > 0:
            spread = window_max / window_min
        else:
            spread = None
        if ratio is not None and ratio >= 0.9 and spread and spread >= 2.0:
            direction = "RISING"
        elif ratio is not None and ratio <= 0.4:
            direction = "FALLING"
        else:
            direction = "STEADY"
        detail = (f"base fee now {newest:.4f} nAVAX; last {len(fees)} blocks ranged "
                  f"{window_min:.4f}-{window_max:.4f} ({spread:.1f}x)" if spread else
                  f"base fee now {newest:.4f} nAVAX")
        return direction, spread, detail
    except Exception as e:
        return "unknown", None, f"gas trend could not be read ({type(e).__name__}) — not treated as stable"


def _print_gas_trend(w3g):
    """Print the gas-trend HEALTH line. Never raises, never gates — see gas_trend()."""
    try:
        _gdir, _gspread, _gdetail = gas_trend(w3g)
        _icon = {"RISING": "📈", "FALLING": "📉", "STEADY": "➖",
                 "unknown": "❔"}.get(_gdir, "❔")
        print(f"  gas        {_icon} {_gdir} — {_gdetail}")
        if _gdir == "RISING":
            print(f"             each deferred rebalance costs more than the last; topping the"
                  f" reserve up now is cheaper than after the next leg up")
    except Exception:
        pass


def _deployed_book_can_close_its_own_gap(info, position_usd):
    """(ok, why) — can a DEPLOYED book below the floor pay for its own re-center?

    ── THE CIRCULAR DEPENDENCY (found 2026-09-27, on dadrian's live book) ──────────────────────
    The gas gate is checked BEFORE the withdraw — correctly, because refusing to begin is free.
    But that check treats the wallet's CURRENT native balance as everything it will ever have.
    For a DEPLOYED book that is false: the withdraw RETURNS the book as WAVAX + USDC, and that
    recovered capital is what pays for the re-deploy.

    So the gate refused to withdraw a book precisely BECAUSE it had not yet been withdrawn:

        to get gas, top up from the book
        to reach the book, withdraw it
        to withdraw it, you must already have gas      <-- the loop

    Measured on dadrian: balance 0.00458405 AVAX; one exit 0.002250; one re-entry 0.006830.
    He could afford the WITHDRAW but not the RE-DEPLOY, so the whole cycle was refused and his
    book stayed off-centre at 30% efficiency — able to pay for its own repair, forbidden to start.

    ── WHY THIS IS NOT A WEAKENING ─────────────────────────────────────────────────────────────
    It does not lower the floor and it does not lower affordability; it asks a BETTER question.
    The full-cycle rule still applies whenever the wallet cannot afford the withdraw either — a
    wallet that cannot pay for step one is still refused. What changes is the case where the
    withdraw IS affordable and the freed capital demonstrably covers the remainder.

    Three things must ALL hold, each measured, never assumed:
      1. the wallet can afford the withdraw AND the swap that buys native AVAX;
      2. the book's own value covers the shortfall the withdraw does not;
      3. the covered amount leaves enough for the swap's own gas.
    Anything unmeasurable refuses, exactly as before: fail closed.

    THIS CLOSES THE RE-FUNDING LOOP, not just one repair. Once a book can fund its own top-up,
    it no longer needs an outside deposit to recover — so `[4a] PROVISION GAS` can restore the
    floor on every future redeploy, and the floor stops being a one-way ratchet downward.
    """
    import gas_reserve as GR
    bal = float(info.get("balance_avax") or 0.0)
    exit_avax = float(info.get("exit_avax") or 0.0)
    reentry_avax = float(info.get("reentry_avax") or 0.0)
    reserve = float(info.get("reserve_avax") or 0.0)
    gp = float(info.get("gas_price_wei") or 0.0)
    price = float(info.get("avax_usd") or 0.0)

    if not (exit_avax > 0 and reentry_avax > 0 and gp > 0 and price > 0):
        return False, "the phase costs could not be measured — refusing rather than guessing"
    if position_usd is None or position_usd <= 0:
        return False, ("the book's value could not be MEASURED — we cannot claim a book pays for "
                       "its own repair without reading what it is worth")

    # 1. can we pay for the withdraw itself?
    #    exit_avax is decreaseLiquidity + collect + swap, but the RECENTER's withdraw calls
    #    lfj_exit WITHOUT --stable, so the swap in that figure is not spent here. Charging it again
    #    (as the first version of this check did) double-counts a swap and refuses a book that can
    #    in fact afford its withdraw. Use the measured per-op table instead of the phase total.
    #
    #    ⚠️ DO NOT charge this leg a bin-scaled figure. It was briefly set per-bin — 53,121 gas/bin
    #    off a 1,324,046 measurement — and that measurement belongs to the RE-ENTRY, not the
    #    withdraw (see the note above OP_GAS_UNITS in gas_reserve.py; at fb3ba25b7 the same file read
    #    `decreaseLiquidity: 210_000` beside `mint: 1_250_000` while calling 1,324,046 the re-entry).
    #    `lfj_exit.py`, which actually sends this transaction, records the real number: "a full exit
    #    measures at 142,395 gasUsed", which is why its own ceiling is 1.5M with "a real exit uses
    #    ~142k". The table's 210,000 is ~1.5x that receipt and is the correct figure here — and it is
    #    the one this gate was written against.
    withdraw_avax = (GR.OP_GAS_UNITS["decreaseLiquidity"] + GR.OP_GAS_UNITS["collect"]) * gp / 1e18
    if bal < withdraw_avax:
        return False, (f"balance {bal:.8f} AVAX cannot even cover the withdraw "
                       f"({withdraw_avax:.8f} AVAX = decreaseLiquidity + collect) — refusing "
                       f"BEFORE touching a deployed book")
    # the top-up step ALSO spends a swap's gas, but it runs AFTER the withdraw, by which point the
    # wallet holds native again — so it is not part of this gate, only of the shortfall arithmetic.
    swap_gas_avax = (GR.OP_GAS_UNITS["swap"] * gp) / 1e18

    # 2. does the freed capital cover what the withdraw does not?
    #    after the withdraw, the wallet holds (bal - withdraw) native, plus the book as USDC/WAVAX.
    #    What still has to be bought: the re-deploy, the top-up swap's own gas, and the reserve.
    native_after = bal - withdraw_avax
    still_needed_avax = (reentry_avax + swap_gas_avax + reserve) - native_after
    if still_needed_avax <= 0:
        # the withdraw alone frees enough native to finish — no conversion needed
        return True, (f"the withdraw alone frees enough ({native_after:.8f} AVAX after it) to fund "
                      f"the re-deploy {reentry_avax:.8f} + reserve {reserve:.8f}")
    need_usd = still_needed_avax * price
    buyable_usd = max(0.0, position_usd - (swap_gas_avax * price))
    if buyable_usd < need_usd:
        return False, (f"the book is worth ${position_usd:,.2f} but the cycle still needs "
                       f"${need_usd:,.4f} of gas beyond it (after the swap's own cost) — the book "
                       f"cannot close its own gap; an outside deposit is genuinely required")
    return True, (f"PHASED — the withdraw is affordable ({withdraw_avax:.8f} AVAX) and the freed "
                  f"book (~${position_usd:,.2f}) covers the remaining ${need_usd:,.4f} of gas; "
                  f"[4a] PROVISION GAS will buy the native AVAX from the withdrawn USDC")


def _gas_precondition(w3g, me, need_gas=None, rescue=False, position_usd=None):
    """(ok, why) — can the wallet fund the WHOLE withdraw + re-deploy cycle AND keep the gas floor?

    ── ONE SOURCE OF TRUTH: THE FLOOR OWNS THE NUMBER NOW (Jordan, 2026-09-25) ─────────────────
    This check used to carry its own inline `3_500_000` gas budget while the gas FLOOR lived in a
    different file (gas_reserve.py) and was consulted by nobody — two numbers describing one
    wallet, in two places, priced at two different moments. Jordan's floor and this precondition
    overlap: BOTH are asking what the wallet can afford to spend on gas.

    THE NUMBER KEPT IS THE 3.5M ONE. It is the measured budget this gate needs (a full exit
    measures ~142,395 and each single-sided leg ~1.2M, so a smaller derived figure would
    under-budget the exact failure the gate exists to prevent), and it now LIVES in
    gas_reserve.RECENTER_GAS, beside the floor's own one-exit+one-re-entry arithmetic. Both are
    priced off ONE live `eth_gasPrice` read in ONE call — gas_reserve.reserve_info().

    TWO QUESTIONS, ONE ANSWER:
      * can this action FINISH?     balance - budget >= 0        (the original rule)
      * and does it SPEND THE FLOOR? balance - budget >= reserve (the 2026-09-25 floor)
    The second subsumes the first, so there is one gate and one message. A refusal here is FREE
    and happens BEFORE the withdraw: "refusing to begin is free; abandoning halfway is not."

    FAIL CLOSED, unchanged: an unmeasurable gas price or an unreadable balance refuses. When the
    chain cannot be read is exactly when a stranded withdraw is most likely.

    A RESCUE IS NEVER GATED BY THE **FLOOR** (see the module header's RESCUE section): `rescue=True`
    (the --rescue flag) prints that the floor did not gate the action and proceeds.

    ── BUT IT IS STILL GATED BY AFFORDABILITY (fixed 2026-09-27) ──────────────────────────────
    The floor and "can this finish?" were collapsed into one gate, so bypassing the floor also
    bypassed the affordability check — and a rescue then withdrew a DEPLOYED book it could not
    re-deploy, every 10 minutes, for hours. They are two different questions and only ONE of them
    is negotiable:
      * the FLOOR (`balance - budget >= reserve`) is a POLICY — a rescue may override it, because
        the reserve exists for repairs and a stranded book is the emergency it was saved for;
      * AFFORDABILITY (`balance >= budget`) is PHYSICS — no flag can override it, and trying is
        what produced `insufficient funds for gas * price + value`.
    So a rescue still refuses when the wallet cannot pay for the cycle it is about to start. The
    callers only invoke --rescue once the book is ALREADY idle, where there is no withdraw to lose
    and the check is a no-op, so this restores the guarantee without weakening the rescue.
    """
    import gas_reserve as GR
    budget_gas = GR.RECENTER_GAS if need_gas is None else int(need_gas)
    try:
        w = Web3.to_checksum_address(me)
        info = GR.reserve_info(tenant=_steward_tenant(), w3=w3g,
                               balance_avax=w3g.eth.get_balance(w) / 1e18)
    except Exception as e:
        return False, (f"UNMEASURABLE — the chain could not be read ({type(e).__name__}: {e}); "
                       f"a cycle we cannot price is a cycle we cannot prove we can finish")
    if not info.get("measured"):
        return False, (f"UNMEASURABLE — {info.get('unmeasured_reason')}; a cycle we cannot price "
                       f"is a cycle we cannot prove we can finish")
    gp = info["gas_price_wei"]
    need_avax = (budget_gas * gp) / 1e18
    detail = (f"balance {info['balance_avax']:.8f} AVAX, reserve (the floor) "
              f"{info['reserve_avax']:.8f} AVAX, this cycle {budget_gas:,} gas = "
              f"{need_avax:.8f} AVAX @ {gp/1e9:.4f} nAVAX (LIVE)")
    # ── AFFORDABILITY IS NOT NEGOTIABLE, EVEN FOR A RESCUE (fixed 2026-09-27) ────────────────
    # Checked BEFORE the floor gate, and NOT passed `bypass=rescue`. `balance >= need_avax` is
    # physics: if the wallet cannot pay for the cycle, the chain will reject the second half of it
    # and we will be left with a withdrawn book — which is strictly worse than the stranded state
    # the rescue was invoked to fix, and it costs gas to get there.
    #
    # This is the check whose absence stranded jordan's book on 2026-09-27: --rescue bypassed the
    # only gate that asked "can this finish?", so a DEPLOYED book was withdrawn and the re-deploy
    # then failed with `insufficient funds for gas * price + value`, every 10 minutes for hours.
    if float(info["balance_avax"]) < need_avax:
        # ── A DEPLOYED BOOK IS NOT AN EMPTY WALLET (found 2026-09-27) ─────────────────────────
        # Below, the affordability refusal fires only when the wallet cannot fund the cycle from
        # native AVAX alone. For a book that is DEPLOYED that is the wrong question, and asking it
        # produced a circular dependency: the gate refused to withdraw a book because the book had
        # not been withdrawn yet. See _deployed_book_can_close_its_own_gap.
        #
        # The withdraw is still strictly required to be affordable; only the RE-DEPLOY portion may
        # be covered by the capital the withdraw itself frees. A wallet that cannot pay for step one
        # is refused here exactly as before.
        if position_usd is not None:
            _ph_ok, _ph_why = _deployed_book_can_close_its_own_gap(info, position_usd)
            if _ph_ok:
                ok, why = GR.gate(info, cost_avax=need_avax, action="re-center", bypass=rescue)
                # The floor may still refuse (the reserve is a POLICY a rescue may override). The
                # PHASED affordability path overrides the FLOOR only when we are rescuing, or when
                # the book demonstrably restores the floor out of its own capital in step [4a].
                if not ok:
                    return True, (f"{_ph_why}. Floor note: {why} [{detail}]")
                return True, f"{_ph_why} [{detail}]"
            # fall through to the honest refusal, now with the measured reason
            return False, (f"CANNOT FINISH THE CYCLE — the wallet holds "
                           f"{info['balance_avax']:.8f} AVAX but this withdraw + re-deploy needs "
                           f"{need_avax:.8f} AVAX, and the book cannot close its own gap "
                           f"({_ph_why}). Refusing BEFORE the withdraw: starting a two-step "
                           f"move we cannot complete leaves the capital idle AND burns the gas. "
                           f"{'(--rescue overrides the FLOOR, never affordability.) ' if rescue else ''}"
                           f"[{detail}]")
        return False, (f"CANNOT FINISH THE CYCLE — the wallet holds "
                       f"{info['balance_avax']:.8f} AVAX but this withdraw + re-deploy needs "
                       f"{need_avax:.8f} AVAX. Refusing BEFORE the withdraw: starting a two-step "
                       f"move we cannot complete leaves the capital idle AND burns the gas. "
                       f"{'(--rescue overrides the FLOOR, never affordability.) ' if rescue else ''}"
                       f"[{detail}]")
    ok, why = GR.gate(info, cost_avax=need_avax, action="re-center", bypass=rescue)
    if not ok:
        return False, f"{why} [{detail}]"
    return True, f"{why} [{detail}]"


def _reserve_split(GR, ri, total_usd, rescue=False):
    """(deployable_usd, reserve_usd, ok, why) — how much of the wallet is NOT the gas reserve.

    THE COMPOSITION STEP'S FLOOR (Jordan, 2026-09-25). Extracted so it can be PROVEN both ways
    with synthetic balances: "a wallet above the floor deploys balance - reserve" and "a wallet
    below the floor deploys nothing" are claims about THIS function, and a claim about money that
    cannot be exercised is not evidence.

    The reserve is expressed in USD here because that is the unit the composition ratio is stated
    in; the floor itself is computed in AVAX by gas_reserve (live gas price, live AVAX price).
    """
    if not ri or not ri.get("measured"):
        if rescue:
            return float(total_usd), 0.0, True, (
                "RESCUE — the floor was unmeasurable and does NOT gate this run")
        return 0.0, 0.0, False, (
            f"the gas floor could not be measured ({(ri or {}).get('unmeasured_reason')}) — a "
            f"reserve that cannot be sized cannot be held back, so nothing is deployable")
    reserve_usd = ri["reserve_avax"] * ri["avax_usd"]
    deployable = max(0.0, float(total_usd) - reserve_usd)
    return deployable, reserve_usd, True, (
        f"deployable ${deployable:,.2f} of ${total_usd:,.2f}   (the reserve ${reserve_usd:,.4f} "
        f"stays LOOSE — no deploy path may spend it)")


def _verify_ratio(w3, usdc_c, wavax_c, me, target_ask_share, reserve_info):
    """Report the ACHIEVED composition after the tilt swap — measure, never assume.

    THE DEFECT THIS CLOSES (2026-09-26). Everything in the rebalance above computes a TARGET
    ratio and asks a swap to hit it. NOTHING read back what was actually achieved, so a tilt
    miss was SILENT: jordan's book sat at 98.8% USDC / 1.2% WAVAX against a 70% WAVAX target
    while every report still described the intent. Jordan found it himself, by eye, on his own
    chart: "You're doing a 70-30 the opposite way and we're not really earning that much when
    we're heavy on USDC." A target that is never checked is a target that is never met.

    Reads the REAL balances from the chain (not the variables the plan computed with) and says
    plainly whether the tilt landed. An unreadable read reports UNREADABLE — never "on target",
    never a zero (the read-failure-as-value class this fleet keeps hitting).

    Returns (achieved_ask_share or None, on_target: bool|None) so it can be asserted in a test.
    """
    try:
        u = usdc_c.functions.balanceOf(me).call() / 1e6
        w = wavax_c.functions.balanceOf(me).call() / 1e18
        px = None
        if isinstance(reserve_info, dict):
            px = reserve_info.get("avax_usd") or reserve_info.get("price_usd")
        px = float(px or 0)
        if px <= 0:
            print("\n  [4c] VERIFY RATIO — UNREADABLE (no live AVAX/USD to price the WAVAX leg).")
            print("      Cannot confirm the tilt landed. Reported as unknown, never on-target.")
            return None, None
        wusd = w * px
        tot = u + wusd
        if tot <= 0:
            print("\n  [4c] VERIFY RATIO — UNREADABLE (both legs read zero).")
            return None, None
        ask = wusd / tot
        gap = ask - target_ask_share
        print(f"\n  [4c] VERIFY RATIO — the tilt is MEASURED, not assumed")
        print(f"      achieved : {1-ask:.1%} USDC / {ask:.1%} WAVAX (${u:,.2f} / ${wusd:,.2f})")
        print(f"      target   : {1-target_ask_share:.1%} USDC / {target_ask_share:.1%} WAVAX")
        if abs(gap) <= 0.10:
            print(f"      ✅ ON TARGET (off by {gap:+.1%}) — the book is built to the tilt the "
                  f"regime called for.")
            return ask, True
        print(f"      ⚠️  OFF TARGET by {gap:+.1%} — the book is being built at {ask:.1%} WAVAX, "
              f"NOT {target_ask_share:.0%}.")
        print(f"         A REAL divergence, not lag: the tilt swap did NOT land. Deploying anyway "
              f"(a ratio miss beats an idle book), but the composition is not what was asked for.")
        return ask, False
    except Exception as e:
        print(f"\n  [4c] VERIFY RATIO — UNREADABLE ({type(e).__name__}: {e}).")
        print("      Cannot confirm the tilt landed. Reported as unknown, never on-target.")
        return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--side", choices=["bid", "ask", "curve"], default=None,
                    help="bid = USDC below spot; ask = WAVAX above spot; "
                         "curve = BOTH legs straddling spot (earns on chop while still "
                         "absorbing a dip). Jordan 2026-09-21: 'We might want to consider "
                         "a bid ask as we absorb some of this dip.' detect_direction() could "
                         "already RETURN curve, but the CLI would not accept it -- so the only "
                         "way to get a curve was to wait for the tape to go flat, and a "
                         "single-sided ladder parked off-spot earns 0%% in the meantime.")
    ap.add_argument("--near", type=int, default=None, help="closest bin offset from spot")
    ap.add_argument("--far",  type=int, default=None, help="furthest bin offset from spot")
    ap.add_argument("--kind", choices=["uniform", "bidask"], default="bidask")
    ap.add_argument("--ratio", type=float, default=0.30,
                    help="fraction of the WAVAX BALANCE deployed into the ASK leg. It is NOT "
                         "'fraction of book on the USDC side' -- the old help text said that and "
                         "it is INVERTED, which is how a request for a USDC-heavy book turns into "
                         "an AVAX-heavy one. LOWER = more USDC-heavy pool, because the ask leg is "
                         "the only AVAX consumer. Measured on the live book ($10.54 USDC bid vs "
                         "9.1734 WAVAX): 0.30 -> 26%% USDC pool, 0.15 -> 41%%, 0.07 -> 60%%, "
                         "0.05 -> 68%%.")
    ap.add_argument("--confirm", type=int, default=2, help="samples the trigger must persist")
    ap.add_argument("--cooldown-min", type=int, default=60,
                    help="minutes that must pass between re-centers (prevents churn)")
    ap.add_argument("--force", action="store_true", help="skip the in-range check")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--rescue", action="store_true",
                    help="RESCUE ONLY: the gas floor does not gate this run (it still prints the "
                         "floor and says it did not gate). For repairing a state the floor exists "
                         "to prevent — a book stranded out of the pool, capital sitting idle — "
                         "where refusing to pay for the repair to protect a gas balance would "
                         "preserve the very breakage. Never set automatically.")
    a = ap.parse_args()

    # ── THE PER-WALLET LOCK (2026-09-27) ─────────────────────────────────────────────────────
    # Placed HERE, immediately after parsing and BEFORE anything reads or signs, because every
    # path below — withdraw, swap, approve, deploy — mutates one wallet.
    #
    # THE DEFECT THIS CLOSES (measured): the cron cadence is `*/5 * * * *` and one rebuild takes
    # 7–11 minutes, with NO mutual exclusion anywhere in the chain. So the next pass started while
    # the previous one was still mid-cycle — two `--execute` processes on one wallet, observed
    # live (processes from 11:41 and 11:42 alive together; nonce 1601->1604 in 45 min).
    #
    # Consequence, 11:36Z: jordan's book came out 13 bins, ASK-only, out of range, earning $0.00,
    # because the bid leg read an allowance another run was mid-way through changing.
    #
    # Only for EXECUTE runs. A dry run reads and prints; blocking it would make diagnosis
    # impossible while a real run is in flight, and a read-only pass cannot race a writer's nonce.
    if a.execute and a.yes:
        try:
            from agent_lock import WalletLock
        except Exception as _e:
            print(f"  ❌ agent_lock unavailable ({_e}) — refusing to sign without mutual exclusion.",
                  file=sys.stderr)
            sys.exit(9)
        _lock = WalletLock(ME, purpose="recenter")
        _lock.acquire_or_exit()
    else:
        _lock = None

    # ── THE DEPLOYED SHAPE (Jordan, 2026-09-23) ──────────────────────────────────────────────
    # a.side says WHICH WAY UP the book faces (bid / ask / curve). a.shape says WHICH GEOMETRY
    # it is built in (curve ~25 bins / bid-ask 45 bins). They are different questions, and
    # conflating them is how the regime's shape rule stayed dead: the deploy below called
    # lfj-curve-deploy.sh with NO --shape, so it always built the script's default no matter
    # what the regime said. Set from the REGIME at the direction step; curve is the fallback
    # only because that is the house default (tenants.json yield_farm_defaults.shape_default).
    # ── THE SHAPE IS DECIDED HERE, ONCE, AND NOTHING DOWNSTREAM MAY OVERRIDE IT ─────────
    # (fixed 2026-09-23, after three separate fixes changed nothing)
    # The decision block further down was guarded by `if a.side is None:` — and a.side is never
    # None, so that entire block was DEAD CODE and a.shape kept this line's literal on every
    # run. Reading the market, the regime, the width table and the weights function all
    # changed nothing, because none of them could reach the variable the deploy consumes.
    # The market decides; the regime is the fallback; a literal is the last resort. One
    # authority, evaluated before any branch can skip it.
    _mkt = None
    try:
        from steward_rebalance import measured_shape as _ms
        _mkt = _ms()                    # "bid-ask" / "curve" / None (never a default)
    except Exception as _e:
        print(f"     (market shape read failed: {type(_e).__name__} — falling back to the regime)")
    a.shape = _mkt or "curve"
    print(f"     -> SHAPE OF RECORD: {a.shape}"
          + ("   [from the MARKET's own volatility read]" if _mkt else
             "   [market unreadable — house default]"))

    # ── JORDAN'S BIN RULE (Sep 21 2026) ──────────────────────────────────────────────────────
    # "The widest I could see us going for a bid-ask, I said a maximum of 45 bins, because we
    # want to be wide but we also don't want to be so wide we're not earning as much as we
    # could be."  BID 22 + ASK 23 = 45 bins, ~4-5% wide.
    # These defaults previously read 5/60 and 1/45 = 101 bins. A re-center would therefore have
    # redeployed the wide shape we are retiring. The rule has to live in EVERY file that can
    # deploy, not just the one we happened to edit.
    if a.near is None: a.near = 2  if a.side == "bid" else 1
    if a.far  is None: a.far  = 23 if a.side == "bid" else 23

    w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 45}))
    c = w3.eth.contract(address=PAIR, abi=PAIR_ABI)
    bs = c.functions.getBinStep().call()
    active = settled_active(c)
    if active is None:
        print("  ❌ cannot read activeId"); return
    ids, tot = scan(c, active)

    print("=" * 92); print("  LFJ RE-CENTER"); print("=" * 92)
    print(f"  activeId {active}   binStep {bs}   bins held {len(ids)}   LP {tot:,}")

    if tot == 0:
        # ── A FLAT BOOK MUST BE LOUD (fixed 2026-09-23) ─────────────────────────────────────
        # This early return is what let BOTH treasuries sit empty all night UNSEEN. It exits
        # clean (rc=0) carrying text the watchdog's classifier recognises nothing in — "nothing
        # to withdraw — flat" matches none of IDLE CAPITAL / DRIFTED / OUT OF RANGE / REBALANCE
        # NOW / ⚠️. So the position monitor fell SILENT on the one condition it exists to catch,
        # and the failure had to be discovered by Jordan asking "pool status?".
        # A full wallet IS the failure: every cent idle, nothing earning, nothing to withdraw.
        # It now says the material phrase before it returns, so the watchdog speaks at any hour.
        print(f"\n  ⚠️  IDLE CAPITAL — 100.0% of the book is in the wallet: 0 bins deployed, "
              f"nothing earning.")
        # ── THE OPERATOR HOLD (2026-09-28) ────────────────────────────────────────────────────
        # CHECKED BEFORE ANY RE-ENTRY. Jordan exited this pool ON PURPOSE and the watchdog put the
        # capital straight back (see steward_hold.py for the full account). A flat book created by
        # a human decision is not a defect, and the machine had no way to tell the two apart.
        # This is that distinction. Nothing below may re-enter while a live hold is set for the
        # tenant — a hold is an operator instruction, and it outranks the no-idle rule.
        try:
            import steward_hold as _SH
            _held, _why = _SH.is_hold(_steward_tenant())
        except Exception as _e:                                     # fail OPEN, never strand
            _held, _why = False, ""
            print(f"  ℹ️  hold store unreadable ({type(_e).__name__}) — proceeding WITHOUT a hold "
                  f"(fail-open: an unreadable flag must never strand capital)")
        if _held:
            print(f"\n  ⏸  OPERATOR HOLD — NOT RE-ENTERING.")
            print(f"      {_why}")
            print(f"      The book is flat ON PURPOSE. The no-idle rule does not apply to a "
                  f"deliberate")
            print(f"      exit; clear the hold (steward_hold.py --clear) to let the book return.")
            return
        # ── A FLAT BOOK MUST RE-ENTER ITSELF (fixed 2026-09-23) ─────────────────────────────
        # This branch used to print "nothing to withdraw — flat. Run lfj_bid_deploy.py to enter."
        # and return. So the monitor could SEE a flat book but never FIX one: recovery depended on
        # a human running a command. Combined with the old capital gate (which stopped the monitor
        # running at all when flat) that is why jordan went flat and STAYED flat — repeatedly.
        # A book with a funded wallet and no position is not a report, it is a task. Deploy it.
        if not (a.execute and a.yes):
            print("  (dry-run — would re-enter now)")
            return
        # ── A FLAT BOOK HAS NO SIDE TO READ (fixed 2026-09-23, evening — REGRESSION FROM THIS MORNING)
        # This morning's defect-#6 fix removed the `if a.side is None:` block on the reasoning that
        # a.side is NEVER None. THAT WAS WRONG, and it cost jordan his position:
        # On a flat book there is no position to derive a side from, so a.side IS None — and the
        # `else` branch below crashed on `a.side.upper()` with AttributeError, AFTER a successful
        # withdraw. The book was left empty with $121 idle and nothing said so.
        # The side must therefore be DERIVED FROM THE SHAPE when there is no position to read:
        #   curve   -> the curve re-enter path (the correct default now that the market picks shape)
        #   bid-ask -> ask (its leg names are handled by the shape's own deploy)
        # LESSON: "this branch is unreachable" is a claim that must be PROVEN, never inferred from
        # one successful run. The em-dash of evidence here is that it was reachable on the ONE path
        # that matters most — recovery from an empty book.
        if a.side is None:
            _shp = str(a.shape).strip().lower()
            # ── A TWO-SIDED SHAPE MUST NOT COLLAPSE TO ONE LEG (fixed 2026-09-26) ──────────────
            # This read `"curve" if shape == "curve" else "ask"`, so a `bid-ask` shape — which is
            # TWO-SIDED by definition — fell through to a single ASK leg. On a flat book that
            # builds HALF a position: dadrian's 12.96 USDC had nowhere to go and sat idle while
            # only his WAVAX was deployed. A one-sided book wearing a two-sided shape's name is
            # exactly the state the rebalance guard exists to prevent — and here the RECOVERY
            # path itself manufactured it, so every repair run reproduced the fault it was
            # repairing. Deploy the WHOLE balance as the shape it actually is.
            a.side = "curve" if _shp in ("curve", "bidask", "bid-ask", "bid_ask") else "ask"
            print(f"  ⚠️  flat book — no position to read a side from; side derived from the "
                  f"shape {_shp!r}: {a.side}"
                  f"{'  (two-sided — deploying BOTH legs)' if a.side == 'curve' else ''}")

        # ── A FLAT BOOK RE-ENTERS, UNLESS THE WALLET IS AT/BELOW THE GAS FLOOR (2026-09-25) ────
        # There is NO withdraw on this path, so refusing is free and strands nothing: nothing is
        # half-built that would need gas to finish. The legs below hold the reserve back from
        # whatever they deploy, and this gate stops the re-entry entirely when the wallet has no
        # floor left — because the same reserve pays for the re-entry's own gas.
        # --rescue forces it when idle capital is the worse state (see the RESCUE note below).
        try:
            import gas_reserve as _GRf
            _rif = _GRf.reserve_info(tenant=_steward_tenant(), w3=w3,
                                     balance_avax=w3.eth.get_balance(ME) / 1e18)
            _fok, _fwhy = _GRf.gate(_rif, cost_avax=(_GRf.REENTRY_GAS * w3.eth.gas_price) / 1e18,
                                    action="flat-book re-entry", bypass=a.rescue)
            print(f"  {_GRf.floor_line(_rif)}")
        except Exception as _fe:
            _fok = False
            _fwhy = (f"the floor could not be measured ({type(_fe).__name__}: {_fe}) — a deploy that "
                     f"cannot size its own reserve does not spend it. --rescue overrides.")
            print(f"  gas floor: UNMEASURABLE — {_fwhy}")
        if not _fok:
            print(f"\n  🛑 REFUSING TO RE-ENTER A FLAT BOOK — {_fwhy}")
            print(f"     The capital stays in the wallet (idle is recoverable; a wallet with no gas")
            print(f"     to repair is not). Restore the reserve: python3 gas_reserve.py --plan")
            print(f"     If idle capital is genuinely the worse state here, force it: --rescue")
            return
        if a.side == "curve":
            print(f"\n  [5] RE-ENTER — deploying a fresh {a.shape.upper()}")
            dep = subprocess.run(["bash", os.path.join(HERE, "lfj-curve-deploy.sh"),
                                  "--shape", a.shape, "--execute"]
                                 + (["--rescue"] if a.rescue else []), cwd=HERE)
        else:
            print(f"\n  [5] RE-ENTER — deploying a fresh {a.side.upper()}")
            dep = subprocess.run([sys.executable, os.path.join(HERE, "lfj_bid_deploy.py"),
                                  "--side", a.side, "--near", str(a.near), "--far", str(a.far),
                                  "--kind", a.kind, "--ratio", str(1.0 if a.side == "bid" else a.ratio),
                                  "--execute", "--yes"]
                                 + (["--rescue"] if a.rescue else []),
                                 capture_output=True, text=True, timeout=420)
            for l in [l for l in dep.stdout.split("\n") if l.strip()][-6:]:
                print("      " + l.strip())
        if dep.returncode != 0:
            print(f"\n  ❌ RE-ENTRY FAILED (exit {dep.returncode}) — will retry on the next sample.")
            return 1
        print("\n  [6] VERIFY (re-read the chain)")
        time.sleep(4)
        n2 = settled_active(c)
        ids2, tot2 = scan(c, n2)
        if tot2 > 0 and ids2:
            inside2 = min(ids2) <= n2 <= max(ids2)
            print(f"      ✅ re-entered — {len(ids2)} bins, band {min(ids2)}..{max(ids2)}, spot {n2}")
            print(f"      {'✅ band adjacent to spot' if inside2 else '⚠️ band drifted from spot'}")
            # This branch runs before `st` is loaded further down the function, so read it here.
            try:
                st = json.load(open(STATE))
            except Exception:
                st = {}
            st["out_streak"] = 0
            st["last_action_ts"] = int(time.time())
            json.dump(st, open(STATE, "w"))
        else:
            print("      ⚠️ re-read found no position — re-entry did not land.")
        return

    lo, hi = min(ids), max(ids)
    # A SINGLE-SIDED LB position never spans spot by design: an ask sits entirely ABOVE
    # the active bin, a bid entirely BELOW. Asserting 'the band brackets spot' is wrong
    # and would mark every healthy position as broken (caught 2026-09-20).
    # What actually matters is the GAP: how far the nearest edge has drifted from spot.
    # LABELS WERE SWAPPED (found 2026-09-20). In a Liquidity Book, bins ABOVE the active bin
    # hold tokenX (WAVAX) -> a SELL ladder (ASK). Bins BELOW hold tokenY (USDC) -> a dip
    # ladder (BID). The original code had these inverted, so a live BID was reported as an
    # ASK and vice versa. Cosmetic in effect - the re-center direction comes from the tape,
    # not this label - but this label is what a human reads in the Telegram log, so a swapped
    # label actively misleads the operator about what the book is doing.
    if hi < active:      side, gap = "BID", active - hi      # band BELOW spot -> USDC dip ladder
    elif lo > active:    side, gap = "ASK", lo - active      # band ABOVE spot -> WAVAX sell ladder
    else:                side, gap = "SPANNING", 0           # two-sided / straddling
    # healthy when the nearest edge is adjacent (gap small); decayed when it drifts away
    inside = gap <= 2
    # ── ZERO MARGIN MUST NOT READ AS HEALTHY (fixed 2026-09-24) ──────────────────────────
    # `gap` is 0 for EVERY two-sided book (it is measuring "how far OUTSIDE the band", and a
    # straddling book is not outside at all). The print then hardcoded that 0 into the label, so
    # a book whose spot sits exactly ON an edge -- one bin from falling out of the pool, the most
    # fragile geometry we can hold -- printed the SAME "✅ ADJACENT (healthy)" as a book sitting
    # comfortably in the middle. Caught on both live books: jordan's true nearest-edge distance
    # was 4 bins and dadrian's was 7, and BOTH printed "gap=0 bins ✅ ADJACENT (healthy)".
    # The number a reader actually needs is the MARGIN -- the real distance from spot to the
    # nearer edge -- so compute it, always, and say it out loud. Behaviour is unchanged
    # (`inside` still governs the trigger); this only stops the display from hiding fragility.
    margin = min(active - lo, hi - active) if (lo <= active <= hi) else 0
    thin = inside and margin <= 2
    print(f"  band {lo}..{hi}   spot {active}   side={side}   nearest-edge gap={gap} bins"
          f"   margin {margin} bins"
          f"   {'✅ ADJACENT (healthy)' if inside else f'⚠️ DRIFTED {gap} bins away'}")
    if thin:
        print(f"     ⚠️  THIN MARGIN — spot is only {margin} bin(s) from the nearer edge. "
              f"The book is in range but has almost no room; a small move takes it out of the pool.")
    if side == "ASK":  print("     (ask: bins above spot hold WAVAX - correct for a sell-side ladder)")
    if side == "BID":  print("     (bid: bins below spot hold USDC - correct for a dip ladder)")

    # ── DIRECTION INTELLIGENCE ──────────────────────────────────────────────────
    # Jordan (2026-09-20): "The loop should use intelligence to detect the direction."
    # Not a hard-coded side, and not merely preserving what we happen to hold either --
    # either one lets a stale structure survive a regime change. The loop reads the TAPE:
    # confirmed rally -> ASK (sell into strength); confirmed pullback -> BID (buy the dip).
    # Same two-sample discipline used everywhere else: one red hour is not a reversal.
    # ── THE REGIME DECIDES THE SHAPE; THE TAPE DECIDES THE DIRECTION (Jordan, 2026-09-23) ─────
    # Jordan: "the efficiency is really low and we're not earning that much and we want to
    # consider the volatility... if we're really moving a lot, we might want to consider a
    # bid-ask especially overnight." REGIME_SHAPE (steward_rebalance) has said exactly that
    # since it was written — HIGH_VOLATILITY / BULL_TRENDING / BEAR_TRENDING -> BID_ASK.
    #
    # It was never reachable: this file derived its shape from the TAPE alone and never asked
    # the regime, and the watchdog passed only the TILT. So the shape half of the rule was
    # written down, correct, and dead. Consult the regime FIRST; the tape still decides
    # DIRECTION (ask = sell into strength, bid = buy the dip) when the regime is silent.
    #
    # HONEST LIMIT, stated rather than hidden: this path knows curve / bid / ask. A curve<->
    # bid-ask change is two-sided and needs no swap step, but the bid-ask plan is NOT built
    # here yet (lfj_shapes.widths("bid-ask") = 15+30 = 45 bins exists; the deploy path does
    # not). So when the regime asks for BID_ASK we SAY SO and keep the shape we hold, rather
    # than silently deploying a curve and reporting success. A rule that cannot be obeyed must
    # be visible, not swallowed.
    _regime_shape = None
    if a.side is None:
        try:
            from steward_rebalance import read_regime, shape_for, measured_shape
            _r = read_regime() or {}
            # The MARKET reads the shape; the regime is the fallback (Jordan, 2026-09-23:
            # "it was the volatility that gave us the bid-ask strategy"). The regime label is
            # BTC-based, so it cannot speak for AVAX's own tape — the pool's accumulator can.
            _meas = measured_shape()
            _want = shape_for(_r.get("regime"), measured=_meas)
            if _want:
                print(f"     -> REGIME {_r.get('regime')} calls for {_want}")
                _regime_shape = _want.upper()
        except Exception as _e:
            # An unreadable regime must not pick a shape. Fall through to the tape, which
            # at least reads a live signal, and say so.
            print(f"     -> REGIME UNREADABLE ({type(_e).__name__}) — falling back to the tape")

    if _regime_canon(_regime_shape):
        # ── NORMALISE BEFORE THE TEST (fixed 2026-09-25) ─────────────────────────────────────
        # The guard used to be `if _regime_shape in ("CURVE", "BID_ASK")` while the live value is
        # "BID-ASK" (hyphen, from shape_for()). "BID-ASK" is not "BID_ASK", so the whole block --
        # including the canon() fix written inside it the day before -- was unreachable for every
        # bid-ask the regime ever asked for. `_regime_canon` accepts both spellings and returns
        # None for anything else, so an unknown name can never pick a shape.
        _rkey = _regime_canon(_regime_shape)
        # BOTH shapes are TWO-SIDED, so both are expressible through the proven two-leg deploy
        # path -- `lfj-curve-deploy.sh --shape` already resolves either geometry from
        # lfj_shapes.py and enforces the 45-bin ceiling by computation, not prose. No swap step
        # is needed, which is precisely why the regime's shape rule is executable where a
        # one-sided rotation is not (see the note below).
        #
        # So Jordan's volatility rule is now end-to-end: "if we're really moving a lot, we might
        # want to consider a bid-ask especially overnight." HIGH_VOLATILITY / BULL_TRENDING /
        # BEAR_TRENDING -> bid-ask (wide, captures the swings); the calm regimes -> curve.
        # ── A HYPHEN vs AN UNDERSCORE: NO BID-ASK WAS EVER DEPLOYED (fixed 2026-09-23) ──────
        # shape_for() returns "bid-ask" (HYPHEN). This line compared it to "BID_ASK"
        # (UNDERSCORE). The test could never be true, so `a.shape` was ALWAYS "curve" — under
        # every regime, on every deploy, since it was written. The shape decision was
        # decorative: the machine could describe a bid-ask, reason about a bid-ask, print a
        # bid-ask, and never once build one.
        # Caught by deploying twice for a true bid-ask and reading "CURVE LIVE" both times --
        # a fix that is verified only at the DISPLAY would have missed it forever, because
        # every surface except the chain was saying "bid-ask".
        # Fix: use the ONE canonical normaliser that already exists. lfj_shapes.canon()
        # accepts both spellings precisely so a vocabulary mismatch degrades to WORKING
        # rather than to silently-wrong. Never hand-compare two spellings of one value.
        a.shape = "bid-ask" if _rkey == "bidask" else "curve"
        a.side = "curve"          # the two-sided deploy path
        print(f"     -> SHAPE from the REGIME: {_regime_shape}  "
              f"(two-sided, {a.shape} geometry)")
    elif a.side is None:
        d = detect_direction()
        if d is None:
            a.side = side.lower()
            print(f"     -> MAINTAINING {a.side.upper()} (tape unreadable)")
        elif side == "SPANNING" and d.lower() != "curve":
            # ── A CONFIRMED CALL DOES NOT COLLAPSE A HEALTHY CURVE (2026-09-22) ──────────────
            # The tape reads PULLBACK or RALLY and asks for a one-sided ladder. But the
            # re-center path has NO SWAP STEP: collapsing a two-sided book to one side
            # withdraws BOTH legs and re-deploys only one, leaving the other asset idle in the
            # wallet. That is not a theory — it happened at block 95874805, where the ask leg
            # (10.06 WAVAX, ~$111) was withdrawn and never redeployed, and the idle-capital
            # trigger did not catch it because that trigger measures the POSITION, not the
            # wallet. $111 earned nothing until Jordan caught it.
            # A curve already expresses direction — its bid leg absorbs the dip. So a confirmed
            # call re-centres the curve rather than collapsing it, and the capital keeps earning
            # on both sides. Jordan, 2026-09-22: "we should rebalance to a curve."
            a.side = "curve"
            print(f"     -> KEEPING CURVE (tape wanted {d.upper()}): a one-sided rotation has no "
                  f"swap step and would leave the other leg idle")
        else:
            a.side = d
            print(f"     -> DIRECTION from the tape: {a.side.upper()}")
            if d.lower() != side.lower():
                print(f"     -> ROTATION: {side} -> {d.upper()} (structure flip on confirmed signal)")

    # ── two-sample confirmation ────────────────────────────────────────────────
    st = {}
    if os.path.exists(STATE):
        try: st = json.load(open(STATE))
        except Exception: st = {}
    streak = st.get("out_streak", 0) + (0 if inside else 1) if not inside else 0
    st["out_streak"] = streak; st["last_active"] = active; st["ts"] = int(time.time())
    json.dump(st, open(STATE, "w"))
    print(f"  out-of-range streak: {streak}/{a.confirm}")
    # ── IDLE-CAPITAL TRIGGER (Jordan, Sep 21) ────────────────────────────────────────────────
    # Jordan: "we need this to be yield farm logic where we don't want funds to sit idle when it
    # comes, we want funds to be balanced, either 50/50, 60/40, or 70/30."
    #
    # WHY THIS TRIGGER HAD TO EXIST: the two existing triggers (out-of-range, over-bins) both watch
    # the POSITION. Neither watches the WALLET. So a book could sit majority-undeployed, in range,
    # at the correct bin count, and this script would print "no re-center needed" every 10 minutes
    # while most of the capital earned nothing. Measured 2026-09-21: $71.34 loose (63.6% of a
    # $112.88 book) against $41.09 working -- with a green light the entire time. That is the
    # failure mode risk-envelope.json names outright: "Idle capital is the failure mode this
    # exists to prevent."
    #
    # A re-center costs ~$0.003 in gas, so the bar for acting is deliberately low. 25% idle is the
    # threshold: below that the churn is not worth the price impact, above it the foregone fees win.
    #
    # ── AND A FRESH DEPOSIT IS NOT CHURN (fixed 2026-09-24) ──────────────────────────────
    # Jordan, 2026-09-24: "this also means it's a perfect opportunity to dollar cost average so I
    # might add some money after work." His cadence is $20-$150 WEEKLY, and his book is ~$120 --
    # so a $20 deposit is 14% idle, UNDER this threshold, and would have landed and SAT THERE
    # earning nothing until some unrelated trigger happened to fire. He would have seen his money
    # go in and do nothing, which reads as a broken agent.
    # The 25% rule exists to stop CHURN (re-placing an existing book for no gain). Capital that
    # has just ARRIVED is not churn: it is money at 0% that could be earning. Deploying it costs
    # ~$0.001 in gas against a $667k pool, so the price impact is nil.
    # So: trigger on 25% of the book OR an absolute floor, whichever comes first. The floor is
    # set well above gas and well above the ~0.2% dust a re-center leaves behind, so it cannot
    # spin the loop -- it can only pick up money that is genuinely idle.
    IDLE_TRIGGER_PCT = 25.0
    IDLE_TRIGGER_USD = 10.0
    idle_pct = None
    idle_usd = None
    try:
        import steward_fee_ledger as _led
        _snap = _led.snapshot()
        _tot = float(_snap.get("total_usd") or 0.0)
        _liq = float(_snap.get("liquid_usd") or 0.0)
        idle_usd = _liq
        if _tot > 0:
            idle_pct = _liq / _tot * 100.0
    except Exception:
        idle_pct = None

    # An unreadable idle figure must NOT trigger (a failed read is not a real zero -- and it is
    # not a real idle balance either). Only a measured value may act.
    idle_trigger = bool(
        (idle_pct is not None and idle_pct > IDLE_TRIGGER_PCT)
        or (idle_usd is not None and idle_usd >= IDLE_TRIGGER_USD)
    )
    if idle_pct is not None:
        _why = ""
        if idle_pct > IDLE_TRIGGER_PCT:
            _why = f"   ⚠️  IDLE CAPITAL (>{IDLE_TRIGGER_PCT:.0f}% of the book)"
        elif idle_usd is not None and idle_usd >= IDLE_TRIGGER_USD:
            _why = (f"   ⚠️  IDLE CAPITAL (${idle_usd:.2f} sitting at 0% — under the "
                    f"{IDLE_TRIGGER_PCT:.0f}% bar but over the ${IDLE_TRIGGER_USD:.0f} floor; "
                    f"a fresh deposit is not churn)")
        print(f"  idle capital: {idle_pct:.1f}% of the book undeployed "
              f"(trigger >{IDLE_TRIGGER_PCT:.0f}% or >=${IDLE_TRIGGER_USD:.0f}){_why}")
    else:
        print("  idle capital: UNMEASURED — not triggering on an unreadable value")

    # NOTE ON ORDERING (2026-09-22): the idle measurement now runs BEFORE the cooldown gate.
    # The cooldown exists to stop the loop re-centering, being immediately out of range again,
    # and re-centering again — tape flapping. Idle capital is not flapping: it is one deploy
    # of money that is currently earning nothing. With the measurement below the gate, a
    # deposit landing during the 60-minute cooldown sat idle for the rest of the hour while
    # every print said 'COOLDOWN — not acting'. Jordan's rule is no idle funds; a rule that
    # suspends itself for an hour after every action is not the rule he asked for.
    # COOLDOWN — an autonomous loop that re-centers, is immediately out of range again,
    # and re-centers again would eat the position in gas and swap fees. Require a gap.
    last_act = st.get("last_action_ts", 0)
    since_min = (time.time() - last_act) / 60 if last_act else 1e9
    # ── OUT OF RANGE DOES NOT WAIT AN HOUR (fixed 2026-09-23 — same lesson, third gate) ─────────
    # The cooldown already exempts IDLE capital (2026-09-22) because idle money is not flapping
    # — it is money earning nothing. OUT OF RANGE is that same fact one step further on: the
    # whole book is deployed and NONE of it earns. It never got the same exemption, so the
    # re-center that fixes it had to wait out the full hour.
    # Caught live: AVAX fell $11.20 -> $10.44 in a day; jordan broke below his band and the page
    # sat on "Out of Range / 0% efficiency" while Jordan watched and asked why the auto-rebalance
    # was not working. It WAS working — it was queued behind a gate built for a different problem.
    # The hour is NOT dropped entirely: an out-of-range book still gets at most ONE action per
    # watchdog cycle (15 min), so a tape oscillating on the band edge cannot spin the loop.
    # Same shape as the idle fix, same reason, third gate — see IDLE_TRIGGER_PCT above and the
    # streak bypass below. When a rule suspends itself while the thing it protects is losing,
    # the rule is the bug.
    # ══ DECISION INPUTS COMPUTED ABOVE EVERY GATE THAT CAN SHORT-CIRCUIT THEM ═══════════════
    # AUDIT FINDING (Jordan, 2026-09-24: "why don't we do an audit and try to troubleshoot and
    # fix that"). Four decision inputs were computed BELOW the cooldown gate and the streak gate,
    # and BOTH of those gates `return` early. So `over_bins`, `held_shape`, `shape_mismatch` and
    # `eff_trigger` did not EXIST at the moment the gates ran, and could never exempt themselves
    # from either one. The gate printed "COOLDOWN - not acting" or "HOLDING - needs N samples",
    # the run read as complete, and the condition those inputs describe had never been evaluated
    # at all. That is collision #4, and it is why a shape mismatch could never become a rebuild.
    #
    # This is the same family as the three gates fixed before it (idle capital, out of range, and
    # the margin display), but it removes the CAUSE instead of teaching one more gate one more
    # exemption: compute every decision input ONCE, here, above the first `return`. The blocks
    # further down still print their own messages in their own place -- they just no longer OWN
    # the value, so the gates can see it.
    #
    # Classify every condition before gating it: an ARITHMETIC condition (the price is outside the
    # band, the capital is idle, the shape on chain differs from the shape the market calls for) is
    # settled by ONE reading and must never sit behind a confirm-count. A TREND condition (a drift,
    # a breakout, a sustained low-efficiency duty cycle) genuinely needs consecutive samples.
    MAX_BINS = 45
    over_bins = len(ids) > MAX_BINS                                        # ARITHMETIC
    # ONE definition of the shape on chain -- see _held_shape(). It used to be computed HERE
    # and again 200 lines below, with a gap test that named "bid-ask" for every book (both
    # shapes have a hole at spot), which made shape_mismatch fire on the healthy state.
    held_shape = _held_shape(ids)                                          # ARITHMETIC
    shape_mismatch = bool(held_shape and a.shape and held_shape != a.shape)  # ARITHMETIC
    # ── A REGIME THAT JUST FLIPPED IS NOT A VERDICT (added 2026-09-26) ─────────────────────
    # shape_mismatch is deliberately ARITHMETIC and bypasses the cooldown — correct while the
    # regime is STABLE, because a wrong geometry genuinely can be read off the chain and no
    # second sample changes the answer. It is WRONG while the regime is FLAPPING, because then
    # the geometry it demands changes with the label, and every flip is a full withdraw +
    # rebuild. This is the churn engine, measured live today:
    #   10:15 jordan curve 25 bins -> SHAPE REBUILD -> bid-ask
    #   10:48 jordan back to a curve 25 bins (the bid-ask the market "called for" lasted 33 min)
    #   25 bins -> 45 bins -> 25 bins, each step an unsubscribe + redeploy of the WHOLE book.
    # The state file already records the flip (`regime_changed`, `prev_regime`); nothing read
    # it. Now, on a JUST-CHANGED regime, the shape is held and the rebuild waits for the next
    # hourly read to confirm — one sample of patience instead of a withdraw.
    # This does NOT weaken the safety cases. A book that is OUT OF RANGE, or IDLE, or wider
    # than the bin rule, is a real condition read off the CHAIN and still acts immediately;
    # only the shape swap — the one decision that costs a full rebuild — waits for a settled
    # signal. Two flips in a row still confirm, because the second read clears regime_changed.
    _reg_changed = False
    _reg_prev = _reg_now = None
    try:
        from steward_rebalance import read_regime as _rr
        _r2 = _rr() or {}
        _reg_changed = bool(_r2.get("regime_changed"))
        _reg_prev = _r2.get("prev_regime")
        _reg_now = _r2.get("regime")
    except Exception:
        _reg_changed = False       # unreadable -> behave exactly as before, never a new block
    if shape_mismatch and _reg_changed:
        print(f"  ⏸  SHAPE REBUILD HELD — the regime JUST changed ({_reg_prev} -> {_reg_now}); "
              f"the shape it calls for may flip back.")
        print(f"     Holding the funded {held_shape} rather than paying a full withdraw + "
              f"rebuild on an unconfirmed label.")
        shape_mismatch = False
    eff_trigger = False
    _held_eff = None
    try:
        import fee_efficiency as _fe0
        _er = _fe0.evaluate(held_shape) or {}
        eff_trigger = bool(_er.get("triggered"))                          # TREND (duty cycle)
        _held_eff = _er.get("efficiency")
    except Exception:
        eff_trigger = False
    # ── A BOOK EARNING AT THE TOP OF ITS BAND IS NOT THE WRONG SHAPE (added 2026-09-30) ────────────
    # `shape_mismatch` is ARITHMETIC and bypasses the cooldown, so it will withdraw and rebuild the
    # WHOLE book purely because the geometry on chain differs from the geometry the market read
    # names. The guard above (regime-just-changed) already sets the principle: "only the shape
    # swap -- the one decision that costs a full rebuild -- waits for a settled signal." This is the
    # same principle applied to the OUTCOME. fee_efficiency is the measure of whether the shape is
    # doing its job, and the Hold & Earn band (>=70) is the system's own word for "this is working."
    # Rebuilding a book the machine has JUST CALLED "Hold & Earn" is the machine contradicting its
    # own verdict in the same breath.
    # MEASURED, live 2026-09-30: jordan's curve read **95.6% Hold & Earn**, and the recenter still
    # printed "SHAPE REBUILD -- the book on chain is a curve, the market calls for a bid-ask" and
    # planned to swap it back to a 45-bin bid-ask AND a 70/30 tilt -- undoing two explicit operator
    # instructions in one cycle. The bid-ask it wanted to build reads **34.4%**. A rebuild that takes
    # a 96% book to a 34% book is not a repair.
    # This does NOT block a genuine switch: the LOW-EFFICIENCY trigger (<50%) acts on its own, which
    # is exactly the condition Jordan named -- "sitting with low efficiency for too long and not
    # acting." Switch the shape when the book earns poorly; keep it when it earns well.
    # Unreadable efficiency holds NOTHING back (behaves exactly as before).
    # ── FEE EFFICIENCY MATTERS ABOVE ALL (Jordan, 2026-09-30) ────────────────────────────────
    # Jordan, verbatim: "the[y] should listen to me and my strategy" and "Fee efficiency matters
    # above all." That is the ordering of authority made explicit: the OUTCOME outranks every
    # classifier, including this script's own shape read.
    # fee_efficiency.efficiency() is a PURE, shape-aware model of the SAME live range:
    #     bid-ask: e = 2 * |n - 0.5| * 100   (a U  -- peaks at the EDGES, earns nothing in the trough)
    #     curve  : e = (1 - 2*|n - 0.5|) * 100 (a bell -- peaks at the CENTRE, earns nothing at an edge)
    # so the target shape's reading at the CURRENT spot is computable BEFORE spending anything.
    # THE RULE: a rebuild may not LOWER fee efficiency. If the shape the market read names would
    # collect less than the shape already on chain, at the same price, then the rebuild is
    # arithmetic that loses money -- and this is exactly the mechanism that destroyed Jordan's book.
    # MEASURED 2026-09-30: jordan's 25-bin curve read **95.6%**; the rebuild the machine performed
    # at 08:08-08:10 replaced it with a 45-bin bid-ask that read **41.4%** minutes later. Two
    # operator instructions (the curve, and the 60/40) were undone in one cycle by a classifier
    # whose own arithmetic said the other shape paid less. A switch DOWN the efficiency scale is
    # not a rebalance. This also ends the churn loop, because each rebuild was creating the next
    # trigger. The <50% low-efficiency trigger still fires as before: if the HELD shape is the
    # worse one, the comparison passes and the machine switches -- it just may no longer trade a
    # better book for a worse one. Unreadable numbers hold NOTHING back (behaves as before).
    if shape_mismatch and _held_eff is not None:
        try:
            import fee_efficiency as _feE
            _mm = _feE.evaluate(held_shape) or {}
            _sp, _lo, _hi = _mm.get("spot"), _mm.get("low"), _mm.get("high")
            _alt = (_feE.efficiency(float(_sp), float(_lo), float(_hi), a.shape)
                    if None not in (_sp, _lo, _hi) else None)
        except Exception:
            _alt = None
        if _alt is not None and float(_alt) < float(_held_eff):
            print(f"  HOLD: SHAPE REBUILD REFUSED -- FEE EFFICIENCY MATTERS ABOVE ALL.")
            print(f"     on chain : {held_shape} reads {float(_held_eff):.1f}%")
            print(f"     market's : {a.shape} would read {float(_alt):.1f}% at the SAME spot "
                  f"(${_sp:,.4f}, same range)")
            print(f"     A rebuild that collects LESS is not a rebalance. Keeping the book that pays "
                  f"more; the <50% trigger still switches when the held shape is the worse one.")
            shape_mismatch = False
    if shape_mismatch and _held_eff is not None and float(_held_eff) >= 75.0:
        print(f"  HOLD: SHAPE REBUILD HELD -- the held {held_shape} reads {float(_held_eff):.1f}% "
              f"(Hold & Earn).")
        print(f"     The market read names '{a.shape}', but a book earning at the top of its band "
              f"is not the wrong shape.")
        print(f"     Rebuilding it would trade {float(_held_eff):.1f}% for the other geometry's "
              f"~35% baseline. The <50% low-efficiency trigger still switches shape when the book "
              f"genuinely earns poorly.")
        shape_mismatch = False

    OUT_COOLDOWN_MIN = 10   # was 15 — tightened 2026-09-25 (Jordan: "watch for five minutes and
                            # then after ten minutes we'll rebalance... this market is more active
                            # than the one before"). The watchdog now runs every 5 min, so a 2-sample
                            # TREND confirm lands at 10 min; 15 was leaving the book idle 5 min longer
                            # than the confirm it was enforcing. Out-of-range is ARITHMETIC and still
                            # acts on ONE sample.
    _cd = a.cooldown_min if inside else min(OUT_COOLDOWN_MIN, a.cooldown_min)
    print(f"  since last re-center: {since_min:.1f} min (cooldown {_cd} min"
          + (f"; OUT OF RANGE shortens it from {a.cooldown_min} min)" if _cd != a.cooldown_min else ")"))
    # An ARITHMETIC condition is not flapping and must not wait out a cooldown either. `over_bins`
    # (the book is wider than the rule allows) and `shape_mismatch` (the book on chain is not the
    # shape the market calls for) are both settled by READING THE CHAIN -- no second sample can
    # change either answer. They were previously invisible here because they were computed further
    # down; see the block above the gate.
    if last_act and since_min < _cd and not a.force and not idle_trigger \
            and not over_bins and not shape_mismatch:
        print(f"\n  ⏸  COOLDOWN — {_cd - since_min:.1f} min remaining. Not acting.")
        if not inside:
            print(f"     (out of range, but under the {OUT_COOLDOWN_MIN}-min floor — one action "
                  f"per watchdog cycle)")
        if idle_trigger:
            print("     (idle capital is present but the gate was reached first — should not happen)")
        return

    # ── IDLE CAPITAL BYPASSES THE STREAK TOO (fixed 2026-09-23) ──────────────────────────────
    # The 2026-09-22 idle fix taught the COOLDOWN gate that idle capital is not flapping — it is
    # money earning nothing — and let `idle_trigger` through. The STREAK gate never got the same
    # lesson, so an out-of-range book with idle capital waited for a trend to confirm before it
    # could deploy the very capital that was doing nothing. Caught live: jordan at 50.2% idle,
    # drift 3 bins, streak 1/2 -> HOLDING, while half his book sat in the wallet.
    # A streak exists to prove a CONDITION is real (a drift, a regime flip). "This money is not
    # earning" needs no confirmation — it is true on every single reading. Same ruling, same
    # reason, second gate.
    # ── OUT OF RANGE BYPASSES THE STREAK TOO (fixed 2026-09-24) ──────────────────────────────
    # Caught LIVE on jordan's book while Jordan watched and asked "why are we getting axed":
    #     band 8363270..8363296   spot 8363267   side=ASK   gap=3 bins
    #     out-of-range streak: 1/2
    #     ⏸  HOLDING — trigger needs 2 consecutive samples, have 1.
    # His money was OUT OF THE POOL, earning nothing, while the machine waited ten minutes for a
    # second opinion. The two-sample rule is right for a DRIFT (a gap can close, a regime can flip
    # back) — but "the price is outside our band" is ARITHMETIC, not a trend: either spot sits
    # between the band edges or it does not, and no second reading can change the answer.
    # A streak exists to prove a CONDITION is real. "This money is not earning" needs no
    # confirmation — it is true on every single reading. SAME RULING as the idle fix directly
    # above, and the same as Jordan's 70/30 rule: a condition that is ARITHMETIC must not wait
    # for a trend to confirm it.
    # The oscillation worry ("a tape sitting on the band edge spins the loop") is already covered
    # by OUT_COOLDOWN_MIN above — an out-of-range book gets at most ONE action per 15-min cycle —
    # so the streak was redundant here and only ever cost us earning time.
    # ── A SHAPE MISMATCH AND OVER-BINS BYPASS THE STREAK TOO (fixed 2026-09-24) ──────────────
    # COLLISION #4, reported by Jordan ("we were having collision issues yesterday"). Both are
    # ARITHMETIC conditions read off the chain: the book IS this wide, the book IS this shape.
    # Neither is a trend, so neither may wait for one to confirm. Same ruling as the idle and
    # out-of-range bypasses above -- and this time the exemption can actually be SEEN, because
    # the inputs are now computed above the gate instead of below it.
    # ── THE SUSTAINED-LOW-EFFICIENCY TRIGGER CARRIES ITS OWN CONFIRMATION (fixed 2026-09-25) ──
    # `eff_trigger` is the ONLY trigger built for the state this gate is most likely to swallow:
    # the book is IN RANGE, correctly shaped, fully deployed — and earning nothing because spot
    # is sitting at the shape's trough. It is a TREND trigger and it ALREADY has its own
    # confirmation window: the duty cycle has to stay low for 10-20 minutes before
    # `triggered` is set at all.
    #
    # It was missing from this gate's exemption list, and `streak` is the OUT-OF-RANGE counter
    # (line 564: `streak = ... if not inside else 0`) — so for ANY in-range book `streak` is
    # structurally 0 and `0 < a.confirm` is always true. The gate therefore returned HOLDING
    # unconditionally, and `eff_trigger=True` could never reach the ONE place that reads it (the
    # `✅ in range — no re-center needed` return below, whose entire purpose is to let this
    # trigger through when it is true).
    # MEASURED, before this fix (same live book, dry run, in range, correct shape, 0.1% idle):
    #     duty cycle low  -> "⏸  HOLDING — trigger needs 2 consecutive samples, have 0."
    #     duty cycle fine -> "⏸  HOLDING — trigger needs 2 consecutive samples, have 0."
    # Identical output for a failing book and a healthy one: the trigger's answer made no
    # difference to the run. A money rule that cannot fire on the state it exists for.
    # This does NOT weaken the gate for a DRIFT — a drift's evidence IS the streak. It only
    # stops one trigger being conditioned on evidence that belongs to another. Churn stays
    # bounded by the COOLDOWN gate above, which deliberately does NOT exempt eff_trigger: an
    # in-range low-efficiency re-centre is a trend and waits its hour.
    if inside and streak < a.confirm and not a.force and not idle_trigger \
            and not over_bins and not shape_mismatch and not eff_trigger:
        print(f"\n  ⏸  HOLDING — trigger needs {a.confirm} consecutive samples, have {streak}.")
        print("     One reading is not a trend (see 2026-09-20 false-value lessons).")
        if idle_trigger:
            print("     (idle capital present — it bypasses this gate; should not reach here)")
        return
    if not inside and streak < a.confirm:
        print(f"\n  ⚡ OUT OF RANGE — acting on ONE sample (streak {streak}/{a.confirm}).")
        print("     The price is outside the band: that is arithmetic, not a trend, and no second")
        print("     reading can change it. The book is earning nothing while we wait.")
    # ── OUT-OF-RANGE TRIGGER (Jordan, 2026-09-23) ────────────────────────────────────────────
    # Jordan: "We didn't write the logic for when we're out of the range of the pool." He was
    # right, and it was worse than missing: there was NO branch for it, and the one string that
    # described it — "out-of-range streak: N/M", lowercase — could never match the watchdog's
    # classifier, which greps the uppercase "OUT OF RANGE". So the condition this whole job
    # exists to catch was both unhandled and unspoken.
    #
    # AND THE DIRECTION MATTERS — these are opposite events, not one event:
    #   * UP   -> the ask leg sold into the rally, so the book is now ~100% WAVAX. Re-centring
    #             UPWARD sells MORE WAVAX into the move: the LP doing the exact opposite of
    #             Jordan's bullish mode ("when the market takes off, we withdraw and hold the
    #             asset"). hold_trigger.py passes all three gates right now.
    #   * DOWN -> the bid leg bought the dip, so the book is now ~100% USDC. Re-centring down is
    #             a ladder back in — precisely the shape it was built for. That one re-centres.
    #
    # This branch NAMES the direction and says it out loud. It does NOT auto-consolidate into
    # WAVAX: that is a capital action, Jordan owns it, and the brain's own exit_plan.py exists
    # for it. A proposal, not a trade.
    if not inside:
        # ── THE DIRECTION WAS INVERTED HERE — fixed 2026-09-23, minutes after writing it ─────
        # `side` is the BAND's position relative to spot, not the book's composition:
        #     hi < active -> side="BID"  -> the band sits BELOW spot -> price ran UP through it
        #     lo > active -> side="ASK"  -> the band sits ABOVE spot -> price ran DOWN through it
        # I had written `_up = (side == "ASK")`, which reported every upward escape as a
        # downward one. Caught on live data: jordan held 15 bins at [10.8443-10.9971] with spot
        # at $11.02 — band BELOW spot, i.e. an UP escape, which the old test called "DOWN".
        #
        # The composition was inverted too. Bins ABOVE spot hold WAVAX (asks, selling into a
        # rise); bins BELOW hold USDC (bids, buying a fall). So a rally SELLS the ask leg and
        # leaves the book mostly USDC — not WAVAX, as this first said. Confirmed by this
        # position's own history: "a curve whose ask leg has been consumed by the rally" left
        # it ~95% USDC.
        _up = (side == "BID")
        print(f"\n  ⚠️  OUT OF RANGE — spot is {gap} bins {'above' if _up else 'below'} the band; "
              f"nothing in the book is earning.")
        if _up:
            print("     Escaped UP: the ask leg SOLD into the rally — the book is now mostly USDC.")
            print("     Re-centring UP chases the price and never consolidates. Jordan, 2026-09-23:")
            print("     'No longer following those old notes. We're in a bull market, things have")
            print("     changed.' The posture is HOLD THE ASSET — the April 75/25 note is RETIRED,")
            print("     and the regime closes the split question, not a reconciliation of notes.")
            # ── BULLISH MODE — PROPOSE, NEVER TRADE (Jordan, 2026-09-23) ─────────────────────
            # hold_trigger.py (3 gates) -> exit_plan.py --mode HOLD_TOKEN.
            # WHY THIS IS SAFE TO WIRE: exit_plan.py is a READ-ONLY planner — stdlib imports
            # only, no tx path anywhere in it, 0.03s. It prints the swap/remove sequence and
            # touches no wallet. So the machine can propose a directional conversion without
            # performing one; Jordan owns the execution and has not yet seen it propose once.
            #
            # WHY THE GATE IS CACHED: hold_trigger.py fetches ~90d of live prices and takes
            # ~39s. Running that on every out-of-range pass (each 15 min) would be wasteful and
            # the answer barely moves intraday. So the verdict is cached for BULLISH_TTL_MIN and
            # its AGE IS ALWAYS PRINTED — a cached verdict that does not say how old it is reads
            # as a fresh one, which is the false-value pattern with a clock on it.
            BULLISH_TTL_MIN = 60
            try:
                import subprocess as _sp
                _bt = st.get("bullish_gate", {})
                _age = (time.time() - _bt.get("ts", 0)) / 60 if _bt.get("ts") else 1e9
                if _bt.get("verdict") and _age < BULLISH_TTL_MIN:
                    _verdict, _src = _bt["verdict"], f"cached {_age:.0f} min ago"
                else:
                    _g = _sp.run([sys.executable, os.path.join(HERE, "hold_trigger.py")],
                                 capture_output=True, text=True, timeout=180)
                    _verdict = "HOLD" if "VERDICT" in _g.stdout and "HOLD is justified" in _g.stdout \
                               else ("FARM" if "VERDICT" in _g.stdout else "UNREADABLE")
                    _bt = {"verdict": _verdict, "ts": int(time.time())}
                    st["bullish_gate"] = _bt; json.dump(st, open(STATE, "w"))
                    _src = "measured now"
                print(f"     hold_trigger: {_verdict}  ({_src})")
                if _verdict == "HOLD":
                    _e = _sp.run([sys.executable, os.path.join(HERE, "exit_plan.py"),
                                  "lfj", "--mode", "HOLD_TOKEN"],
                                 capture_output=True, text=True, timeout=60)
                    for _l in _e.stdout.splitlines():
                        if any(k in _l for k in ("EXIT PLAN", "swaps", "gives up", "risk",
                                                 "REMOVE", "SWAP", "COLLECT", "HARVEST")):
                            print(f"     {_l.strip()}")
                    print("     -> PROPOSAL ONLY. No capital has moved. Jordan owns this call.")
                elif _verdict == "FARM":
                    print("     -> gates do not justify holding: re-centre and keep farming.")
                else:
                    print("     -> gate UNREADABLE — not proposing on an unknown. Re-centre.")
            except Exception as _ex:
                print(f"     (bullish proposal unavailable: {type(_ex).__name__} — re-centre as normal)")
        else:
            print("     Escaped DOWN: the bid leg BOUGHT the dip — the book is now mostly WAVAX.")
            print("     Re-centring down is a ladder back in: the shape this position was built for.")

    # ── OVER-BINS TRIGGER (Jordan, Sep 21) ───────────────────────────────────────────────────
    # The old logic fired ONLY on out-of-range. A position sitting comfortably in range with 101
    # bins would never re-center - so the 45-bin rule governed an event that might never come.
    MAX_BINS = 45
    over_bins = len(ids) > MAX_BINS
    if over_bins:
        print(f"\n  ⚠️  OVER BINS — holding {len(ids)} bins, rule maximum is {MAX_BINS}.")
        print(f"     In range, but wider than the rule allows: the same capital spread thinner")
        print(f"     earns less per bin. Jordan (Sep 21): 'we're okay right now, but we can earn")
        print(f"     more money by closing the gap.' Closing it.")


    if idle_trigger:
        print(f"\n  ⚠️  IDLE CAPITAL — {idle_pct:.1f}% of the book is sitting in the wallet earning")
        print(f"     nothing. In range and within the bin rule, but the capital is not WORKING.")
        print(f"     Re-centering to deploy the full balance (Jordan: 'we don't want funds to")
        print(f"     sit idle').")
        # ── IDLE CAPITAL DEPLOYS BOTH LEGS (2026-09-22) ─────────────────────────────────────
        # If the reason capital is idle is that the book went one-sided, then re-deploying the
        # SAME one side leaves the other asset idle again — the loop would fire every 10
        # minutes, pay gas, and never fix it. Only a two-sided deploy puts both assets to work.
        # This is the same ruling as the shape switch below, reached from a different trigger:
        # Jordan, 2026-09-22: "we should rebalance to a curve."
        if side != "SPANNING":
            print(f"     -> IDLE IS FROM A ONE-SIDED BOOK ({side}) — deploying BOTH legs as a curve")
            a.side = "curve"

    # ── FEE-EFFICIENCY TRIGGER (Jordan, 2026-09-21) ─────────────────────────────────────────
    # Jordan: "I had rules in place for this. The cron Job should see the fee efficiency has been
    # low for 10 mins and rebalance based on scenario."
    #
    # The rule already existed in defi-rebalance.py — bid-ask pays at the EDGES (U-shape), curve
    # pays at the CENTER (bell) — but it was pinned to a position we no longer hold
    # (RANGE_LOW=6.70 / RANGE_HIGH=6.88 while AVAX trades ~$11.16 and our real range is
    # ~$10.99-$11.50) and it ran twice a day. A rule bound to a stale range cannot observe a
    # 10-minute condition in the position that exists.
    #
    # fee_efficiency.py evaluates the recovered rule against the LIVE legs, and persists the
    # low-streak across runs — a single reading cannot tell you how long a condition has HELD,
    # which is the whole requirement.
    # ── WHICH SHAPE ARE WE ACTUALLY HOLDING? (fixed 2026-09-22, TWICE) ─────────────────────
    # FIRST FIX: this called `_fe.evaluate("bid-ask")` — a HARDCODED shape, so once the book
    # became a curve the module still scored it as a bid-ask and kept reporting "switch to
    # curve" about a position that already WAS one.
    # SECOND FIX (this one): the replacement read `side`, which is NOT the shape. `side` is
    # where the SPOT SITS relative to the band (BID = band below spot, ASK = band above it,
    # SPANNING = spot inside it). A curve that drifts out of range stops SPANNING and gets
    # labelled BID or ASK — so the moment the position most needs measuring correctly, its
    # shape flipped to bid-ask and it was scored with U-shape math against a bell-shaped book.
    # The shape is a property of the BOOK, not of where the price happens to be standing.
    # Read the structure: a curve is ONE CONTIGUOUS BAND of bins; a bid-ask is TWO legs with a
    # HOLE at the spot (that hole is the entire point of the shape). Contiguity survives the
    # position going out of range, which is exactly when we need the answer.
    # held_shape was computed ONCE above the gates (_held_shape) and is deliberately NOT
    # recomputed here: two computations of one decision drift apart, and the second one is the
    # one that acts.
    eff_trigger = False
    eff = None
    try:
        import fee_efficiency as _fe
        eff = _fe.evaluate(held_shape)
        eff_trigger = bool(eff.get("triggered"))
        line = (f"  fee efficiency: {eff['efficiency']:.1f}% ({eff['band']}) "
                f"as a {held_shape} at {eff['posPct']:.0f}% of range")
        if eff_trigger:
            line += f"   ⚠️  LOW FOR {eff['lowForMinutes']:.1f} MIN"
        print(line)
    except Exception as _e:
        print(f"  fee efficiency: UNMEASURED ({type(_e).__name__}) — "
              f"not triggering on an unreadable value")

    if eff_trigger:
        sc = eff.get("scenario") or {}
        print(f"\n  ⚠️  LOW FEE EFFICIENCY — {eff['efficiency']:.1f}% sustained for "
              f"{eff['lowForMinutes']:.1f} min (rule: act after 10).")
        print(f"     SCENARIO: {sc.get('action')}")
        print(f"     {sc.get('detail')}")

        # ── THE SHAPE SWITCH (Jordan, 2026-09-22) ───────────────────────────────────────────
        # Until now the trigger DETECTED and REPORTED while the plan deployed the SAME shape:
        # a low-efficiency bid-ask was "fixed" by re-deploying a low-efficiency bid-ask, and
        # the low-streak never cleared. Jordan ruled the response: "fee efficiency has been low
        # for awhile. we should rebalance to a curve." The scenario already computed the
        # alternative shape and its efficiency — this is where that computation becomes the
        # ACTION instead of a note beside it.
        # It only ever moves bid-ask -> curve, never back. A switch that could reverse would
        # oscillate between two shapes on alternating readings, paying gas to stand still.
        #
        # ── FIXED 2026-09-23: THE CHURN THIS CAUSED ──────────────────────────────────────────
        # Wiring the regime in (above) created a FIGHT between two shape authorities. This
        # block set `a.side = "curve"` but left `a.shape` at whatever the REGIME chose — and
        # the deploy uses a.shape. So a low-reading bid-ask withdrew, announced "SWITCH to
        # curve", and then re-deployed a BID-ASK. The book churned withdraw -> redeploy of the
        # SAME shape on every pass, and BOTH tenants ended up FLAT in their wallets:
        #   "SHAPE SWITCH: bid-ask -> curve"  followed by  "RE-DEPLOY BID-ASK"
        # One shape authority, not two. When the REGIME supplies a shape it WINS and this
        # trigger re-centres WITHIN it; the legacy switch applies only when the regime is
        # silent (unknown). A low reading is then handled where it belongs — by re-centring
        # the geometry, which is the thing that was actually wrong.
        # ── THE ONE SHAPE AUTHORITY IS THE OUTCOME, NOT THE LABEL (Jordan, 2026-09-30) ────────
        # Jordan, verbatim: "the[y] should listen to me and my strategy" and "Fee efficiency
        # matters above all." The block below kept the "one shape authority, not two" principle
        # written on 2026-09-23 — that principle is RIGHT, and it stopped a real churn. What it
        # got wrong was WHICH authority holds the pen: it gave the pen to the regime label, so a
        # book reading 9.5% was re-centred inside its own trough while the machine printed, in the
        # same breath, "(A curve would read 91% here — but the REGIME owns the shape ... this
        # trigger cannot override it.)" A number that says 91% outranks a label that says bid-ask.
        # THE RULE: at the live spot and the live range, the shape with the higher fee efficiency
        # wins. This is still ONE authority — it is simply the measurement instead of the label —
        # and it is the authority Jordan named. A margin (20 points) keeps it from twitching on a
        # near-tie, so a switch is only ever taken when the other shape materially pays more.
        # The guard added above is the mirror of this one: never switch DOWN either. Together they
        # make efficiency monotonic — the book may only move toward the shape that collects more.
        _sw = None
        try:
            import fee_efficiency as _feS
            _ms = _feS.evaluate(held_shape) or {}
            _sp, _lo, _hi = _ms.get("spot"), _ms.get("low"), _ms.get("high")
            _he = _ms.get("efficiency")
            _other = "curve" if (a.shape or held_shape) == "bid-ask" else "bid-ask"
            if None not in (_sp, _lo, _hi) and _he is not None and _other != held_shape:
                _ae = _feS.efficiency(float(_sp), float(_lo), float(_hi), _other)
                _sw = (_other, float(_he), float(_ae))
        except Exception:
            _sw = None                                       # unreadable -> behave exactly as before
        if _sw and (_sw[2] - _sw[1]) >= 20.0:
            print(f"     -> SHAPE SWITCH ON EFFICIENCY — fee efficiency matters above all "
                  f"(Jordan, 2026-09-30):")
            print(f"        {held_shape} reads {_sw[1]:.1f}% at the live spot; {_sw[0]} reads "
                  f"{_sw[2]:.1f}% on the SAME spot and range (+{_sw[2]-_sw[1]:.1f} points).")
            print(f"        The regime label says {a.shape}; the measurement says {_sw[0]}. "
                  f"The measurement wins.")
            a.shape = _sw[0]
            a.side = "curve"
            _regime_shape = None                             # the outcome is the authority now
        if _regime_shape:
            print(f"     -> SHAPE IS THE REGIME'S CALL ({a.shape}) — re-centring within it; "
                  f"not switching shape")
        elif held_shape != "curve" and not _mkt:
            print(f"     -> SHAPE SWITCH (Jordan 2026-09-22): {held_shape} -> curve")
            a.side = "curve"
            a.shape = "curve"
        elif held_shape != "curve" and _mkt:
            # The market's own read says this shape is right. A low reading is then handled by
            # re-centring WITHIN the shape (the geometry was the thing that was wrong), which is
            # exactly what the regime branch above already does. Switching shape because a
            # number is low is how the books churned earlier today.
            print(f"     -> LOW READING, but the MARKET still calls for {a.shape} — "
                  f"re-centring within it, not switching shape")

    # ── THE MARKET'S OWN SHAPE IS A REASON TO ACT (Jordan, 2026-09-23) ──────────────────
    # Jordan: "the auto balancer is not rebalancing ... stuck in the middle of our bid-ask ...
    # why aren't the rules being honored? What's blocking us?"
    #
    # What was blocking him: the trigger set was {out-of-range, over-bins, idle, sustained-low-eff}.
    # The book was IN RANGE, so the first three were silent -- and the fourth needs an UNINTERRUPTED
    # 10-minute low streak, which a price oscillating in and out of the low zone resets forever.
    # Each trigger has its own blind spot, and together they missed the actual condition: the
    # market had called for a CURVE while the book sat there as a 45-bin bid-ask, earning ~20%
    # where a bell earns ~80%.
    #
    # The doctrine says THE MARKET PICKS THE SHAPE. So a disagreement between the market's read and
    # the book on chain is not a detail to note in passing -- it is the instruction. A shape that
    # no longer matches the market is a book that is no longer doing its job.
    #
    # Guarded like every other trigger: it rides the cooldown, so it cannot churn.
    _held = locals().get("held_shape")
    shape_mismatch = bool(_held and a.shape and _held != a.shape)
    if shape_mismatch:
        print(f"\n  🔄 SHAPE REBUILD — the book on chain is a {_held}, the market calls "
              f"for a {a.shape}. Re-centring into the market's shape.")

    # ── THE HEAVY-LEG RULE — SPEC ONLY, NOT YET WIRED (Jordan, 2026-09-24) ─────────────────
    # "Whenever we have a 70/30 bid-ask and we're breaking up or down... now we're no longer in
    #  the 70%... and we're coming back down to the 30. We should rebalance immediately, because
    #  we're not gonna be earning as much on the 30%. So we want to stay on the 70."
    #
    # NOT IMPLEMENTED ON PURPOSE. Two attempts were written and BOTH were unfireable, so neither
    # shipped — a money trigger that cannot fire is indistinguishable from one that works, and
    # this day has already produced six of those.
    #   Attempt 1 keyed off `side`, which is SPANNING whenever spot is inside the band — the
    #             NORMAL state of a straddling bid-ask. Could never fire.
    #   Attempt 2 tested `active in _thin_bins`, but those bins are defined as `> active` (asks)
    #             or `< active` (bids), so spot is excluded BY CONSTRUCTION. Could never fire.
    #
    # THE SPEC, for implementation with a harness:
    #   The condition is about WHERE THE MONEY SITS RELATIVE TO SPOT, not about band edges.
    #   Measure the share of the book's USD value held in bins NEAR spot (say +/-3 bins). When the
    #   price has moved into the leg that holds the SMALL share, the near-spot mass collapses
    #   toward the thin ratio (~30%) while the book is still "in range" and fully deployed.
    #   FIRE when near-spot mass falls below the thin leg's share — IMMEDIATELY, no confirm streak,
    #   because it is arithmetic rather than a trend read.
    #   Needs: per-bin USD (the hub collector already computes it as `shape[].usd`), spot, ratio.
    #   VERIFY both directions: a book at its designed geometry must NOT fire; a book whose price
    #   has crossed into the thin leg MUST fire.
    heavy_vacant = False
    if inside and not over_bins and not idle_trigger and not eff_trigger and not a.force \
            and not shape_mismatch and not heavy_vacant:
        print("\n  ✅ in range — no re-center needed.")
        return

    # ── READ THE REAL LEGS AND RATIOS (2026-09-21) ────────────────────────────────────────────
    # This line printed a HARDCODED "BID 22 + ASK 23 = 45 bins" and a ratio taken from a.ratio --
    # which the curve path never passes to the deploy script. So the plan described a deploy that
    # was not the deploy: after the legs became 15+30 it still said 22+23, and after ASK_RATIO
    # went to 1.0 it still said 70/30. A plan that does not describe what runs is a report that
    # lies, and this is the same family as the rest of today's bugs. Read the values that the
    # deploy script will actually use.
    def _curve_plan():
        # GEOMETRY comes from lfj_shapes.py — the ONE source of truth (Jordan, 2026-09-22).
        # This used to regex the SOURCE TEXT of lfj-curve-deploy.sh for BID_NEAR/BID_FAR/
        # ASK_NEAR/ASK_FAR. That broke the moment the shell stopped hardcoding them and started
        # deriving them from lfj_shapes: the values now appear as a Python f-string
        # (`print(f"BID_NEAR={d['bid_near']}; ...")`), so a numeric regex finds nothing and the
        # plan degraded to "legs UNREADABLE — do not trust this plan". A plan that says do not
        # trust it is worse than no plan. fee_efficiency.py already learned this exact lesson;
        # this reader had not. Ask the table, never scrape the shell.
        # The RATIOS are still plain shell assignments, so reading those from the shell is fine.
        import lfj_shapes as _ls
        try:
            # ── ASK FOR THE SHAPE BEING DEPLOYED, NOT ALWAYS "curve" (fixed 2026-09-23) ──────
            # This line read widths("curve") unconditionally, so the plan described 12+13=25 bins
            # while the deploy built 15+30=45 — the plan was the ONE surface still lying after the
            # geometry was fixed, because it was the one place that named a shape of its own.
            # Caught by dry-running the corrected pipeline and reading "re-deploy … 25 bins" next
            # to a deploy that had just put 45 bins on chain.
            # An operator authorises from this line. A plan that names a different shape from the
            # one about to be built is a report that lies, and this is the same family as every
            # other defect today.
            w = _ls.widths(a.shape)
            nb, na = w["bid_n"], w["ask_n"]
            legs = f"BID {nb} + ASK {na} = {nb+na} bins ({w['shape']})"
        except Exception:
            legs = None

        ratio = None
        try:
            src = open(os.path.join(HERE, "lfj-curve-deploy.sh")).read()
            def g(k):
                for line in src.split("\n"):
                    s = line.strip()
                    if s.startswith("#"):
                        continue
                    m = re.search(rf'(?:^|[;\s]){k}="?([0-9.]+)"?', s)
                    if m:
                        return float(m.group(1))
                raise ValueError(k)
            br, ar = g("BID_RATIO"), g("ASK_RATIO")
            ratio = f"BID {br*100:.0f}% of USDC / ASK {ar*100:.0f}% of WAVAX"
        except Exception:
            ratio = None

        if legs is None and ratio is None:
            return ("legs UNREADABLE", "ratio UNREADABLE — do not trust this plan")
        return (legs or "legs UNREADABLE (lfj_shapes unavailable)",
                ratio or "ratio UNREADABLE (lfj-curve-deploy.sh ratios unreadable)")

    if a.side == "curve":
        _legs, _ratio_desc = _curve_plan()
    else:
        _legs = f"{a.far-a.near+1} bins"
        # ── PRINT THE RATIO THAT WILL ACTUALLY BE PASSED (fixed 2026-09-23, Sr audit) ──────
        # This printed `a.ratio` for ANY non-curve side, but the deploy below forces
        # `bid_ratio = 1.0` for a bid leg (a bid is pure buying power; the ask ratio is an ASK
        # instruction). So an armed bid run announced e.g. "55/45 USDC/AVAX" and then deployed
        # 100% — and the PLAN block is the ONLY thing the watchdog captures and a human audits.
        # A plan that does not describe the action is worse than no plan.
        _eff_ratio = 1.0 if a.side == "bid" else a.ratio
        _ratio_desc = (f"{int((1-_eff_ratio)*100)}/{int(_eff_ratio*100)} "
                       f"{'AVAX/USDC' if a.side=='ask' else 'USDC/AVAX'}"
                       + ("  (bid leg deploys its full balance — the ask ratio is an ASK instruction)"
                          if a.side == "bid" else ""))
    print(f"\n  ── PLAN ──  withdraw -> re-deploy {a.side.upper()} ({a.kind}, {_legs})")
    _sdesc = {"bid": "USDC below spot (buy the dip)",
              "ask": "WAVAX above spot (sell into strength)",
              "curve": "BOTH legs straddling spot (bid absorbs the dip, ask earns on chop)"
              }.get(a.side, a.side)
    print(f"     side    : {_sdesc}")
    print(f"     ratio   : {_ratio_desc}")
    # ── THE FLOOR IS PART OF THE PLAN, BECAUSE THE PLAN IS WHAT A HUMAN AUDITS (2026-09-25) ────
    # The plan block is the only surface Jordan reads before authorising a re-center. A plan that
    # says "deploy the whole balance" while the code holds a reserve back is a plan that lies.
    try:
        import gas_reserve as _GRp
        _rip = _GRp.reserve_info(tenant=_steward_tenant(), w3=w3,
                                 balance_avax=w3.eth.get_balance(ME) / 1e18)
        print(f"     floor   : {_GRp.floor_line(_rip)}")
        if not _rip.get("measured"):
            print(f"               ⚠️  the floor is UNMEASURABLE — a deploy refuses on this state.")
        elif not _rip.get("above"):
            print(f"               ⚠️  {_GRp.shortfall_text(_rip)}")
    except Exception as _e:
        print(f"     floor   : UNMEASURABLE ({type(_e).__name__}: {_e}) — a deploy refuses on this "
              f"state, and a deploy that cannot size its own reserve must not spend it")
    # ── AND SAY WHAT THE BOOK WILL END UP BEING (Jordan, 2026-09-23) ──────────────────────────
    # `--ratio` is the ask (WAVAX) share and the rebalance now CONVERTS to hit it, so the plan is
    # incomplete without it: "BID 100% / ASK 100%" describes the legs' deployment, not the
    # composition Jordan is actually choosing when he says "70/30 USDC-heavy". The plan block is
    # the only thing a human audits, so it must state the outcome, not just the mechanism.
    _ask_pct = int(round(a.ratio * 100))
    print(f"     target  : {100-_ask_pct}% USDC / {_ask_pct}% WAVAX by value "
          f"(ratio {a.ratio:g} = the ask/WAVAX share)")
    print(f"               built by CONVERTING in the rebalance step, then deploying the whole "
          f"balance MINUS the gas reserve (Jordan, 2026-09-25) — nothing idle, and the reserve the"
          f" no-idle rule may never spend")

    # ── AN UNREADABLE PLAN MUST NOT EXECUTE (fixed 2026-09-23, Sr audit) ────────────────────
    # Lines above print "legs UNREADABLE — do not trust this plan" / "ratio UNREADABLE" and then
    # the code proceeded to withdraw and deploy on exactly that unreadable basis — the watchdog
    # always passes --execute --yes, so a bad read moved real money every pass. A warning the
    # code ignores is not a warning. Refuse.
    if "UNREADABLE" in f"{_legs} {_ratio_desc}":
        print("\n  ❌ PLAN UNREADABLE — refusing to move capital on a plan we cannot read.")
        return 1

    if not (a.execute and a.yes):
        _print_gas_trend(Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 20})))
        print("\n  (dry-run — pass --execute --yes to run)")
        return

    _assert_may_act("maintain")   # re-centering an existing position is class 2

    # ── GAS PRECONDITION — CHECK THE WHOLE CYCLE BEFORE THE POINT OF NO RETURN ──────────────
    # Root-caused 2026-09-25 on live money. A re-center is NOT gas-atomic: it WITHDRAWS (spending
    # gas) and THEN re-deploys two single-sided legs (spending more). When the withdraw drains the
    # wallet, the deploy dies on "insufficient funds for gas" and the capital lands in the WORST
    # possible state -- out of the pool, idle, earning nothing, with only 0.000025 AVAX left to
    # fix it.
    #
    # Observed: balance 0.00002497 AVAX after the withdraw; leg 1 needed 0.00004858 and leg 2
    # 0.00005155 -- a full curve re-deploy needs 0.00010013, FOUR TIMES what the wallet held. Both
    # legs exited 1, the wrapper printed PARTIAL, and jordan's $119.50 sat idle in the wallet.
    #
    # THE RULE: an action that can strand capital must prove it can FINISH before it STARTS.
    # Refusing to begin is free; abandoning halfway is not. If the wallet cannot fund the full
    # cycle we HOLD THE POSITION AS-IS -- a book that is merely out of range still holds its
    # inventory and can still be fixed later. A book that has been withdrawn and cannot be
    # re-deployed is strictly worse in every dimension.
    _gp_w3 = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 20}))
    # ONE GATE, ONE NUMBER (Jordan, 2026-09-25). The 3.5M-gas budget and the gas FLOOR are the same
    # question asked twice ("what can this wallet afford to spend on gas?"), so they are now ONE
    # check with ONE source of truth — gas_reserve.py — priced off ONE live gas-price read. The
    # number KEPT is the 3.5M measured budget, moved out of here into gas_reserve.RECENTER_GAS;
    # there is no second, competing figure left in this file.
    # ── IS THIS BOOK DEPLOYED, AND WHAT IS IT WORTH? (found 2026-09-27) ───────────────────────
    # The phased path below needs the book's MEASURED value. If it cannot be measured we pass
    # None and the gate behaves exactly as before — a claim that "the book pays for its own
    # repair" must never rest on a number we could not read.
    _pos_usd = None
    try:
        import steward_fee_ledger as _ledg
        _pv = float((_ledg.snapshot() or {}).get("total_usd") or 0.0)
        _pos_usd = _pv if _pv > 0 else None
    except Exception:
        _pos_usd = None
    _ok, _why = _gas_precondition(_gp_w3, ME, rescue=a.rescue, position_usd=_pos_usd)
    if not _ok:
        print(f"\n  🛑 REFUSING TO START — CANNOT SHOW THE CYCLE CAN BE FINISHED, FLOOR INTACT.")
        print(f"     {_why}")
        print(f"     A re-center WITHDRAWS first and re-deploys second. Starting this would spend")
        print(f"     the withdraw's gas and then fail the deploy, stranding the capital OUT of the")
        print(f"     pool and earning nothing — strictly worse than leaving it in place.")
        print(f"     HOLDING the position unchanged. Top up native AVAX and the next pass proceeds.")
        print(f"     (gas_reserve.py --plan prints the exact swap; it rotates a sliver of the book's")
        print(f"      own USDC into AVAX, so it needs no outside deposit.)")
        print(f"     ⚠️  GAS FLOOR — the reserve is what pays for the NEXT swap or re-deploy, and no")
        print(f"     deploy path may spend it (Jordan, 2026-09-25).")
        print(f"     A genuine EMERGENCY (a book stranded out of the pool, capital idle) is not")
        print(f"     blocked: run with --rescue, which prints that the floor did not gate it.")
        print(f"     FAIL CLOSED: a precondition that cannot be EVALUATED refuses too — when the")
        print(f"     chain is unreadable is exactly when a stranded withdraw is most likely.")
        return

    # ── 4. WITHDRAW ────────────────────────────────────────────────────────────
    print("\n  [4] WITHDRAW")
    ex = subprocess.run([sys.executable, os.path.join(HERE, "lfj_exit.py"), "--execute", "--yes"],
                        capture_output=True, text=True, timeout=420)
    tail = [l for l in ex.stdout.split("\n") if l.strip()][-6:]
    for l in tail: print("      " + l.strip())

    # ── THE WITHDRAW MUST SUCCEED BEFORE WE DEPLOY (fixed 2026-09-22) ─────────────────────────
    # This used to ignore the exit code entirely: it printed the last six lines of the withdraw
    # and re-deployed regardless. So a FAILED withdraw was indistinguishable from a successful
    # one, and the deploy legs then ran against an empty wallet — reverting one after another and
    # reporting "PARTIAL — bid=4 ask=4", which reads like a routing fault instead of "the money
    # never left the pool". Dadrian's position sat out of range through exactly this: his
    # encrypted key could not be read by the old plaintext key path, so every withdraw failed
    # silently and every deploy was doomed. Check the result, and stop if the money is not loose.
    if ex.returncode != 0:
        # ── EXIT CODE IS NOT THE CHAIN'S ANSWER (fixed 2026-09-26) ────────────────────────────
        # This branch printed "Nothing was sent. The position is unchanged" for ANY non-zero
        # exit. On 2026-09-26 dadrian's withdraw BROADCAST AND LANDED (tx 58398469a4c41f38e30a
        # 26a9f990daccf261dbcd9c5ecefdbbdd626699b840c3) and lfj_exit.py then crashed with a
        # Traceback AFTER sending, exiting 1. This branch read that as "nothing happened",
        # ABORTED the rebuild, and left dadrian's book EMPTY with $28 idle in the wallet — the
        # exact stranded-withdraw state the abort believed it was preventing. A tool that
        # crashes after broadcasting is indistinguishable, BY EXIT CODE ALONE, from one that
        # never sent anything. So ask the CHAIN: if a tx was broadcast, re-read the position.
        # Gone => the withdraw succeeded and we carry on. Only abort when the money is
        # genuinely still in the pool, or when the chain cannot be read at all.
        _sent = "SENT" in ex.stdout
        _landed = None
        if _sent:
            try:
                _c = Web3(Web3.HTTPProvider(RPC, request_kwargs={"timeout": 45})).eth.contract(
                    address=PAIR, abi=PAIR_ABI)
                _a = _c.functions.getActiveId().call()
                _ids, _tot = scan(_c, _a)
                _landed = (len(_ids) == 0)
            except Exception:
                _landed = None
        if _sent and _landed is True:
            print(f"      ⚠️  withdraw tool exited {ex.returncode} AFTER broadcasting — NOT "
                  f"trusting the exit code.")
            print("      ✅ re-read the chain: the position is GONE, so the withdraw DID land. "
                  "Continuing the rebuild instead of stranding the capital.")
        else:
            print(f"\n  ❌ WITHDRAW FAILED (exit {ex.returncode}) — ABORTING before re-deploy.")
            if _sent and _landed is None:
                print("     A tx WAS broadcast but the chain could not be re-read to confirm it "
                      "landed. Aborting rather than guessing — check the wallet and the pool.")
            else:
                print("     Nothing was sent. The position is unchanged; this is not a partial "
                      "build.")
            for l in ex.stdout.split("\n") + ex.stderr.split("\n"):
                if any(k in l for k in ("❌", "Error", "error", "reverted", "Traceback",
                                        'File "', "line ")):
                    print("       " + l.strip()[:180])
            return 1
    if "SENT" not in ex.stdout:
        print("\n  ❌ WITHDRAW reported success but sent NO transaction — ABORTING.")
        print("     A withdraw that does not withdraw looks exactly like one that did.")
        return 1

    # ── 4a. PROVISION GAS FROM THE CAPITAL JUST FREED (Jordan, 2026-09-27) ────────────────────
    # JORDAN'S PLAN, in his words: *"if we're still able to do the swap and everything is good right
    # now, let's just go ahead and continue and once you like redeploy, just go ahead and make sure
    # you keep 20 cents worth of Avax for gas. So that way, even though we're low right now, we're
    # below our cap, we can fix it on the next redeployment."*
    #
    # WHY THIS WAS A REAL GAP, not a missing convenience: the recenter PRESERVES native AVAX but
    # never CREATES it. Its composition step sizes the deploy against `deployable = wallet MINUS
    # reserve` — so it can hold the reserve back, but it has no way to RESTORE one. A wallet that
    # is already under the floor can therefore never recover through a redeploy alone; the most it
    # can do is rebuild the book and stay exactly as under-funded as before.
    #
    # The capital to fix it arrives at THIS exact moment: the withdraw just returned the book as
    # WAVAX + USDC, and WAVAX unwraps 1:1 to native AVAX. Waiting one step longer (until after the
    # swap) lets the swap consume the WAVAX it needs for leg balance first, and there is simply
    # less left to unwrap. So this runs between the withdraw and the swap/deploy.
    #
    # ADVISORY, NEVER FATAL. If gas cannot be provisioned the book is still rebuilt — a thin gas
    # balance is bad, but a book stranded out of the pool earning nothing is worse. Same ordering
    # the rescue rule already uses.
    print("\n  [4a] PROVISION GAS from the withdrawal (keep the floor, per Jordan's 20c rule)")
    gt = subprocess.run([sys.executable, os.path.join(HERE, "gas_topup.py"),
                         "--execute", "--yes"], capture_output=True, text=True, timeout=900)
    _gt_out = (gt.stdout or "") + (gt.stderr or "")
    if "✅" in _gt_out and gt.returncode == 0:
        for _l in _gt_out.split("\n"):
            if any(k in _l for k in ("UNWRAP", "SELF-SUFFICIENT", "after ", "gas now",
                                     "provisioned", "SENT")):
                print("     " + _l.strip()[:160])
    else:
        print(f"     ℹ️  gas provisioning did not change the wallet (exit {gt.returncode}) — "
              f"continuing. The book is rebuilt regardless; a thin gas balance is less bad than a "
              f"stranded book.")
        for _l in _gt_out.split("\n"):
            if any(k in _l for k in ("⛔", "SHORTFALL", "NOT WORTH IT", "no usable asset")):
                print("       " + _l.strip()[:160])

    # ── 4b. REBALANCE THE LEGS (the swap step that was missing) ────────────────
    # THE GAP THIS CLOSES: this script withdraws and then re-deploys the SAME assets. It had no
    # swap step at all. So a book that has gone ONE-SIDED can never rebuild its other leg — and a
    # book goes one-sided precisely when price leaves the range, which is exactly when you want to
    # re-center. Every bid fills as price falls, leaving 100% WAVAX; the BID leg then needs USDC,
    # the wallet holds none, the deploy reverts, and the position sits out of range earning nothing.
    # Measured on Dadrian 2026-09-22: 2.680995 WAVAX, 0.000005 USDC, and a BID plan that could not
    # be funded. The withdrawal worked; the rebuild was impossible.
    #
    # Swap through the SAME proven leg used everywhere else (lfj_swap_leg.py, version byte fixed
    # to v2.2=3), so this needs no new routing.
    _ERC = json.loads('[{"name":"balanceOf","type":"function","stateMutability":"view",'
                      '"inputs":[{"type":"address"}],"outputs":[{"type":"uint256"}]}]')
    _wavax = w3.eth.contract(address=Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7"), abi=_ERC)
    _usdc  = w3.eth.contract(address=Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"), abi=_ERC)
    # Refuse to rebalance on a guessed price — a wrong price swaps the wrong amount and turns a
    # re-center into an unintended directional bet.
    try:
        import steward_fee_ledger as _L
        price = float(_L.avax_usd())
    except Exception:
        price = 0.0
    if price <= 0:
        print("      ❌ cannot read the AVAX price — refusing to rebalance blind. ABORTING.")
        return 1
    w_bal = _wavax.functions.balanceOf(ME).call() / 1e18
    u_bal = _usdc.functions.balanceOf(ME).call() / 1e6
    w_usd, u_usd = w_bal * price, u_bal
    total = w_usd + u_usd
    print(f"\n  [4b] REBALANCE — wallet {w_bal:,.6f} WAVAX (${w_usd:,.2f}) + "
          f"{u_bal:,.6f} USDC (${u_usd:,.2f}) = ${total:,.2f}")
    _ask_pct = int(round(a.ratio * 100))
    print(f"      target composition: {100-_ask_pct}% USDC / {_ask_pct}% WAVAX "
          f"(ratio {a.ratio:g} = the ask/WAVAX share; the rest is USDC dry powder)")

    if total < 1.0:
        print("      ❌ nothing to rebalance — wallet is empty after the withdraw. ABORTING.")
        return 1

    # ── THE RESERVE IS NOT DEPLOYABLE CAPITAL (Jordan, 2026-09-25) ────────────────────────────
    # Jordan: "keeping like maybe 10 cents of the natural whatever the coin is for gas... You still
    # got to have a little bit of gas." This is the re-center's COMPOSITION decision — how much to
    # swap and how much to deploy — and it is where the no-idle rule used to win by default:
    # `--ratio 1.0` on both legs put 100% of the book to work and left the wallet unable to pay for
    # its next swap or re-deploy. "Deploy the whole balance" now means "the whole balance MINUS the
    # reserve": everything below is sized against `deployable`, so the reserve is never CONVERTED
    # into the book either — the wallet keeps a loose slice it can rotate into gas.
    # The floor comes from gas_reserve.py (LIVE gas price, LIVE AVAX price) — ONE implementation.
    _GR, _ri = None, None
    try:
        import gas_reserve as _GRm
        _GR = _GRm
        _ri = _GR.reserve_info(tenant=_steward_tenant(), w3=w3,
                               balance_avax=w3.eth.get_balance(ME) / 1e18)
    except Exception as _e:
        _ri = {"measured": False, "unmeasured_reason": f"{type(_e).__name__}: {_e}"}
    deployable, _reserve_usd, _split_ok, _split_why = _reserve_split(_GR, _ri, total, a.rescue)
    if _GR is not None:
        print(f"      {_GR.floor_line(_ri)}")
    print(f"      {_split_why}")
    if not _split_ok:
        print(f"      ❌ ABORTING rather than deploying a floor we cannot measure.")
        return 1
    if deployable < 1.0:
        print(f"      ❌ nothing deployable above the reserve — ABORTING (the whole balance is the "
              f"gas floor).")
        return 1

    # ── THE RATIO DRIVES THE COMPOSITION, NOT A HARDCODED 50/50 (Jordan, 2026-09-23) ────────
    # Jordan: *"it's looking like a pullback for AVAX ... let's look into doing a 70, 30 USDC-heavy
    # bid-ask since we're trending down."* That could not be expressed: the curve's target was a
    # fixed 50/50, and the curve PLAN read its ratios from lfj-curve-deploy.sh (1.0/1.0) while
    # ignoring --ratio entirely. The tilt existed in REGIME_TILT/`tilt_for` ("the ask-leg ratio
    # this regime calls for") and reached NOTHING that set the book's shape.
    #
    # `a.ratio` IS the ask (WAVAX) share, so it sets the TARGET COMPOSITION here and the swap
    # below converts to hit it. Then the deploy still puts the WHOLE balance of each asset to
    # work (BID_RATIO/ASK_RATIO stay 1.0). That matters: Jordan's standing ruling is that idle
    # capital is the failure mode ("it left ~$71 of a $113 book earning ZERO"), so a 70/30 book
    # must be built by CONVERTING WAVAX to USDC, not by leaving 70% of the WAVAX raw on the
    # sidelines during a pullback — where raw WAVAX simply loses value as price falls.
    if a.side == "curve":
        want_wavax_usd = deployable * a.ratio
    elif a.side == "ask":
        want_wavax_usd = deployable * max(a.ratio, 0.9)
    else:                                   # bid: USDC-heavy, the bid leg buys the dip
        want_wavax_usd = deployable * a.ratio

    drift = (w_usd - want_wavax_usd) / deployable if deployable else 0
    if abs(drift) < 0.10:
        print(f"      ✅ legs already balanced (drift {drift:+.1%}) — no swap needed")
    else:
        if w_usd > want_wavax_usd:
            amt_usd = w_usd - want_wavax_usd
            pct = amt_usd / w_usd
            print(f"      swapping {pct:.1%} of WAVAX (~${amt_usd:,.2f}) -> USDC")
            sw = subprocess.run([sys.executable, os.path.join(HERE, "lfj_swap_leg.py"),
                                 "--from", "wavax", "--pct", f"{pct:.6f}", "--execute", "--yes"]
                                + (["--rescue"] if a.rescue else []),
                                capture_output=True, text=True, timeout=420)
        else:
            # ── SOLD THE WRONG LEG'S TARGET: NEGATIVE AMOUNT EMPTIED A BOOK (2026-09-24) ──
            # This was `amt_usd = u_usd - want_wavax_usd` — USDC minus the *WAVAX* target, a
            # comparison between two different legs. Wanting MORE WAVAX than we hold makes
            # `want_wavax_usd` LARGER than our USDC, so the difference went NEGATIVE
            # (68.02 - 84.95 = -16.93), the percentage inherited the sign (-24.9%), the swap
            # leg refused a negative amount, and the recenter aborted AFTER withdrawing —
            # leaving a funded book empty and earning nothing.
            #
            # The USDC to SELL is what we hold above the USDC share we intend to keep:
            #     keep_usdc = total - want_wavax_usd
            #     sell_usdc = u_usd - keep_usdc
            # which is the same quantity as (want_wavax_usd - w_usd), stated from the USDC side.
            # Checked against the live book: 68.02 - (121.36 - 84.95) = $31.61 to sell, positive.
            keep_usdc = deployable - want_wavax_usd
            amt_usd = u_usd - keep_usdc
            if amt_usd <= 0:
                # Defensive: never hand a non-positive amount to a swap. If the arithmetic
                # surprises us, say so and leave the book alone rather than abort a half-built
                # position. Refusing to act is safe; acting on a wrong number is not.
                print(f"      ⚠️  computed swap amount is {amt_usd:+,.2f} — refusing to swap")
                print(f"         (hold {u_usd:,.2f} USDC, target USDC share {keep_usdc:,.2f})")
                sw = None
            else:
                pct = amt_usd / u_usd
                print(f"      swapping {pct:.1%} of USDC (~${amt_usd:,.2f}) -> WAVAX")
                sw = subprocess.run([sys.executable, os.path.join(HERE, "lfj_swap_leg.py"),
                                     "--from", "usdc", "--pct", f"{abs(pct):.6f}", "--execute", "--yes"]
                                    + (["--rescue"] if a.rescue else []),
                                    capture_output=True, text=True, timeout=420)
        if sw is not None:
            for l in [l for l in sw.stdout.split("\n") if l.strip()][-5:]:
                print("      " + l.strip())
            # ── "SENT" IS NOT "SUCCEEDED" (fixed 2026-09-23, Sr audit) ────────────────────
            # The old test passed on any line announcing a broadcast — "SENT" / "sent 0x" —
            # which a transaction that LATER REVERTS also prints. The abort below exists
            # precisely to stop a one-sided book being deployed onto a misbalanced wallet, and
            # the bare broadcast token let the very failure it guards against slip through.
            # Require the success marker.
            if sw.returncode != 0 or "status=SUCCESS" not in sw.stdout:
                # ── A FAILED OPTIMISATION IS NOT A FAILED RE-CENTER (fixed 2026-09-26) ─────────
                # The guard exists to stop a ONE-SIDED book being deployed with a leg it cannot
                # fund. It was implemented as "if the ratio swap failed, abort" — a STRICTER test
                # than its own purpose, and on 2026-09-26 that stricter test cost Jordan his whole
                # position: a healthy, in-range, 80.8%-efficient curve was WITHDRAWN for a SHAPE
                # REBUILD; the WAVAX->USDC ratio swap then found no route (all three router
                # versions reverted: v3 0x32e2717a, v2/v1 0xd648e3a2); and this line aborted,
                # leaving $146.47 in the wallet earning nothing with NO BOOK AT ALL.
                # The swap only moves the book toward the 65/35 TARGET ratio. Both sides were
                # already funded (67.28 USDC + 7.47 WAVAX), so a perfectly good two-sided book
                # was deployable the moment it was withdrawn. Aborting a rebuild because an
                # OPTIMISATION failed converts a ratio miss into a total outage.
                # So ask the question this guard actually MEANS: can each leg be funded?
                _needs_usdc = a.side in ("bid", "curve")
                _needs_wavax = a.side in ("ask", "curve")
                _no_usdc = u_bal < 1e-6
                _no_wavax = w_bal < 1e-9
                if (_needs_usdc and _no_usdc) or (_needs_wavax and _no_wavax):
                    print(f"\n  ❌ REBALANCE SWAP FAILED (exit {sw.returncode}) AND a leg has "
                          f"NOTHING to deploy — ABORTING before re-deploy.")
                    print("     Deploying an unbalanced book is how a curve silently becomes "
                          "one-sided.")
                    print(f"     wallet after withdraw: {u_bal:,.6f} USDC / {w_bal:,.6f} WAVAX")
                    return 1
                print(f"\n  ⚠️  REBALANCE SWAP FAILED (exit {sw.returncode}) — CONTINUING WITHOUT "
                      f"IT. Both legs are funded, so the book can still be rebuilt two-sided.")
                print(f"     wallet after withdraw: {u_bal:,.6f} USDC (${u_usd:,.2f}) / "
                      f"{w_bal:,.6f} WAVAX (${w_usd:,.2f})")
                print(f"     It will land OFF the {1-a.ratio:.0%} USDC / {a.ratio:.0%} WAVAX target "
                      f"ratio — not one-sided. A ratio miss beats an empty book.")
                print("     Worth diagnosing: a swap that cannot quote on ANY router version is a "
                      "route fault, not a market condition.")

    _verify_ratio(w3, _usdc, _wavax, ME, a.ratio, _ri)

    # ── 5. RE-DEPLOY ───────────────────────────────────────────────────────────
    print(f"\n  [5] RE-DEPLOY {a.side.upper()}")
    if a.side == "curve":
        # Jordan (2026-09-20): "If we get stable switch to curve." A curve is deployed as TWO
        # single-sided legs (see lfj-curve-deploy.sh) because the single-tx two-sided path
        # reverts with CompositionFactorFlawed - we hit it before and it is why the book went
        # single-sided. Same shape, proven paths, one extra tx of gas (~$0.003).
        print(f"\n  [5] RE-DEPLOY {a.shape.upper()} (bid + ask, two single-sided legs)")
        dep = subprocess.run(["bash", os.path.join(HERE, "lfj-curve-deploy.sh"),
                              "--shape", a.shape, "--execute"]
                             + (["--rescue"] if a.rescue else []), cwd=HERE,
                             capture_output=True, text=True)
        # ── CAPTURE THE CAUSE (fixed 2026-09-26) ──────────────────────────────────────────────
        # This ran WITHOUT capture_output, so the deploy's own output was not preserved by
        # anything that logs. On 2026-09-26 01:10 a curve re-deploy failed and the record held
        # exactly one line — "curve exit=1" — with no leg output, no revert reason and no way to
        # tell which leg broke. Catching a failure is not the same as PRESERVING its cause.
        _DEP = (dep.stdout or "") + (dep.stderr or "")
        for l in [l for l in _DEP.split("\n") if l.strip()][-12:]:
            print("      " + l.rstrip())
        print(f"      {a.shape} exit={dep.returncode}")
        # ── THIS BRANCH MUST NOT RETURN (fixed 2026-09-23, Sr audit) ──────────────────────────
        # It used to end `return dep.returncode` right here, which skipped BOTH the [6] VERIFY
        # on-chain re-read AND the cooldown write (`st["last_action_ts"]`, §838 below). A
        # curve-labelled book therefore NEVER started its 60-minute cooldown, so the very next
        # 15-minute watchdog pass found no cooldown and re-centred again: withdraw + re-deploy on
        # a healthy IN-RANGE book, forever. That is the observed churn  (log: "bins held 45" ->
        # "[4] WITHDRAW" -> "[5] RE-DEPLOY CURVE" -> "[4] RE-DEPLOY BID-ASK") and the mechanism
        # that twice left the wallet FLAT — `lfj-curve-deploy.sh` fires two independent legs, so
        # when one failed the book stayed half-deployed with nothing to recover it.
        # Found by the Kimi K3 senior audit; verified against this source before applying.
        if dep.returncode != 0:
            print(f"\n  ❌ RE-DEPLOY FAILED (exit {dep.returncode}) — NOT starting a cooldown.")
            print("     A failed re-center must retry on the next sample, not wait an hour.")
            # Name the cause, or say plainly that none was preserved. A record that reads
            # "it failed" and nothing else cannot be acted on tomorrow.
            _errs = [l.strip() for l in _DEP.split("\n")
                     if any(k in l for k in ("❌", "Error", "error", "reverted", "Traceback",
                                             "exit=", "SHORT", "SIMULATION", "NOTHING TO DEPLOY"))]
            if _errs:
                print("     CAUSE (from the deploy's own output):")
                for l in _errs[-8:]:
                    print("       " + l[:190])
            else:
                print("     ⚠️  the deploy printed NO diagnosable cause — that is itself a defect.")
                print("        A failure whose cause is not preserved cannot be fixed from the "
                      "record.")
            return 1
    else:
        print(f"\n  [5] RE-DEPLOY {a.side.upper()}")

        # RATIO PER SIDE (Jordan, 2026-09-21). a.ratio is the ASK ratio -- "keep 70% of the WAVAX raw
        # for the breakout". It is a POSITION instruction for the ask leg ONLY. Passing it to the BID
        # leg made the bid deploy 30% of our USDC and idle the other 70%: on 2026-09-21 a forced
        # re-center deployed $4.53 of $15.11 available. The bid leg is pure buying power -- there is
        # no upside to preserve on it -- so it deploys the full balance MINUS THE GAS RESERVE, which
        # lfj_bid_deploy holds back itself (Jordan, 2026-09-25: "deploy the whole balance" means the
        # whole balance minus the reserve, never the reserve).
        bid_ratio = 1.0 if a.side == "bid" else a.ratio
        dep = subprocess.run([sys.executable, os.path.join(HERE, "lfj_bid_deploy.py"),
                              "--side", a.side, "--near", str(a.near), "--far", str(a.far),
                              "--kind", a.kind, "--ratio", str(bid_ratio),
                              "--execute", "--yes"]
                             + (["--rescue"] if a.rescue else []),
                             capture_output=True, text=True, timeout=420)
        for l in [l for l in dep.stdout.split("\n") if l.strip()][-8:]:
            print("      " + l.strip())

        # ── A FAILED DEPLOY MUST NOT START A COOLDOWN (fixed 2026-09-22) ───────────────────────
        # The verify step below looks for "any position exists" and treats that as success. But the
        # OLD position is still sitting there when the deploy fails, so a failed re-center read as a
        # successful one and started a 60-minute cooldown — the position stayed out of range and the
        # script refused to retry for an hour, every hour. That is how Dadrian's book sat idle for
        # 340+ minutes while the log said "cooldown, not acting".
        if dep.returncode != 0:
            print(f"\n  ❌ RE-DEPLOY FAILED (exit {dep.returncode}) — NOT starting a cooldown.")
            print("     A failed re-center must retry on the next sample, not wait an hour.")
            for l in dep.stdout.split("\n"):
                if any(k in l for k in ("❌", "reverted", "PARTIAL", "exit=")):
                    print("       " + l.strip()[:170])
            return 1

    # ── 6. VERIFY ──────────────────────────────────────────────────────────────
    print("\n  [6] VERIFY (re-read the chain)")
    time.sleep(4)
    n2 = settled_active(c)
    ids2, tot2 = scan(c, n2)
    if tot2 > 0 and ids2:
        inside2 = min(ids2) <= n2 <= max(ids2)
        print(f"      ✅ position re-opened — {len(ids2)} bins, band {min(ids2)}..{max(ids2)}, spot {n2}")
        print(f"      {'✅ band adjacent to spot' if inside2 else '⚠️ band drifted from spot'}")
        st["out_streak"] = 0
        st["last_action_ts"] = int(time.time())   # start the cooldown
        json.dump(st, open(STATE, "w"))
    else:
        print(f"      ⚠️ no position found after re-deploy — investigate (flat now)")

    # ── GAS TREND, LAST LINE OF THE RUN (Jordan, 2026-09-27) ───────────────────────────────────
    # *"I think the gas trend thing should be at the very bottom because it's not something that's
    # very important to us since it's just showing that you've got enough gas."*
    # A health line, not a decision line — so it goes under everything that describes the book.
    _print_gas_trend(_gp_w3)


if __name__ == "__main__":
    main()
