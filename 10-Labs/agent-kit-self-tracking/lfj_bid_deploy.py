#!/usr/bin/env python3
"""
lfj_bid_deploy.py — SINGLE-SIDED USDC bid on the LFJ WAVAX/USDC Liquidity Book.

Built from the pattern PROVEN by lfj-addliquidity-dryrun.py, which clears the
router (both scenarios simulated successfully). The parameters that matter:

    deltaIds        ALL NEGATIVE   (bins below spot)
    distributionX   ALL ZEROS      (deposit no tokenX)
    amountX         0              (single-sided)
    idSlippage      0              (do not hunt for a range)

Why single-sided: a two-sided deposit forces the router to compute a composition
factor, which reverts BinHelper__CompositionFactorFlawed. With one token there is
no composition to compute, so the failure path is bypassed entirely.

This is the "USDC on the left side" shape: USDC sits in the bins below spot and
converts to WAVAX as price falls through them.

REVERTS the earlier X/Y swap made to deploy_lp_curve.py — that change was wrong;
bins below spot hold tokenY, as the working code already had.
"""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from web3 import Web3
from eth_account import Account
from steward_identity import wallet as sw_wallet, key_path as sw_keypath
import steward_identity as _SI   # ONE signing path: asserts the tenant + decrypts


def _gp(w3):
    """Gas price WITH headroom — the PRICE, not the limit. (2026-09-26)

    The raw `eth_gasPrice` sits exactly on the current base fee, and on Avalanche the base fee
    moves every block, so a tx priced there can be born BELOW the floor: the node hands back a
    hash, the tx never propagates to any validator, and the caller then waits out its whole
    receipt timeout for a receipt that cannot arrive.

    Measured live on dadrian (09:51Z): legs built at 0.097612 nAVAX against a 0.100841 base fee
    were absent from four independent RPCs, the account nonce never advanced, ~$28 sat idle,
    and the watchdog retried into the same wall every 5 minutes from 08:09Z onward.
    """
    try:
        import gas_reserve as _G
        return _G.gas_price_wei(w3)
    except Exception:                       # fallback is still strictly better than raw
        return int(w3.eth.gas_price * 1.3)

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

RPC=_avax_url()
RPC2="https://avalanche.drpc.org"
# RPC failover (2026-09-22). The fixed primary began returning 429 and this deploy path died
# mid-curve, leaving a HALF-BUILT position — "a directional position wearing a curve's name".
# A rate-limited endpoint must never be able to do that. Probe, take the first that answers.
RPC_CANDIDATES = [
    "https://avalanche-c-chain-rpc.publicnode.com",
    "https://avalanche.drpc.org",
    "https://rpc.ankr.com/avalanche",
    _avax_url(),
]


def _live_rpc(exclude=None):
    """First candidate that answers eth_blockNumber. Never returns `exclude`."""
    for _u in RPC_CANDIDATES:
        if exclude and _u == exclude:
            continue
        try:
            if Web3(Web3.HTTPProvider(_u, request_kwargs={"timeout": 20})).eth.block_number:
                return _u
        except Exception:
            continue
    return RPC_CANDIDATES[0]
WAVAX=Web3.to_checksum_address("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7")
USDC =Web3.to_checksum_address("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E")
ROUTER=Web3.to_checksum_address("0x18556DA13313f3532c54711497A8FedAC273220E")
PAIR =Web3.to_checksum_address("0x864d4e5ee7318e97483db7eb0912e09f161516ea")
ME=Web3.to_checksum_address(sw_wallet())
ONE=10**18

