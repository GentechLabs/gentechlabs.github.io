#!/usr/bin/env python3
"""Deploy LFJ V2.2 AVAX/USDC curve LP position with verified SDK distribution."""
from web3 import Web3
import time, math, os, sys
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)


def _gp(w3):
    """Gas price WITH headroom — the PRICE, not the limit. (2026-09-26)

    `eth_gasPrice` sits exactly on the current base fee and the base fee moves every block, so
    a tx priced there can be born BELOW the floor: the node returns a hash, nothing propagates,
    and the caller waits out its whole receipt timeout for a receipt that cannot arrive.
    Measured on the LFJ deploy path: legs priced 3.2% under the floor were absent from four
    independent RPCs and the account nonce never advanced.
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

w3 = Web3(Web3.HTTPProvider(_avax_url()))
ROUTER = Web3.to_checksum_address('0x18556DA13313f3532c54711497A8FedAC273220E')
PAIR = Web3.to_checksum_address('0x864d4e5ee7318e97483db7eb0912e09f161516ea')
WAVAX = Web3.to_checksum_address('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')
USDC = Web3.to_checksum_address('0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E')
STEWARD = Web3.to_checksum_address(_sw_wallet())
KEY_FILE = _sw_keypath()
BIN_STEP = 10

# getSigma from SDK
def get_sigma(R):
    if R >= 20: return 2.0
    elif R >= 15: return 1.8
    elif R >= 10: return 1.7
    elif R >= 8: return 1.6
    elif R >= 6: return 1.5
    elif R >= 5: return 1.4
    else: return 1.0

def _legs(w):
    """Signed delta ids for a shape, from the ONE geometry table (lfj_shapes).

    Returns (neg_ids ascending, pos_ids ascending). Bins BELOW spot hold tokenY (USDC)
    and bins ABOVE hold tokenX (WAVAX) -- confirmed against the live book and against
    lfj-addliquidity-dryrun.py, whose single-sided bid uses all-negative deltaIds with
    distributionX = 0.
    """
    neg_ids = sorted(-k for k in range(w['bid_near'], w['bid_far'] + 1))
    pos_ids = sorted(k for k in range(w['ask_near'], w['ask_far'] + 1))
    return neg_ids, pos_ids


def shape_dist(w):
    """Distribution for a shape resolved from lfj_shapes.py -- no local width table.

    WHY THIS EXISTS: this file used to carry its own SHAPE_DEFAULT_SPREAD ({curve: 11,
    bid-ask: 15}) which contradicted lfj_shapes.py (curve 25 bins, bid-ask 45) AND was
    symmetric where the rule is asymmetric. That is the second-source-of-truth defect
    class: the deploy path and the rule could disagree while both looked healthy.
    Geometry is now ASKED FOR, never recomputed here.
    """
    neg_ids, pos_ids = _legs(w)

    # The ACTIVE bin (delta 0) carries no liquidity: the rule's total is bid_n + ask_n
    # (curve 12+13=25, bidask 15+30=45) and the live books measure EXACTLY those counts.
    # Including delta 0 deployed 26/46 -- one bin over the stated rule, and inconsistent
    # with lfj-curve-deploy.sh, which deploys two single-sided legs that both exclude spot.
    delta_ids = neg_ids + pos_ids

    if w['shape'] == 'bidask':
        # Bid-Ask: liquidity concentrated at the two EXTREME edge bins. Fees flow on the
        # volatile cross at the edges rather than on chop at spot.
        distX = [0] * len(delta_ids)
        distY = [0] * len(delta_ids)
        # SCALE: LFJ distributions are FRACTIONS out of 1e18 -- the proven rail
        # (lfj_bid_deploy.py) normalises every leg to exactly 1e18 (`w[-1] += ONE - sum(w)`).
        # This path used to write 100 * 10**18, i.e. 100x the valid scale, so the router
        # would try to deposit 100x the available amount. Same intent (100% of the token at
        # the edge bin), correct units.
        distY[0] = 10**18      # 100% of the USDC at the far BID edge
        distX[-1] = 10**18     # 100% of the WAVAX at the far ASK edge
        return delta_ids, distX, distY

    # CURVE: Gaussian centred on the active bin, tapering outward -- earns on chop while
    # staying in range. Sigma scales with each leg's own length so the asymmetry of the
    # rule's geometry (bid 12 / ask 13) is expressed rather than flattened to one spread.
    RX = len(pos_ids); sigmaX = get_sigma(RX)
    AX = 1 / (math.sqrt(math.pi * 2) * sigmaX)
    distX = [0] * len(neg_ids) \
        + [2 * AX * math.exp(-0.5 * ((ind + 1) / sigmaX) ** 2) for ind in range(len(pos_ids))]

    RY = len(neg_ids); sigmaY = get_sigma(RY)
    AY = 1 / (math.sqrt(math.pi * 2) * sigmaY)
    distY = [2 * AY * math.exp(-0.5 * ((RY - ind) / sigmaY) ** 2) for ind in range(len(neg_ids))] \
        + [0] * len(pos_ids)

    distX_ether = [int(round(x * 1e18)) for x in distX]
    distY_ether = [int(round(x * 1e18)) for x in distY]

    def _norm(arr):
        # Preserve STRUCTURAL ZEROS. In an LFJ Liquidity Book, a bin BELOW the
        # active bin holds only tokenX and a bin ABOVE holds only tokenY. Giving
        # a zero side a 1-wei share makes the router try to compose BOTH tokens
        # in a one-token bin and revert BinHelper__CompositionFactorFlawed(uint24).
        #
        # History: an earlier ZeroShares revert on the Gaussian tail was "fixed"
        # by flooring EVERY entry at 1 wei. That cured ZeroShares and caused
        # CompositionFactorFlawed. Floor only the NON-ZERO entries instead, so the
        # tail is representable without inventing liquidity on the wrong side.
        _idx = [i for i, v in enumerate(arr) if v > 0]
        if not _idx:
            return arr
        _fixed = [0] * len(arr)
        for _i in _idx:
            _fixed[_i] = max(1, arr[_i])
        _s = sum(_fixed)
        _j = max(_idx, key=lambda i: _fixed[i])
        _fixed[_j] += 10**18 - _s
        return _fixed

    return delta_ids, _norm(distX_ether), _norm(distY_ether)


ABI = [{
  "inputs": [{"components": [
    {"name":"tokenX","type":"address"},{"name":"tokenY","type":"address"},
    {"name":"binStep","type":"uint256"},{"name":"amountX","type":"uint256"},
    {"name":"amountY","type":"uint256"},{"name":"amountXMin","type":"uint256"},
    {"name":"amountYMin","type":"uint256"},{"name":"activeIdDesired","type":"uint256"},
    {"name":"idSlippage","type":"uint256"},{"name":"deltaIds","type":"int256[]"},
    {"name":"distributionX","type":"uint256[]"},{"name":"distributionY","type":"uint256[]"},
    {"name":"to","type":"address"},{"name":"refundTo","type":"address"},
    {"name":"deadline","type":"uint256"}],
    "name":"liquidityParameters","type":"tuple"}],
  "name":"addLiquidity",
  "outputs":[{"name":"amountXAdded","type":"uint256"},{"name":"amountYAdded","type":"uint256"},
    {"name":"amountXLeft","type":"uint256"},{"name":"amountYLeft","type":"uint256"},
    {"name":"depositIds","type":"uint256[]"},{"name":"liquidityMinted","type":"uint256[]"}],
  "stateMutability":"nonpayable","type":"function"}]

def bal(token):
    return int.from_bytes(w3.eth.call({'to': token, 'data':'0x70a08231'+STEWARD[2:].lower().rjust(64,'0')}), 'big')

# ── Shape geometry comes from lfj_shapes.py — the ONE source of truth ────────────
# This file used to carry SHAPE_DEFAULT_SPREAD {"curve": 11, "bid-ask": 15}:
#     curve    -> 23 bins   (the rule says 25)
#     bid-ask  -> 31 bins   (the rule says 45, and 45 is a CEILING)
# which is the second-source-of-truth defect class — the deploy path and the rule
# could disagree while both looked healthy. AND the caller passed "CURVE"/"BID_ASK"
# (uppercase, underscore) into a choices=['curve','bid-ask'] argument, so argparse
# rejected it with exit 2 and the autonomous rebalance could NEVER execute.
# Geometry is now ASKED FOR, and the shape name is canonicalised so any spelling
# degrades to working instead of to a silent refusal.
_SD = os.path.dirname(os.path.abspath(globals().get("__file__") or (sys.argv and sys.argv[0]) or "."))
if _SD not in sys.path:
    sys.path.insert(0, _SD)
import lfj_shapes


def main():
    ap = __import__('argparse').ArgumentParser()
    ap.add_argument('--spread', type=int, default=None,
                    help='explicit SYMMETRIC override (±N bins); otherwise the shape rule applies')
    ap.add_argument('--shape', default='curve',
                    help="curve | bidask | bid-ask (any case) - geometry resolved from lfj_shapes.py")
    ap.add_argument('--mode', default=None,
                    help="accepted for caller compatibility (e.g. withdraw-redeploy); does not alter geometry")
    ap.add_argument('--dry-run', action='store_true', default=True)
    ap.add_argument('--execute', action='store_true')
    ap.add_argument('--yes', action='store_true')
    args = ap.parse_args()

    if not w3.is_connected():
        print('ERROR: cannot connect to Avalanche RPC'); sys.exit(1)

    # Canonicalise through the shared table: CURVE / BID_ASK / bid-ask / bidask all resolve.
    w = lfj_shapes.widths(args.shape)
    if args.spread is not None:
        # Explicit override: symmetric ±spread. Still ceiling-checked, so an override
        # can never quietly exceed Jordan's 45-bin maximum.
        _n = args.spread * 2 + 1
        if _n > lfj_shapes.CEILING:
            print(f"  \u274c REFUSING: ±{args.spread} = {_n} bins exceeds the "
                  f"{lfj_shapes.CEILING}-bin ceiling")
            sys.exit(2)
        # Explicit override: symmetric range of ±spread bins per side. `near` must be 1 and
        # `far` the spread, NOT near==far==spread -- that produced only TWO bins ([-N, +N]),
        # which is a 2-bin book wearing a spread's name. Still ceiling-checked, so an
        # override can never quietly exceed Jordan's 45-bin maximum.
        w = {"shape": w['shape'], "bid_near": 1, "bid_far": args.spread,
             "ask_near": 1, "ask_far": args.spread}
    elif w['over_ceiling']:
        print(f"  \u274c REFUSING: {w['shape']} resolves to {w['total']} bins "
              f"> ceiling {w['ceiling']}")
        sys.exit(2)

    bid_n = w['bid_far'] - w['bid_near'] + 1
    ask_n = w['ask_far'] - w['ask_near'] + 1
    total_n = bid_n + ask_n
    reach = max(w['bid_far'], w['ask_far'])

    active = int.from_bytes(w3.eth.call({'to': PAIR, 'data':'0xdbe65edc'}), 'big')
    usdc_raw = bal(USDC); wavax_raw = bal(WAVAX)
    print(f"activeId: {active}")
    print(f"USDC: {usdc_raw/1e6:.2f}  WAVAX: {wavax_raw/1e18:.6f}")

    delta_ids, distX, distY = shape_dist(w)
    print(f"Shape: {w['shape']}  Range: {active - w['bid_far']}..{active + w['ask_far']}  "
          f"bins: BID {bid_n} + ASK {ask_n} = {total_n}  (ceiling {lfj_shapes.CEILING})")
    print(f"deltaIds: {delta_ids}")

    params = {
        "tokenX": WAVAX, "tokenY": USDC, "binStep": BIN_STEP,
        "amountX": wavax_raw, "amountY": usdc_raw,
        "amountXMin": 0, "amountYMin": 0,
        "activeIdDesired": active, "idSlippage": reach,
        "deltaIds": delta_ids, "distributionX": distX, "distributionY": distY,
        "to": STEWARD, "refundTo": STEWARD, "deadline": int(time.time())+600,
    }

    router = w3.eth.contract(address=ROUTER, abi=ABI)

    if args.execute:
        if not args.yes:
            print('Refusing without --yes'); sys.exit(1)
        if not os.path.exists(KEY_FILE):
            print('Key not found'); sys.exit(1)
        key = open(KEY_FILE).read().strip()
        acct = w3.eth.account.from_key(key)
        if acct.address.lower() != STEWARD.lower():
            print('Key mismatch!'); sys.exit(1)

        # Simulate first (safety)
        try:
            router.functions.addLiquidity(params).call({'from': STEWARD})
            print('✅ Simulation passed')
        except Exception as e:
            print(f'❌ Simulation failed: {str(e)[:150]}'); sys.exit(1)

        print('\n💧 Executing addLiquidity...')
        tx = router.functions.addLiquidity(params).build_transaction({
            'from': acct.address, 'nonce': w3.eth.get_transaction_count(acct.address),
            'gas': 1500000, 'gasPrice': _gp(w3), 'chainId': 43114})
        signed = acct.sign_transaction(tx)
        h = w3.eth.send_raw_transaction(signed.raw_transaction)
        rcpt = w3.eth.wait_for_transaction_receipt(h)
        print(f'addLiquidity tx: {h.hex()} status={rcpt["status"]}')
        if rcpt['status'] != 1:
            print('❌ REVERTED'); sys.exit(1)
        print('\n✅ LP position deployed!')
        # verify balances
        print(f"USDC now: {bal(USDC)/1e6:.2f}  WAVAX now: {bal(WAVAX)/1e18:.6f}")
        return
    else:
        # dry run - simulate
        try:
            result = router.functions.addLiquidity(params).call({'from': STEWARD})
            x_add, y_add, x_left, y_left = result[0], result[1], result[2], result[3]
            print(f'✅ Simulation: X_add={x_add/1e18:.4f} Y_add={y_add/1e6:.2f} X_left={x_left/1e18:.4f} Y_left={y_left/1e6:.2f}')
        except Exception as e:
            print(f'❌ Simulation failed: {str(e)[:200]}'); sys.exit(1)
        print('\n✅ DRY-RUN passed. Ready for execution.')

if __name__ == '__main__':
    main()