ABI=json.loads('''[{"inputs":[{"components":[
{"name":"tokenX","type":"address"},{"name":"tokenY","type":"address"},
{"name":"binStep","type":"uint256"},{"name":"amountX","type":"uint256"},
{"name":"amountY","type":"uint256"},{"name":"amountXMin","type":"uint256"},
{"name":"amountYMin","type":"uint256"},{"name":"activeIdDesired","type":"uint256"},
{"name":"idSlippage","type":"uint256"},{"name":"deltaIds","type":"int256[]"},
{"name":"distributionX","type":"uint256[]"},{"name":"distributionY","type":"uint256[]"},
{"name":"to","type":"address"},{"name":"refundTo","type":"address"},
{"name":"deadline","type":"uint256"}],"name":"liquidityParameters","type":"tuple"}],
"name":"addLiquidity","outputs":[{"name":"amountXAdded","type":"uint256"},
{"name":"amountYAdded","type":"uint256"},{"name":"amountXLeft","type":"uint256"},
{"name":"amountYLeft","type":"uint256"},{"name":"depositIds","type":"uint256[]"},
{"name":"liquidityMinted","type":"uint256[]"}],"stateMutability":"nonpayable","type":"function"}]''')
PAIR_ABI=json.loads('[{"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},{"name":"getBinStep","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint16"}]},{"name":"getPriceFromId","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],"outputs":[{"type":"uint256"}]}]')
ERC=json.loads('[{"name":"balanceOf","type":"function","stateMutability":"view","inputs":[{"type":"address"}],"outputs":[{"type":"uint256"}]},{"name":"allowance","type":"function","stateMutability":"view","inputs":[{"type":"address"},{"type":"address"}],"outputs":[{"type":"uint256"}]},{"name":"approve","type":"function","stateMutability":"nonpayable","inputs":[{"type":"address"},{"type":"uint256"}],"outputs":[{"type":"bool"}]}]')

def weights(n, kind):
    """Per-bin weights for a leg. `last entry = the bin CLOSEST to the active bin`.

    ── THE TWO SHAPES ARE OPPOSITE, AND BOTH WERE CALLED "bidask" (fixed 2026-09-23) ──
    This function had ONE non-uniform shape and it was heavier toward the bin NEAREST spot —
    a BELL — while its comment called that "bidask" and lfj_shapes.py describes a bid-ask as
    "pays at the EDGES, U-shape". Two files, two contradictory definitions, and this one won
    every time because lfj-curve-deploy.sh never passed --kind, so it always took the default.
    Net effect: EVERY book ever deployed was centre-heavy, and the U was never built once.

    Jordan found it by eye, looking at his own page: "it's not showing that it's the opposite
    of the alligator, where it's bigger on the edges." He was reading the chain correctly.

        curve   -> heavier NEAR spot  (the BELL: earns on chop around the centre)
        bidask  -> heavier AWAY from spot (the U: pays at the edges when price swings wide)
    """
    if kind=="uniform":
        w=[ONE//n]*n; w[-1]+=ONE-sum(w); return w
    if kind=="curve":
        # BELL: least at the far edge, most at the bin nearest spot.
        raw=[i+1 for i in range(n)]
    else:
        # U: most at the FAR edge, least at the bin nearest spot. A wide swing pays here —
        # which is the whole reason a bid-ask is the volatile-market tool.
        raw=[n-i for i in range(n)]
    t=sum(raw); w=[ONE*r//t for r in raw]; w[-1]+=ONE-sum(w); return w

def _ceiling_check(n):
    """(ok, why) — Jordan's 45-bin ceiling, computed from the ACTUAL arguments.

    ── THE CEILING WAS ENFORCED ONLY IN A FILE THIS ONE DOES NOT GO THROUGH (fixed 2026-09-25) ─
    lfj-curve-deploy.sh computes BID_N + ASK_N against lfj_shapes.CEILING and refuses over 45
    bins ("the widest I could see us going for a bid-ask... a maximum of 45 bins"). But THIS file
    is the only thing that actually places a leg, and it had no check at all -- while its own
    defaults for a bid leg are `--near 5 --far 60`, i.e. 56 bins. Any caller that omits --far (a
    hand run, a future tool, any wrapper that forgets) deploys WIDER than the rule allows and
    nothing says so. This is the "rule re-implemented in another file that can act" defect with
    the enforcement in the wrong file: a rule that one path enforces and the acting path does not
    is a rule that is not in force.

    The ceiling is read from lfj_shapes (ONE source of truth); the literal 45 is only a fallback
    so an import error cannot disable the refusal.
    """
    try:
        import lfj_shapes as _ls
        cap = _ls.CEILING
    except Exception:
        cap = 45
    if n > cap:
        return False, (f"{n} bins exceeds the {cap}-bin ceiling "
                       f"(Jordan 2026-09-21: 'a maximum of 45 bins')")
    return True, f"{n} bins <= ceiling {cap}"


def _gas_floor(a, w3, me):
    """(gas_reserve module, reserve_info, token_usd, token_decimals) — or EXIT.

    ══ THE GAS FLOOR — A FLOOR THE NO-IDLE RULE MUST RESPECT (Jordan, 2026-09-25) ═══════════════
    Jordan, re-stating the rule for the third time: "keeping like maybe 10 cents of the natural
    whatever the coin is for gas... You still got to have a little bit of gas."

    THIS FILE IS THE ONLY THING THAT ACTUALLY PLACES A LEG, so this is the one place the reserve
    can be spent. It used to hold back a hardcoded FLOOR_USDC = $0.20 (and FLOOR_WAVAX = 0.0, on
    the reasoning "gas is paid in AVAX, not WAVAX") — a number nobody could tie to the live gas
    price, and on the wrong side of the book: the treasury buys its gas by ROTATING a sliver of its
    own loose book, so a wallet left 100% deployed has nothing to rotate. The floor now comes from
    gas_reserve.py (ONE implementation, measured LIVE) and it is held back on BOTH sides.

    ENFORCEMENT IS TWO LAYERS, ON PURPOSE:
      1. the leg may never deploy into the reserve (cap_deploy: "the whole balance MINUS the
         reserve") — so the wallet is never left with nothing loose;
      2. the WALLET must be at/above the floor for the deploy to start at all, because this leg's
         own gas is drawn from the same reserve.
    A refusal here is FREE (nothing is built, nothing is signed) — unlike refusing after a
    withdraw, which is how a book gets stranded out of the pool.

    FAIL CLOSED: if the floor cannot be measured, the deploy does not run. `--rescue` (or
    STEWARD_GAS_FLOOR_BYPASS=1) is the ONLY way past it, and it says so out loud.
    """
    try:
        import gas_reserve as GR
    except Exception as e:
        print(f"  ❌ REFUSING TO DEPLOY — the gas floor could not be loaded "
              f"({type(e).__name__}: {e}).")
        print(f"     A reserve that cannot be sized cannot be held back; deploying blind is how the")
        print(f"     reserve got spent in the first place (2026-09-25).")
        sys.exit(7)
    try:
        info = GR.reserve_info(tenant=_SI.tenant(), w3=w3,
                               balance_avax=w3.eth.get_balance(me) / 1e18)
    except Exception as e:
        info = {"measured": False, "unmeasured_reason": f"{type(e).__name__}: {e}"}
    # USDC is $1. WAVAX is priced at the live AVAX/USD the SAME reserve read returned (they differ
    # by a few bps, and this is a FLOOR, so the tiny conversion error only holds back more).
    token_usd = 1.0 if a.side == "bid" else float(info.get("avax_usd") or 0.0)
    dec = 6 if a.side == "bid" else 18
    try:
        cost_avax = (GR.RECENTER_GAS * w3.eth.gas_price) / 1e18
    except Exception:
        cost_avax = 0.0
    ok, why = GR.gate(info, cost_avax=cost_avax, action=f"{a.side} leg deploy", bypass=a.rescue)
    print(f"  {GR.floor_line(info)}")
    if not ok:
        print(f"  ❌ REFUSING TO DEPLOY — {why}")
        print(f"     The reserve pays for the NEXT swap or re-deploy; deploying it is exactly how")
        print(f"     the book was left out of the pool with nothing to fix it (2026-09-25).")
        print(f"     `python3 gas_reserve.py --plan` prints the swap that restores it.")
        print(f"     A genuine re-entry of a stranded book can still be forced with --rescue.")
        sys.exit(7)
    return GR, info, token_usd, dec


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--near", type=int, default=None, help="closest bin offset from spot")
    ap.add_argument("--far",  type=int, default=None, help="furthest bin offset from spot")
    ap.add_argument("--kind", choices=["uniform","curve","bidask"], default="bidask")
    ap.add_argument("--side", choices=["bid","ask"], default="bid",
                    help="bid = USDC below spot; ask = WAVAX above spot")
    ap.add_argument("--ratio", type=float, default=1.0,
                    help="fraction of the available side-token to deploy (bid: of USDC; ask: of WAVAX)")
    ap.add_argument("--slippage", type=int, default=12, help="idSlippage: bins of activeId drift to tolerate")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--rescue", action="store_true",
                    help="RESCUE ONLY: let the deploy proceed even though the wallet is at or "
                         "below the gas floor. Never set automatically — a floor with an "
                         "automatic exception is not a floor. Prints that it did so.")
    a=ap.parse_args()
    if a.near is None: a.near = 5  if a.side=="bid" else 1
    if a.far  is None: a.far  = 60 if a.side=="bid" else 45

    _rpc1=_live_rpc(); _rpc2=_live_rpc(exclude=_rpc1)
    w3=Web3(Web3.HTTPProvider(_rpc1,request_kwargs={"timeout":45}))
    print(f"  rpc {_rpc1}")
    pair=w3.eth.contract(address=PAIR,abi=PAIR_ABI)
    active=pair.functions.getActiveId().call()
    bs=pair.functions.getBinStep().call()
    router=w3.eth.contract(address=ROUTER,abi=ABI)
    usdc=w3.eth.contract(address=USDC,abi=ERC)
    wavaxc=w3.eth.contract(address=WAVAX,abi=ERC)

    n=a.far-a.near+1
    # ── THE CEILING IS CHECKED IN THE FILE THAT DEPLOYS (fixed 2026-09-25) ────────────────────
    # It was only checked in lfj-curve-deploy.sh, while THIS file's own --far default for a bid
    # leg is 60 (56 bins). Refuse before anything is read or signed.
    _ok, _why = _ceiling_check(n)
    if not _ok:
        print(f"  ❌ REFUSING: {_why}")
        print(f"     near={a.near} far={a.far} -- one leg may not exceed Jordan's ceiling.")
        sys.exit(6)

    # ══ THE GAS FLOOR — A FLOOR THE NO-IDLE RULE MUST RESPECT (Jordan, 2026-09-25) ═════════════
    # See _gas_floor() below: it computes the reserve from the LIVE gas price, refuses the deploy
    # when the wallet is at/below it, and returns what this leg must leave loose. It EXITS the
    # process on refusal, so everything after this line runs with the floor verified.
    _GR, _ri, _leg_usd, _leg_dec = _gas_floor(a, w3, ME)
    # GAS FLOOR (Jordan's rule, enforced): the leg deploys everything ABOVE the reserve and
    # nothing inside it. The reserve is a FLOOR ON THE DEPLOYED LEG -- not a hoard: an earlier
    # version held back 50% of the bid leg, which is 2,500x this floor and earned nothing.
    # ── EXACT-AMOUNT MATH (2026-09-21) ────────────────────────────────────────────────────────
    # `int(avail * ratio)` does FLOAT arithmetic on an 18-decimal integer, and it drifts.
    # Measured: WAVAX balance 1926403793234405805 wei, ratio 1.0 -> int(avail * 1.0) =
    # 1926403793234405888 -- 83 wei MORE than the wallet actually holds. The router then tried to
    # pull more than the balance and reverted TokenHelper__TransferFailed(). So "deploy the full
    # balance" could NEVER have worked on the ask path, and the failure looked like an on-chain
    # problem rather than a rounding bug. Ratio is applied as exact integer arithmetic; at
    # ratio >= 1.0 we use the balance itself.
    def _scale(raw, ratio):
        if ratio >= 1.0:
            return raw
        return raw * int(round(ratio * 10**6)) // 10**6

    # ── "THE WHOLE BALANCE MINUS THE RESERVE" (Jordan, 2026-09-25) ────────────────────────────
    # The held-back slice is computed by gas_reserve.cap_deploy() from the LIVE gas price and the
    # LIVE AVAX price. FLOOR_USDC = 0.20 / FLOOR_WAVAX = 0.0 are GONE: a floor that lives in two
    # files is two floors, and the one that ACTS is the one that has to be right. The reserve is
    # held back on BOTH sides -- USDC is what the book rotates into gas, and WAVAX is the gas
    # token's own wrapped form, so either side left at zero is a wallet that cannot pay.
    if a.side=="bid":
        # BELOW spot -> tokenY (USDC). distributionX MUST be zero.
        deltas=[-a.far+i for i in range(n)]
        dy=weights(n,a.kind); dx=[0]*n
        avail=usdc.functions.balanceOf(ME).call()
        amt=_scale(avail, a.ratio)
        amt, _kept, _cap = _GR.cap_deploy(amt, avail, _ri, _leg_usd, _leg_dec, rescue=a.rescue)
        print(f"  reserve kept : {_kept/1e6:,.6f} USDC   ({_cap})")
        ax, ay = 0, amt
    else:
        # ABOVE spot -> tokenX (WAVAX). distributionY MUST be zero.
        # BUG FIX (2026-09-22, found via the hub's shape chart): this read
        # `deltas=[a.near+i for i in range(n)]` -> deltas[-1] = +far = the FURTHEST bin.
        # `weights()` documents "last entry = closest to active", so the heaviest weight landed on
        # the bin FURTHEST from spot — the ask leg was deployed INVERTED. Confirmed on-chain:
        # nearest ask bin $5.66 vs furthest $11.25, while the bid leg correctly ran 245:1 the
        # other way. Ascending offsets here vs descending in the bid branch is the whole bug.
        deltas=[a.far-i for i in range(n)]
        # n==1 makes this check vacuous (deltas[0] IS deltas[-1]) — don't false-trip on it.
        assert n < 2 or abs(deltas[-1]) < abs(deltas[0]), \
            f"ask leg deltaIds must END nearest spot (got {deltas[0]}..{deltas[-1]})"
        dx=weights(n,a.kind); dy=[0]*n
        avail=wavaxc.functions.balanceOf(ME).call()
        amt=_scale(avail, a.ratio)
        amt, _kept, _cap = _GR.cap_deploy(amt, avail, _ri, _leg_usd, _leg_dec, rescue=a.rescue)
        print(f"  reserve kept : {_kept/1e18:,.6f} WAVAX  ({_cap})")
        ax, ay = amt, 0

    print("="*96); print(f"  LFJ SINGLE-SIDED {'ASK (WAVAX above spot)' if a.side=='ask' else 'BID (USDC below spot)'}   shape={a.kind}  {n} bins"); print("="*96)
    # REFUSE A ZERO-AMOUNT DEPLOY. Without this, a wallet below the floor sends a 0-liquidity
    # addLiquidity that either reverts or "succeeds" while depositing nothing -- a mechanism
    # reporting success while doing nothing, which is this treasury's dominant bug class.
    # A deploy that cannot deploy must SAY SO, loudly, and exit non-zero.
    if ax == 0 and ay == 0:
        print(f"  ❌ REFUSING: computed deploy amount is ZERO.")
        print(f"     {_GR.floor_line(_ri)}")
        print(f"     the whole {a.side.upper()} balance ({avail / 10**_leg_dec:,.6f}) is INSIDE the "
              f"reserve, so there is nothing above it to deploy (ratio {a.ratio}).")
        # ONLY when the WALLET is short does the shortfall belong in this message. On a wallet that
        # is comfortably above the floor (jordan's, live) the leg is simply empty, and appending
        # "BELOW THE GAS FLOOR ... SHORT BY 0.000000 AVAX" made a true refusal READ as a false
        # diagnosis — the confident-wrong-diagnosis class this treasury keeps paying for.
        if _ri.get("measured") and not _ri.get("above"):
            print(f"     {_GR.shortfall_text(_ri)}")
            print(f"     Restore the reserve with `python3 gas_reserve.py --plan` (a rotation inside "
                  f"this book, no outside deposit). Do not lower the floor to force a deploy.")
        else:
            print(f"     the wallet itself is ABOVE the floor — this leg is what is empty, so "
                  f"there is nothing to deploy on THIS side (the floor is not the cause, and "
                  f"`--plan` would find nothing to restore).")
        sys.exit(3)
    spot=pair.functions.getPriceFromId(active).call()/2**128*1e18/1e6
    print(f"  spot ${spot:.4f}   activeId {active}   binStep {bs}")
    print(f"  bins  {deltas[0]} .. {deltas[-1]}  ({n} bins)")
    lo=pair.functions.getPriceFromId(active+deltas[0]).call()/2**128*1e18/1e6
    hi=pair.functions.getPriceFromId(active+deltas[-1]).call()/2**128*1e18/1e6
    print(f"  range ${lo:.4f} .. ${hi:.4f}   ({(lo/spot-1)*100:+.2f}% .. {(hi/spot-1)*100:+.2f}% vs spot)")
    print(f"  amountX {ax/1e18:,.6f} WAVAX   amountY {ay/1e6:,.6f} USDC   (single-sided: one side is 0)")
    print(f"  sum(distX) {sum(dx)}  sum(distY) {sum(dy)}   one must be 1e18, other all-zero")
    # Show the allowance for the token this leg actually SPENDS. This printed the USDC allowance
    # on the ask leg -- a green-looking number for a token the ask never touches, which is how a
    # missing WAVAX approval could hide behind a passing readout.
    _tok, _dec = (usdc, 1e6) if a.side=="bid" else (wavaxc, 1e18)
    _al = _tok.functions.allowance(ME,ROUTER).call()
    print(f"  allowance {_al/_dec:,.6f}  ({'USDC' if a.side=='bid' else 'WAVAX'})"
          f"{'' if _al > 0 else '   ❌ ZERO — the router cannot pull this token'}")

    # ── APPROVE IF SHORT, BEFORE SIMULATING (fixed 2026-09-25) ────────────────────────────────
    # WHAT WAS WRONG: this function READ the allowance, PRINTED it, and then simulated anyway.
    # It had NO approve call, and its ERC ABI did not even contain `approve` -- so any leg whose
    # required amount exceeded the standing allowance reverted on EVERY run with
    # "ERC20: transfer amount exceeds allowance", forever. Measured live 2026-09-25:
    # jordan USDC allowance 58.516057 against a leg needing 94.831497 -- a 36.415440 shortfall.
    # The re-center could therefore never land, and 100% of the book sat idle in the wallet while
    # the watchdog retried every 5 minutes and failed every time. The sibling deploy path
    # (gta_avax_lp_execute.py) DOES approve; this one never did. A missing approval is not a
    # market condition and it does not fix itself.
    _need = ax if a.side == "ask" else ay
    # A DUST FLOOR, not `== 0`: the empty-wallet case leaves 7 micro-USDC after the reserve, so
    # an equality test never fires and the leg still simulated a $0.000007 deposit — reporting the
    # LBRouter's custom error 0x9931a6ae(<binId>), which reads like a ROUTING fault and sends the
    # reader hunting one. Under a cent, the gas to deploy costs more than the amount deployed.
    if _need < _dec / 100:
        _tokname = "WAVAX" if a.side == "ask" else "USDC"
        print(f"  ⓘ NOTHING TO DEPLOY — this leg spends {_tokname} and only "
              f"{_need/_dec:,.6f} is loose (the rest is the reserve).")
        print(f"     Not a failure: the capital is already in the pool, or the other leg moved it.")
        sys.exit(0)
    if _al < _need:
        print(f"  ⚠️  SHORT — this leg spends {_need/_dec:,.6f} and only "
              f"{_al/_dec:,.6f} is approved (short {(_need-_al)/_dec:,.6f}). "
              f"The router CANNOT pull this token.")
        if not (a.execute and a.yes):
            print(f"  (dry-run — would approve {_need/_dec:,.6f} to the router, then retry. "
                  f"The simulation below WILL fail until that approval exists.)")
        else:
            try:
                # HEADROOM, NOT THE EXACT SPEND. (2026-09-26)
                # Approving exactly `_need` is a ZERO-HEADROOM APPROVAL, and it is the same defect
                # class as a zero-headroom gas price -- measured on this system twice in one day.
                # The approve and the pull are two different readings of a market that moves
                # between them: `addLiquidity` sizes its pull from the token amounts, and ANY
                # upward drift (a recomputed amount, a bin the activeId crossed, the other leg
                # landing first) makes the pull exceed an exact allowance. WAVAX answers a short
                # pull by REVERTING, which the router reports as
                #   TokenHelper__TransferFailed()  ->  0x32e2717a
                # -- a message that names the token helper and sends the reader hunting a token
                # bug that does not exist. Live proof 2026-09-26: dadrian's ask leg approved
                # exactly 0.051992 and reverted with 0x32e2717a; minutes later the SAME leg
                # simulated clean against an allowance that had slack.
                # The allowance is a CEILING, not a spend, so approving the wallet's FULL balance
                # cannot over-spend: the router pulls only what the pool needs and the balance is
                # the hard cap. Same doctrine as _gp() -- never price an action at the floor.
                _bal = _tok.functions.balanceOf(ME).call()
                # ── ZERO HEADROOM, LIVE AGAIN (fixed 2026-09-28) ─────────────────────────────────
                # `max(_need, _bal)` looks like headroom but collapses to EXACTLY the spend on the
                # one case that matters most: when the wallet's whole balance IS the amount being
                # deployed, `_bal == _need`, so the "headroom" is zero. Measured live 2026-09-28 on
                # dadrian's re-entry — his entire 35.271333 USDC was the leg, the approve granted
                # exactly 35.271333, and the next `estimate_gas` reverted
                #   "ERC20: transfer amount exceeds allowance".
                # The bid leg died, the ask leg landed, and his book was left HALF-BUILT — a
                # one-sided position wearing a curve's name, the exact state the rebalance guard
                # exists to prevent, produced by the recovery path itself.
                # The doctrine below is right and was applied one step short: the allowance is a
                # CEILING and the BALANCE is the hard cap, so granting headroom ABOVE the balance
                # cannot over-spend — but granting exactly the balance gives the router nothing to
                # absorb the drift between pricing the leg and pulling it.
                # So: 5% over the requirement AND at least 2x the balance. Never exact.
                _appr = max(int(_need * 1.05) + 1, _bal * 2)
                _ac = _tok.functions.approve(ROUTER, _appr)
                _ap = _ac.build_transaction({
                    "from": ME, "nonce": w3.eth.get_transaction_count(ME),
                    "gasPrice": _gp(w3), "chainId": w3.eth.chain_id, "value": 0})
                _ap["gas"] = int(_ac.estimate_gas({"from": ME}) * 1.3)
                _ah = w3.eth.send_raw_transaction(
                    Account.sign_transaction(_ap, _SI.signing_key()).raw_transaction)
                print(f"  APPROVE SENT {_ah.hex()}")
                _ar = w3.eth.wait_for_transaction_receipt(_ah, timeout=120)
                if _ar.status != 1:
                    print(f"  ❌ APPROVE REVERTED ({_ah.hex()}) — refusing to deploy a leg "
                          f"whose token cannot be pulled.", file=sys.stderr)
                    sys.exit(6)
                # RE-READ — and do NOT trust a single read. A node that has not yet applied the
                # approve answers with the OLD value, and an unapplied read is INDISTINGUISHABLE
                # from an approve that did nothing. Confirmed live 2026-09-26: dadrian's ask-leg
                # approve was mined (the allowance later read 0.920865) but the immediate re-read
                # returned 0.000000, so the leg refused with exit 6 and left a HALF-BUILT book --
                # bid only -- which then reported "65.2% idle capital" and 0.0% fee efficiency.
                # The fail-closed was right; the ONE-SHOT read was the bug. Poll the block the
                # approve was mined in until the chain's answer actually moves.
                _al = 0
                _t0 = time.time()
                while time.time() - _t0 < 75:
                    try:
                        _al = _tok.functions.allowance(ME, ROUTER).call(
                            block_identifier=_ar.blockNumber)
                    except Exception:
                        try:
                            _al = _tok.functions.allowance(ME, ROUTER).call()
                        except Exception:
                            _al = 0
                    if _al >= _need:
                        break
                    time.sleep(4)
                _waited = time.time() - _t0
                print(f"  ✅ approved — allowance now {_al/_dec:,.6f} "
                      f"(confirmed after {_waited:.0f}s)")
                if _al < _need:
                    print(f"  ❌ allowance STILL short 75s after a CONFIRMED approve "
                          f"({_al/_dec:,.6f} < {_need/_dec:,.6f}, tx {_ah.hex()}) — refusing. "
                          f"The approve MINED, so this is a read problem, not a token problem.",
                          file=sys.stderr)
                    sys.exit(6)
            except SystemExit:
                raise
            except Exception as _e:
                print(f"  ❌ approve failed: {type(_e).__name__}: {str(_e)[:160]}",
                      file=sys.stderr)
                sys.exit(6)

    minA = int(ax*0.95) if a.side=="ask" else 0
    minB = int(ay*0.95) if a.side=="bid" else 0
    params=(WAVAX,USDC,bs,ax,ay,minA,minB,active,a.slippage,deltas,dx,dy,ME,ME,int(time.time())+600)

    # SIMULATE FIRST
    try:
        router.functions.addLiquidity(params).call({"from":ME})
        print("\n  ✅ SIMULATION PASSED")
    except Exception as e:
        data = getattr(e, "data", None) or getattr(e, "args", None)
        print(f"\n  ❌ SIMULATION REVERTED: {str(e)[:200]}")
        if data:
            print(f"     revert data: {data}")
        print("  -> not sending")
        # EXIT NON-ZERO (2026-09-21). This returned 0, so the caller read a leg that never
        # deployed as a leg that worked: lfj-curve-deploy.sh checks `$ASK_RC -eq 0` and printed
        # "✅ CURVE LIVE — liquidity both sides of spot" while the ask leg had done NOTHING. A
        # refusal that reports success is worse than a crash, because nobody goes looking.
        sys.exit(4)
    if not (a.execute and a.yes):
        print("  (dry-run — pass --execute --yes to send)")
        sys.exit(5)
    key=_SI.signing_key()
    gas=router.functions.addLiquidity(params).estimate_gas({"from":ME})
    tx=router.functions.addLiquidity(params).build_transaction({
        "from":ME,"nonce":w3.eth.get_transaction_count(ME),"gas":int(gas*1.3),
        "gasPrice":_gp(w3),"chainId":w3.eth.chain_id,"value":0})
    h=w3.eth.send_raw_transaction(Account.sign_transaction(tx,key).raw_transaction)
    print(f"\n  SENT {h.hex()}")

    # ── RECEIPT — a timeout is NOT a failure, and must never be reported as one ───────
    # History: this was an unguarded wait_for_transaction_receipt(..., timeout=200). On
    # 2026-09-22 a timeout killed the script with a traceback, the wrapper read exit=1 as
    # "leg failed" and printed "PARTIAL — a half-built curve is a directional position".
    # The tx was in fact NEVER MINED — but the script could not tell that apart from
    # "mined and I couldn't see it". That distinction is the whole ballgame here: re-running
    # a leg that DID land double-deploys capital. So on timeout, ASK A SECOND RPC before
    # saying anything: mined / pending / absent are three different answers.
    r = None
    try:
        r = w3.eth.wait_for_transaction_receipt(h, timeout=200)
        print(f"  {'SUCCESS' if r.status==1 else 'FAILED'}  block={r.blockNumber}  gas={r.gasUsed}")
    except Exception as _e:
        print(f"  ⚠️ no receipt from the primary node in 200s ({type(_e).__name__}) — "
              f"asking a second RPC before concluding ANYTHING")
        try:
            w3c = Web3(Web3.HTTPProvider(_rpc2, request_kwargs={"timeout": 30}))
            _r2 = None
            try:
                _r2 = w3c.eth.get_transaction_receipt(h)
            except Exception:
                _r2 = None
            if _r2 is not None and _r2.status == 1:
                print(f"  ✅ MINED (2nd RPC) — block={_r2.blockNumber} gas={_r2.gasUsed}")
                print(f"     The primary node was LAGGING. This leg LANDED — do NOT re-run it.")
                r = _r2
            elif _r2 is not None:
                print(f"  ❌ MINED AND REVERTED (2nd RPC) — block={_r2.blockNumber} status={_r2.status}")
                print(f"     The tx is on-chain and failed. Safe to retry after fixing the cause.")
                sys.exit(1)
            else:
                try:
                    _tx = w3c.eth.get_transaction(h)
                    _pending = (_tx.get("blockNumber") is None)
                except Exception:
                    _pending = False
                if _pending:
                    print(f"  ⏳ PENDING in the mempool (2nd RPC) — nonce {tx.get('nonce')} still in flight.")
                    print(f"     Do NOT re-run: the tx may still land and would DOUBLE this leg.")
                    print(f"     Wait, then re-check the tx hash above before doing anything.")
                else:
                    print(f"  🚫 NOT MINED on either node (nonce {tx.get('nonce')} unused).")
                    print(f"     This leg genuinely did NOT happen — safe to re-run.")
                sys.exit(3)
        except SystemExit:
            raise
        except Exception as _e2:
            print(f"  ❓ Could not reach a 2nd RPC either ({type(_e2).__name__}).")
            print(f"     UNKNOWN whether this leg landed. Check the tx hash above on a third")
            print(f"     explorer BEFORE re-running — a blind retry can double the position.")
            sys.exit(3)

    time.sleep(3)
    w3b=Web3(Web3.HTTPProvider(_rpc2,request_kwargs={"timeout":30}))
    print(f"  VERIFY 2nd RPC — USDC now {w3b.eth.contract(address=USDC,abi=ERC).functions.balanceOf(ME).call()/1e6:,.6f}")

if __name__=="__main__":
    main()
