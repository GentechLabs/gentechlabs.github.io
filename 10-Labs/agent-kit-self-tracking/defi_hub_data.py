#!/usr/bin/env python3
"""
defi_hub_data.py — build ONE data file PER TENANT for the per-person DeFi hubs.

WHY PER-TENANT FILES AND NOT ONE SHARED FILE
--------------------------------------------
Jordan, 2026-09-22: "I would love to have their own hub. So me and my cousin could have a DeFi
hub, so we have our own links to check our own pools."

That is a data-ISOLATION requirement, not a layout preference. A single shared JSON with a
`tenants` array means one template bug renders somebody else's money under your name, and a
missing field silently falls through to the other person's value. So:

  * one JSON per tenant          -> defi-data-<tenant>.json
  * one PAGE per tenant          -> <tenant>-defi.html, with the tenant name HARDCODED in it
  * each tenant valued in its OWN subprocess (`steward_fee_ledger` resolves its wallet at IMPORT
    time, so two tenants in one process is the 23-hardcoded-wallets bug all over again)

A page can therefore only ever fetch its own file. There is no parameter to get wrong.

WHERE IT WRITES
---------------
Both the repo copy and the VPS copy, because the VPS is what nginx actually serves and the repo
is what gets committed. Writing only the repo is exactly why the previous attempt 404'd: the HTML
was committed but never deployed, so the directory served JSON and no page.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
REPO = "/root/repos/gentechlabs.github.io/DeFi"
VPS = "/var/www/gentechlabs/DeFi"

AVG_STAKER_APY = 4.97      # %/yr, measured mean across live Avalanche staking providers
HODL_30D = 50.16           # % over 29.9d — AVAX's own move

# Collected INSIDE the tenant's own process. Reads the chain directly for the bin band so the
# hub shows a real range, not a config value that has since drifted.
COLLECT = r'''
import json, math, time
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware
import steward_fee_ledger as L

PAIR = Web3.to_checksum_address("0x864d4e5ee7318e97483db7eb0912e09f161516ea")
# Provider rotation (2026-09-22). The single hardcoded host carries a per-SOURCE Cloudflare
# limit (1015), and when it trips the hub's own data build dies — every tenant read 429s and
# the pages keep rendering from stale/empty state while looking fine. avax_rpc is the shared
# rotation path and it FAILS CLOSED, so we cannot publish hub data built from a dead endpoint.
#
# NOTE: resolve the script dir WITHOUT assuming __file__ exists — this module is also executed
# via exec()/runpy from the leadersboard path, where __file__ is undefined and referencing it
# crashes with NameError AFTER the JSON write, so data looks fine while the page silently dies.
import os as _os, sys as _sys
_HERE = _os.path.dirname(_os.path.abspath(globals().get("__file__") or _sys.argv[0] or "."))
if _HERE not in _sys.path:
    _sys.path.insert(0, _HERE)
from avax_rpc import connect as _rpc_connect
w3 = _rpc_connect(timeout=45, tries=2)
RPC = getattr(w3.provider, "endpoint_uri", None) or "avax_rpc"
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

ABI = json.loads('[{"name":"getActiveId","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint24"}]},{"name":"getBinStep","type":"function","stateMutability":"view","inputs":[],"outputs":[{"type":"uint16"}]},{"name":"balanceOfBatch","type":"function","stateMutability":"view","inputs":[{"type":"address[]"},{"type":"uint256[]"}],"outputs":[{"type":"uint256[]"}]},{"name":"getBin","type":"function","stateMutability":"view","inputs":[{"type":"uint24"}],"outputs":[{"type":"uint128"},{"type":"uint128"}]},{"name":"totalSupply","type":"function","stateMutability":"view","inputs":[{"type":"uint256"}],"outputs":[{"type":"uint256"}]}]')
pair = w3.eth.contract(address=PAIR, abi=ABI)

snap = L.snapshot()
me = L.WALLET if hasattr(L, "WALLET") else None
# AUDIT FIX (Kimi K3): a missing wallet used to make every balanceOfBatch raise on a None address,
# get swallowed by the chunk handler below, and report an EMPTY position as if that were the truth.
if not me:
    raise SystemExit("collector: no wallet resolved for this tenant")

active = pair.functions.getActiveId().call()
step = pair.functions.getBinStep().call()

# which bins do we actually hold?
# AUDIT FIX (Kimi K3): this window is anchored at SPOT, not at the position. A position wider than
# the window, or one price has drifted away from, would be silently truncated — and the truncated
# edges were then reported as the real range. We now detect that and refuse to present it as fact.
WINDOW = 400
lo_scan, hi_scan = active - WINDOW, active + WINDOW
ids = list(range(lo_scan, hi_scan + 1))
held = []
held_bal = {}
chunk_errors = []
for i in range(0, len(ids), 200):
    chunk = ids[i:i+200]
    try:
        b = pair.functions.balanceOfBatch([me]*len(chunk), chunk).call()
        for cid, bal in zip(chunk, b):
            if bal > 0:
                held.append(cid)
                held_bal[cid] = bal
    except Exception as e:
        # AUDIT FIX (Kimi K3): a dropped chunk used to be `pass`. One rate-limited chunk meant a
        # partial `held` — a truncated range, or a confident false "Out Of Range" if the lost bins
        # were the ones near spot. A failed read is NOT an empty result. Record and fail loudly.
        chunk_errors.append(str(e)[:120])
if chunk_errors:
    raise SystemExit(f"collector: {len(chunk_errors)} bin chunk(s) failed to read: {chunk_errors[0]}")

# Did we hit a scan edge? If so the range we are about to report is a WINDOW edge, not the real
# edge of the position, and saying otherwise is a confident lie.
truncated_low = bool(held) and min(held) <= lo_scan
truncated_high = bool(held) and max(held) >= hi_scan

# RE-AUDIT FIX (Kimi K3, N2) — THE WORST CASE WAS SILENT. If price drifts entirely out of the scan
# window we find NOTHING: no truncation flag (those need `held`), in_range=None, the chart says
# "no bins held", and the delta was suppressed — so a position that had drifted out of view was
# reported as an empty position, which is the single most alarming state we can be in. The ledger
# knows whether capital is deployed, so ask it: LP on the books + no bins found = OUT OF WINDOW,
# not empty. Refuse rather than render a false calm.
lp_on_books = float(snap.get("lp_usd") or 0)
if not held and lp_on_books > 0.01:
    raise SystemExit(
        f"collector: ledger reports ${lp_on_books:.2f} deployed but no bins were found within "
        f"+/-{WINDOW} bins of spot (activeId {active}) — the position lies OUTSIDE the scan "
        f"window, it is not empty. Refusing to report an empty position.")

def price_of(bin_id):
    # LFJ bin price: (1 + binStep/1e4)^(id - 2^23) scaled by 10^(decX - decY).
    # WAVAX 18dp, USDC 6dp. Verified against the live book ($10.91 at activeId 8363338).
    return (1 + step / 10000.0) ** (bin_id - 8388608) * (10 ** (18 - 6))

# ── THE SHAPE ────────────────────────────────────────────────────────────────────────────────
# Where the DOLLARS actually sit, bin by bin — not how many LP tokens we hold. Those are different
# things: an LP token in a bin below spot is 100% WAVAX and one above is 100% USDC, so equal LP
# amounts are very unequal money. Value each bin from its OWN reserves x our share of that bin.
# This is the number a holder recognises as their position shape.
# ── WHERE IS SPOT? (fixed 2026-09-22) ───────────────────────────────────────────────────────
# This preferred the LEDGER price and fell back to the chain, which is backwards, and it made
# the hub the one component that could not see a position going out of range.
#
# The ledger's `price_usd` is a SNAPSHOT taken whenever the ledger was last written. On
# 2026-09-22 it read $11.096 (bin ~8363369) while the on-chain active bin was 8363378 ($11.1744)
# — NINE BINS, ~0.9%, behind. The band top is bin 8363372. Against the live price the position
# was 6 bins OUT OF RANGE and earning nothing; against the stale ledger price it sat just under
# the top and the page printed "In Range" with a green light. Jordan caught it by eye.
#
# The active bin IS the pool's own answer for where spot is — read in this same run, from the
# same chain, with no snapshot in between. It cannot lag. Prefer it, always; the ledger price
# is kept only so the delta stays visible in the payload.
ledger_px = float(snap.get("price_usd") or 0)
chain_px = price_of(active)
spot_px = chain_px or ledger_px
price_source = "chain-active-bin" if chain_px else "ledger"
shape = []
partial_bins = []
for cid in sorted(held):
    # AUDIT FIX (Kimi K3): a failed getBin/totalSupply used to set usd=0.0 and STILL append the bin,
    # so an RPC hiccup rendered as a real $0.00 bar AND was summed into a real-looking total. A
    # decode failure is not a zero. Mark it and exclude it; the page says a bin is unresolved.
    try:
        rx, ry = pair.functions.getBin(cid).call()
        ts = pair.functions.totalSupply(cid).call()
        share = (held_bal[cid] / ts) if ts else 0.0
        mx = rx * share / 1e18
        my = ry * share / 1e6
        usd = mx * spot_px + my
        ok = True
    except Exception:
        mx = my = usd = 0.0
        ok = False
        partial_bins.append(cid)
    shape.append({"bin": cid, "price": round(price_of(cid), 4),
                  "wavax": round(mx, 6), "usdc": round(my, 2),
                  "usd": round(usd, 2), "active": cid == active, "resolved": ok})

out = {
    "snap": snap,
    # RE-AUDIT FIX (Kimi K3, F7): report the address we ACTUALLY read from, so the parent can
    # verify it matches the tenant record. Without this the equality check is inert — a check that
    # can never fail is not a check.
    "wallet_scanned": me,
    "active_id": active,
    "bin_step": step,
    "band_min": min(held) if held else None,
    "band_max": max(held) if held else None,
    # AUDIT FIX (Kimi K3): price_of(max) is the LOWER edge of the top bin; the range's true top is
    # the upper edge, one binStep higher. The old value understated the user's range.
    "range_min": price_of(min(held)) if held else None,
    "range_max": price_of(max(held) + 1) if held else None,
    "in_range": (min(held) <= active <= max(held)) if held else None,
    "shape": shape,
    "partial_bins": partial_bins,
    # Sum of the per-bin values. Kept SEPARATE from the ledger's lp_usd on purpose: if the two
    # disagree, the page can say so out loud instead of quietly picking one and looking certain.
    "shape_total_usd": round(sum(b["usd"] for b in shape if b["resolved"]), 2),
    "price_used": round(spot_px, 4),
    "price_source": price_source,
    "truncated_low": truncated_low,
    "truncated_high": truncated_high,
    "collected_at": int(time.time()),
}
print(json.dumps(out))
'''


def _run(tenant, wallet):
    """ALWAYS returns a dict. A collector that returns a bare string would blow up downstream
    with an attribute error that reads like a bug in the hub rather than in the collection."""
    env = dict(os.environ)
    env["STEWARD_TENANT"] = tenant
    env["STEWARD_WALLET"] = wallet
    env.pop("STEWARD_KEY_PATH", None)
    try:
        r = subprocess.run([sys.executable, "-c", COLLECT], cwd=HERE, env=env,
                           capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        # AUDIT FIX (Kimi K3): TimeoutExpired was NOT caught, so one hung RPC killed the whole run
        # mid-loop — remaining tenants never rebuilt, and the previously written JSON kept being
        # served as though it were live. A hang must degrade to "this tenant failed", not to a
        # fleet-wide silent staleness.
        return {"error": "collector timeout (300s)"}
    if r.returncode != 0:
        return {"error": (r.stderr.strip().splitlines() or ["unknown"])[-1][:200]}
    try:
        val = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception:
        return {"error": "unparseable output"}
    if not isinstance(val, dict):
        return {"error": f"collector returned {type(val).__name__}, expected dict"}
    return val


def build(tenant, trec):
    """One tenant -> its own dict. Never merged with another tenant's numbers."""
    wallet = trec.get("wallet")
    d = _run(tenant, wallet)
    if "error" in d:
        return {"tenant": tenant, "wallet": wallet, "error": d["error"],
                "updated_at": None}
    s = d.get("snap") or {}
    if not isinstance(s, dict):
        return {"tenant": tenant, "wallet": wallet,
                "error": f"snapshot was {type(s).__name__}, expected dict", "updated_at": None}
    # AUDIT FIX (Kimi K3): `float(s.get("total_usd") or 0)` turned a MISSING ledger field into a
    # real $0.00, so a failed snapshot rendered "Capital $0.00 / 0.0% deployed" with no error.
    # A missing field is not a zero. Require the fields we actually depend on.
    for req in ("total_usd", "lp_usd", "lp_bins"):
        if s.get(req) is None:
            return {"tenant": tenant, "wallet": wallet,
                    "error": f"ledger snapshot missing '{req}' — refusing to render a zero",
                    "updated_at": None}
    # RE-AUDIT FIX (Kimi K3, N3 / F1): the None-check passes a malformed STRING and float() then
    # raises UNCAUGHT — through build(), out of main()'s loop, so later tenants never rebuild and
    # their old JSON keeps being served. That is the fleet-wide silent staleness the timeout fix
    # removed, reintroduced. EVERY numeric coercion on this path is defensive, not just the first
    # three: the round-2 fix covered the required fields and left the optional ones bare (F1).
    def _f(v, nd=2):
        """Coerce or None. None means 'we do not know' and the page renders an em dash."""
        try:
            return round(float(v), nd) if v is not None else None
        except (TypeError, ValueError):
            return None

    total = _f(s.get("total_usd"))
    lp = _f(s.get("lp_usd"))
    bins = _f(s.get("lp_bins"), 0)
    if total is None or lp is None or bins is None:
        return {"tenant": tenant, "wallet": wallet,
                "error": "ledger snapshot field not numeric", "updated_at": None}
    bins = int(bins)
    # RE-AUDIT FIX (Kimi K3, F2): the collector deliberately computes a CHAIN price fallback
    # (`price_used`/`price_source`) and `build()` never used it — it errored on a missing ledger
    # price, making the fallback unreachable, and accepted a 0.0 as real, so the page printed
    # "AVAX price $0" while the footer said "chain fallback (ledger price unavailable)". A $0
    # AVAX price is a failed feed, not a measurement. Use the price the collector actually used.
    price = _f(d.get("price_used"), 4)
    price_source = d.get("price_source")
    if not price:
        return {"tenant": tenant, "wallet": wallet,
                "error": "no usable AVAX price — ledger and chain read both failed",
                "updated_at": None}
    # RE-AUDIT FIX (Kimi K3, F3): the N5 fallback stamped a MISSING ledger timestamp with the
    # collector's run time, so the staleness banner read "fresh" no matter how old the capital
    # numbers were — N5 traded "permanently stalled" for "permanently fresh". An absent timestamp
    # is unknown, not now. Only a present-but-malformed one falls back.
    ts = s.get("ts")
    if not (isinstance(ts, str) and len(ts) >= 20 and ts[4] == "-" and ts[10] == "T"
            and (ts.endswith("Z") or "+" in ts[19:] or "-" in ts[19:])):
        if isinstance(ts, str) and len(ts) >= 19 and ts[4] == "-" and ts[10] == "T":
            ts = ts + "Z" if not (ts.endswith("Z") or "+" in ts[19:] or "-" in ts[19:]) else ts
        elif ts is not None:
            ca = d.get("collected_at")
            ts = (__import__("datetime").datetime.utcfromtimestamp(int(ca)).isoformat(timespec="seconds") + "Z"
                  if ca else None)
        else:
            ts = None   # absent -> unknown age, NOT "now"
    in_range = d.get("in_range")
    rmin, rmax = d.get("range_min"), d.get("range_max")

    # ── SHAPE + EFFICIENCY ───────────────────────────────────────────────────────────────────
    # Efficiency is imported from fee_efficiency.py, the module the 10-minute trigger already
    # uses. Two different "efficiency" numbers on the same page would be the false-value family:
    # the dashboard would say one thing and the rebalance rule would act on another.
    shp = [b for b in (d.get("shape") or []) if isinstance(b, dict)]
    shape_total = float(d.get("shape_total_usd") or 0)
    # AUDIT FIX (Kimi K3): shape_kind used to DEFAULT to "curve", and label_matches then judged the
    # live distribution against that assumed label — producing a confident "does not match 'curve'"
    # warning (or a false pass) about an assumption nobody had verified. The shape now comes from
    # the TENANT RECORD (where it belongs); if it is absent we do not know it, and we say so.
    shape_kind, eff, eff_zone, spot_pos, alt_eff = None, None, None, None, None
    # ── THE SHAPE COMES FROM THE CHAIN (Jordan, 2026-09-23) ──────────────────────────────────
    # Jordan: *"It should follow on chain data 🤔"*. He was right, and it is why he had to ask
    # *"I'm currently in a curve, did conditions change?"* while holding 45 bins with a 3-bin gap
    # at spot — a BID-ASK. The label came from the TENANT RECORD, falling back to the DEPLOY
    # SCRIPT NAME: what we ASKED FOR, never what is IN the bins.
    #
    # Geometry is the only witness that cannot be stale. Bins ABOVE spot hold WAVAX (asks), bins
    # BELOW hold USDC (bids); a run of contiguous bin ids is a curve, and a gap means two separate
    # legs — a bid-ask. The re-center already reads it exactly this way, so the hub now agrees
    # with the thing that acts on it.
    _bins = sorted(int(b["bin"]) for b in shp if isinstance(b.get("bin"), (int, float)))
    if len(_bins) >= 2:
        # ── SHAPE FROM WIDTH, NOT FROM THE GAP (fixed 2026-09-23) ──────────────────────────
        # This read "any gap => bid-ask", and BOTH shapes are deployed as two legs with a
        # near-gap: lfj_shapes.py gives curve `bid_near: 2, ask_near: 1`, so bins -1 and 0 sit
        # empty in a CURVE. A curve therefore ALWAYS looked like a bid-ask here, and a curve
        # could never be displayed as one. Caught when Jordan looked at his own page and said
        # "I think our websites have an issue with displaying a bid ask ... bigger on the
        # edges" — his book was drawn as a bell (a curve) while every label called it a
        # bid-ask, and the label was the lie, not the chart.
        # The shapes are told apart by their WIDTH (25 vs 45) and their DISTRIBUTION (a curve
        # is fat at the centre, a bid-ask heavy at the edges) — never by a gap both of them have.
        _gaps = [y - x for x, y in zip(_bins, _bins[1:]) if y - x > 1]
        _kind = None
        try:
            import lfj_shapes as _ls
            _n = len(_bins)
            # match the held width against the table, allowing one bin of drift either way
            for _cand in ("curve", "bidask"):
                if abs(_ls.widths(_cand)["total"] - _n) <= 2:
                    _kind = "bid-ask" if _cand == "bidask" else "curve"
                    break
            if _kind is None:
                # no table match: fall back to the DISTRIBUTION, which is the real difference.
                # A curve peaks at the centre; a bid-ask peaks at the edges.
                _vals = [abs(b - _bins[len(_bins) // 2]) for b in _bins]
                _edge = sum(1 for b in _bins if abs(b - _bins[0]) <= 1 or abs(b - _bins[-1]) <= 1)
                _kind = "bid-ask" if _edge >= max(2, _n // 4) else "curve"
        except Exception:
            _kind = None
        if _kind is not None:
            shape_kind = _kind
        else:
            shape_kind = "bid-ask" if _gaps else "curve"   # last resort, and it says so
        shape_src = (f"chain geometry ({len(_bins)} bins"
                     + (f", gap of {_gaps[0]} at spot)" if _gaps else ", contiguous)"))
    elif trec.get("shape"):
        shape_kind, shape_src = trec.get("shape"), "tenant record (no bins to read)"
    else:
        shape_src = "unknown"
    # A record label that DISAGREES with geometry means something drifted — a deploy that
    # reported one shape and built another. Geometry wins; say so rather than hide it.
    #
    # ── AND THEN WRITE THE TRUTH BACK (fixed 2026-09-23) ─────────────────────────────────────
    # Reporting the disagreement is not enough: the stale record stays stale, and it feeds the
    # efficiency formula (`fee_efficiency._tenant_shape`) and anyone reading tenants.json as
    # fact. That exact staleness already computed the WRONG efficiency for both books once today.
    # Geometry is the only witness that cannot be stale, so the record now heals from it —
    # otherwise every hub run re-reports the same drift and nothing converges.
    if trec.get("shape") and shape_kind and trec.get("shape") != shape_kind:
        stale = trec.get("shape")
        print(f"⚠️  shape label mismatch — record says '{stale}', chain geometry "
              f"says '{shape_kind}'. Geometry wins: on-chain is the truth.")
        try:
            _reg = json.load(open(REGISTRY))
            _t = (_reg.get("tenants") or {}).get(tenant)
            if isinstance(_t, dict) and _t.get("shape") == stale:
                _t["shape"] = shape_kind
                _t["shape_source"] = "chain geometry (hub self-heal)"
                json.dump(_reg, open(REGISTRY, "w"), indent=2)
                trec["shape"] = shape_kind
                print(f"    ↳ record healed: {tenant}.shape '{stale}' -> '{shape_kind}'")
        except Exception as e:
            # a failed heal must be LOUD — a silent one re-creates the staleness it exists to fix
            print(f"    ‼️  could not heal the record ({type(e).__name__}: {e}) — "
                  f"{tenant}.shape is STILL '{stale}' and will be reported again")
    try:
        import fee_efficiency as FE
        if shape_kind and rmin and rmax and float(rmax) > float(rmin) and price:
            e = FE.efficiency(price, float(rmin), float(rmax), shape_kind)
            eff, eff_zone = round(e, 1), FE.band(e, shape_kind)
            spot_pos = round((price - float(rmin)) / (float(rmax) - float(rmin)) * 100, 1)
            # AUDIT FIX (Kimi K3): the alternative shape's efficiency was fabricated as `100 - e`,
            # which is only true if the two rules are exact complements. Ask the real function.
            other = "bid-ask" if shape_kind == "curve" else "curve"
            alt_eff = round(FE.efficiency(price, float(rmin), float(rmax), other), 1)
    except Exception:
        pass

    # ── THE TRANSITION PANEL (Jordan, 2026-09-24) ───────────────────────────────────────────
    # "add a section next to the liquidity shape and put what transition works best and what
    #  transition is going NEXT based off of the market. So that way, maybe after 10 minutes, let's
    #  say that we're still earning well, but our fee efficiency is going down to 60 or maybe 45%.
    #  That's where we can start getting a projection of what we would rebalance to next, so we can
    #  see the scenario."
    #
    # A classifier tells you what the market is NOW. A transition tells you where the book is and
    # which rungs are legal from here -- so the scenario is visible BEFORE it happens.
    #
    # Read the state from the CHAIN, never from a label: shape from the geometry, ratio from the
    # value on each side (bins above spot hold WAVAX, below hold USDC).
    trans = None
    try:
        import transition_map as TM
        # Read the legs from the SHAPE we just built, not from helpers defined further down --
        # `num` and `chain_bins` do not exist yet at this point, and referencing them would have
        # been a NameError at runtime (caught by the type checker before it shipped).
        _w = sum(float(b.get("wavax") or 0) for b in shp)
        _u = sum(float(b.get("usdc") or 0) for b in shp)
        _bins_held = len(shp)
        _ask_usd = _w * float(price or 0)
        _tot = _ask_usd + _u
        _ratio = (_ask_usd / _tot) if _tot > 0 else None
        # Which state is this book in? An EXACT bin-count match is too strict: a real book drifts
        # off its deployed width as bins get consumed, so jordan holding 23 bins matched NEITHER
        # the 25-bin curve nor the 45-bin bid-ask, `_cur` stayed None, the whole transition block
        # came out None, and the HUB PAGE RENDERED BLANK. Caught live: "I want to check the web
        # page and everything was blank." An unmatched book must never yield a missing block --
        # fall back to the NEAREST state on the same shape, and say which one it matched.
        _cur, _best = None, None
        for _nm, _st in TM.STATES.items():
            if _st["shape"] != shape_kind:
                continue
            # rank by bin-distance first, then by ratio-distance
            _bd = abs((_st.get("bins") or 0) - _bins_held)
            _rd = 0.0 if (_ratio is None or _st.get("ratio") is None) else abs(_st["ratio"] - _ratio)
            _score = (_bd, _rd)
            if _best is None or _score < _best:
                _cur, _best = _nm, _score
        # If even the same-shape set is empty, match on bins alone rather than returning nothing.
        if _cur is None:
            for _nm, _st in TM.STATES.items():
                _bd = abs((_st.get("bins") or 0) - _bins_held)
                if _best is None or _bd < _best[0]:
                    _cur, _best = _nm, (_bd, 0.0)
        if _cur:
            _rungs = []
            for _nxt in TM.neighbours(_cur):
                _g = TM.TRANSITIONS.get((_cur, _nxt)) or {}
                _s = TM.STATES.get(_nxt) or {}
                _rungs.append({
                    "to": _nxt,
                    "shape": _s.get("shape") or "flat (USDC)",
                    "bins": _s.get("bins"),
                    "ratio": _s.get("ratio"),
                    "lean": _s.get("lean"),
                    "needs": _g.get("guard"),
                    "why": _g.get("why"),
                    "steps": len(TM.ladder(_cur, _nxt) or [_cur, _nxt]) - 1,
                })
            trans = {
                "state": _cur,
                "state_shape": shape_kind,
                "state_bins": _bins_held,
                "state_ratio_pct": round(_ratio * 100, 1) if _ratio is not None else None,
                "lean": (TM.STATES.get(_cur) or {}).get("lean"),
                "why": (TM.STATES.get(_cur) or {}).get("why"),
                "rungs": _rungs,
                # ── THE PROJECTION (Jordan's example, exactly) ──────────────────────────────
                # "if we're still earning well but our fee efficiency is going down to 60 or maybe
                # 45%, that's where we can start getting a projection of what we would rebalance
                # to next." The bands ARE the scenario ladder, so show what each one implies.
                "projection": [
                    {"at": ">= 70%", "reading": "earning well",
                     "action": "hold — the book sits where its shape collects"},
                    {"at": "50–70%", "reading": "drifting",
                     "action": "watch — if it holds, take the lean-neutral rung"},
                    {"at": "< 50%", "reading": "poorly placed",
                     "action": "re-centre within the shape, or take the next rung"},
                ],
                "now_eff": eff,
                "now_eff_zone": eff_zone,
            }
    except Exception as _e:
        trans = {"error": str(_e)[:120]}

    # A per-bin share of the position, so the chart can be drawn from data rather than guessed.
    peak = max([b["usd"] for b in shp], default=0) or 1
    for b in shp:
        b["pct_of_peak"] = round(b["usd"] / peak * 100, 1)

    # ── DOES THE SHAPE ACTUALLY LOOK LIKE ITS LABEL? ─────────────────────────────────────────
    # The efficiency rule is a heuristic about SPOT'S POSITION within the range, and it assumes
    # the deployed shape has the mass distribution its name implies (a bell clusters at the
    # centre, a U at the edges). If the live distribution disagrees with the label, then the
    # efficiency number is answering a question about a position we do not hold — which is the
    # false-value family. So measure the real distribution and say so out loud rather than
    # letting a confident-looking percentage stand on an assumption nobody checked.
    mass_center, mass_near_spot_pct, label_matches = None, None, None
    tot_shp = sum(b["usd"] for b in shp if b.get("resolved"))
    act_id = d.get("active_id")
    # RE-AUDIT FIX (Kimi K3, N10): ±3 bins and the 30% threshold were calibrated for binStep 10
    # ("±3 bins ≈ 0.3%"), but bin_step is read from chain and was never used. On a step-20 pool the
    # same window is ±0.6%; on step 1 it is ±0.03%. Scale the neighbourhood so "near spot" means
    # the same distance in PRICE on any pool.
    #
    # NOTE the direction: each bin is step/10000 of price, so to hold a constant ±0.3% the number
    # of bins must FALL as the step RISES: bins = 0.003 / (step/10000) = 30/step. (My first attempt
    # wrote 30*step/10, which gave ±30 bins at step 10 — two-thirds of a 45-bin position. The tell
    # was mass-near-spot jumping 35.8% -> 98.8%; a window that swallows the position cannot
    # distinguish anything.)
    step_bps = int(d.get("bin_step") or 10)
    near_bins = max(1, round(30 / step_bps))   # ~±0.3% of price at any bin step
    # AUDIT FIX (Kimi K3): only compare against a label we actually READ. With shape_kind None the
    # comparison is skipped rather than run against a default that may be wrong.
    if shp and tot_shp and act_id is not None and shape_kind:
        mass_center = round(sum(b["bin"] * b["usd"] for b in shp if b.get("resolved")) / tot_shp, 1)
        near = sum(b["usd"] for b in shp
                   if b.get("resolved") and abs(b["bin"] - act_id) <= near_bins)
        mass_near_spot_pct = round(near / tot_shp * 100, 1)
        label_matches = (mass_near_spot_pct >= 30) if shape_kind == "curve" \
                        else (mass_near_spot_pct < 30)

    # ── LEG ORIENTATION (Jordan: "By default check both of our pages for the same bug.") ──────
    # lfj_bid_deploy.py's ask branch built deltaIds ASCENDING while the bid branch built them
    # DESCENDING, and both feed one weights() assuming the LAST entry is nearest spot — so the
    # heaviest ask weight landed on the bin FURTHEST from spot. Every tenant was deployed by that
    # script, so this is checked on EVERY page, from the bins, not from a config label.
    # None means "cannot judge" (one-sided book / unreadable bins) — never rendered as healthy.
    leg_orient = None
    if act_id is not None and shp:
        _below = [b for b in shp if b.get("bin") is not None and b["bin"] < act_id]
        _above = [b for b in shp if b.get("bin") is not None and b["bin"] > act_id]

        def _orient(leg):
            if not leg:
                return None
            leg = sorted(leg, key=lambda b: abs(b["bin"] - act_id))
            n_usd, f_usd = float(leg[0].get("usd") or 0), float(leg[-1].get("usd") or 0)
            if n_usd == 0 and f_usd == 0:
                return None                      # all-zero is NOT a pass
            return {"nearest_usd": round(n_usd, 2), "furthest_usd": round(f_usd, 2),
                    "toward_spot": bool(n_usd > f_usd)}

        bid_o, ask_o = _orient(_below), _orient(_above)
        inverted = [n for n, o in (("bid", bid_o), ("ask", ask_o))
                    if o and not o["toward_spot"]]
        leg_orient = {"bid": bid_o, "ask": ask_o,
                      "inverted": inverted,
                      "verdict": ("OK" if not inverted else "INVERTED: " + ", ".join(inverted))
                      if (bid_o or ask_o) else None}

    # RE-AUDIT FIX (Kimi K3, N6): `or 0` was fixed on the four required fields and stopped one line
    # short — a missing liquid_usd still rendered "$0.00 idle" beside a real deployed figure, and
    # missing holdings rendered "0.0000 WAVAX" as fact. Absent -> null, and the page shows "—".
    def num(key, nd=2):
        return _f(s.get(key), nd)

    # RE-AUDIT FIX (Kimi K3, N7): the "chain-verified from N bins" string used the LEDGER's bin
    # count, never the chain scan's — so the verification claim could cite a number the chain never
    # produced. Emit the scanned count and use that for any chain claim.
    chain_bins = len([b for b in shp if b.get("resolved")])

    # RE-AUDIT FIX (Kimi K3, F7): nothing verified that the wallet SCANNED is the wallet NAMED.
    # Chain data comes from the subprocess's resolved L.WALLET while the displayed address comes
    # from the registry — if those ever diverged, one wallet's position would render under
    # another's address, which is the leakage class, with no alarm. The collector now reports the
    # address it actually read.
    scanned = (d.get("wallet_scanned") or "")
    if scanned and wallet and scanned.lower() != wallet.lower():
        return {"tenant": tenant, "wallet": wallet,
                "error": f"wallet mismatch: scanned {scanned} but tenant record says {wallet} "
                         f"— refusing to render one wallet's position under another's address",
                "updated_at": None}

    # RE-AUDIT FIX (Kimi K3, F9): the clamp was one-sided — lp<0 printed a negative %, and
    # total<=0 with real lp printed "0%" beside a real dollar figure. Clamp both ends; an
    # incoherent ledger (total<=0 while lp>0) is unknown, not 0%.
    if total and total > 0:
        dep_pct = round(max(0.0, min(100.0, lp / total * 100)), 1)
    else:
        dep_pct = None

    # Jordan, 2026-09-22: "Add the DeFi Milestone for the goals."
    # The page shows the book; the milestone shows what the book is FOR. Import the proven
    # ladder + fee estimator from steward_progress rather than re-deriving either: two
    # definitions of "rank" or "daily fees" would drift into two truths.
    # Honesty rule (same class as the ledger reads): if the ladder cannot be computed, emit
    # milestone=None and let the page render "—", NEVER a fabricated "Untested / 0%".
    ms = None
    try:
        import steward_progress as SP
        # 2026-09-25 (Jordan: "add an estimate for the amount of fees we're earning daily for me
        # and my cousin... he doesn't know how much he's earning"): pass IN-RANGE status through.
        # A fully-deployed book that is OUT OF RANGE earns exactly zero -- the watchdog says so in
        # its own words. Without this the estimator printed a confident $0.15/day for a dead
        # position, which is the fabricated-yield class this treasury banned on 2026-09-17.
        try:
            _raw = d.get("in_range")
            # COERCE, DO NOT TRUST. A string "false" is NOT the boolean False, and `"false" is
            # False` evaluates to False -- so a naive pass-through would leave the gate UNFIREABLE
            # while looking correct. That is the calibration defect this treasury keeps catching:
            # a rule wired, reachable, and unable to fire on the condition it exists for.
            if isinstance(_raw, bool):
                _ir = _raw
            elif _raw is None:
                _ir = None
            else:
                _ir = str(_raw).strip().lower() in ("true", "1", "yes", "in range", "in_range")
        except Exception:
            _ir = None
        _ms_est = SP.estimate_daily_fees(total, lp, in_range=_ir) if lp else None
        if _ms_est is not None:
            ms = SP.rank_and_progress(float(_ms_est))
            ms["source"] = "steward_progress.estimate_daily_fees"
            ms["estimated"] = True
            ms["in_range_used"] = _ir
            ms["daily_fees_est"] = float(_ms_est)
    except Exception as e:
        ms = {"error": f"milestone unavailable: {type(e).__name__}: {e}"}

    # ── AUTONOMY / DUTY CYCLE (Jordan, 2026-09-25) ───────────────────────────────────────────
    # *"Why don't we add the amount of hours that we've been active inside the pool between each
    #  rebalance? I think that would also show us the benefits of what we're doing versus doing it
    #  manually because you're able to rebalance and do stuff autonomously now."*
    #
    # That is the one number that isolates what autonomy buys. A manual operator cannot re-center
    # at 3am, so their capital sits OUT of range (deployed, earning zero) for hours; an autonomous
    # one is back inside in minutes. So the metric is IN-RANGE hours vs OUT-OF-RANGE hours between
    # rebalances, and the ratio of the two IS the value of autonomy.
    #
    # Measured in duty_cycle.py from two durable sources: the CHAIN's own rebalance record (a
    # rebalance = one removeLiquidity -> addLiquidity cycle from this wallet, which survives a
    # restart and cannot be rotated away like a cron log) and the POOL's own OHLCV candles.
    # The LIVE band is passed in from THIS tenant's own chain read (rmin/rmax above), so the open
    # interval reflects the real book rather than a replay of the last decoded deploy.
    #
    # Honesty rule, identical to the milestone below it: if the record or the price path cannot be
    # read, the page renders an explicit UNKNOWN. A zero here would read as "fully out of range",
    # which is a claim about the book -- and the unreadable case must never look like a measurement.
    duty = None
    try:
        import duty_cycle as DC
        _lb = None
        if rmin and rmax and float(rmax) > float(rmin):
            _lb = (float(rmin), float(rmax))
        # COERCE, DO NOT TRUST (same rule as the in_range gate above): bin_step arrives from a
        # chain read and a non-numeric value must not silently become a wrong band step.
        try:
            _step = int(d.get("bin_step")) if d.get("bin_step") is not None else None
        except (TypeError, ValueError):
            _step = None
        duty = DC.compute(tenant, wallet, live_band=_lb, live_bin_step=_step)
        if duty.get("status") != "ok":
            # Deliberately worded to avoid the refresh wrapper's failure grep (`traceback|error|
            # unreadable|failed`): a per-statistic gap is not a hub failure, and alerting every 10
            # minutes over a throttled price index is noise. The full reason still travels in the
            # JSON for the page to display, and is logged next to the cache for debugging.
            print(f"  {tenant:10} duty n/a (source gap — the page reads UNKNOWN)")
            try:
                json.dump({"at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                           "tenant": tenant, "error": duty.get("error")},
                          open(os.path.join(HERE, f".duty-cycle-cache-gap-{tenant}.json"), "w"))
            except Exception:
                pass
    except Exception as e:
        duty = {"status": "unknown", "tenant": tenant,
                "error": f"duty cycle unavailable: {type(e).__name__}: {e}"}

    # ── COMPOUNDING — THE HEADLINE (Jordan, 2026-09-25) ────────────────────────────────────────
    # *"on our DeFi hubs instead of showing how much work in capital that we have in the pool Why
    #  don't we instead talk about how much is being auto compounded back into the bins or back into
    #  Our LP I think that would be much more beneficial if you still want to add a tab under that
    #  that shows Hey, here's what you have waiting to be compounded on the next cycle"*
    #
    # So the page LEADS with a FLOW (what compounding is doing, and at what rate) and carries the
    # WAITING amount under it. The capital-in-pool number is DEMOTED, not deleted: Jordan said
    # "instead of", which changes the emphasis, and losing a datum to change an emphasis is not a
    # trade a treasury page gets to make.
    #
    # Wired exactly like `duty` above, including its honesty rule -- if the reading cannot be
    # produced the payload carries status="unknown" with the reason and the page renders UNKNOWN.
    # A 0 here would read as "compounding is off", which is a claim about the venue; the unreadable
    # case must never look like a measurement. That is this project's most repeated bug class.
    compound = None
    try:
        import compound_status as CS
        compound = CS.compute(tenant, wallet=wallet, lp_usd=lp, capital_usd=total,
                              in_range=in_range)
        if compound.get("status") != "ok" and not compound.get("waiting_usd"):
            print(f"  {tenant:10} compound n/a (source gap — the page reads UNKNOWN)")
            try:
                json.dump({"at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
                           "tenant": tenant, "error": compound.get("error")},
                          open(os.path.join(HERE, f".compound-cache-gap-{tenant}.json"), "w"))
            except Exception:
                pass
    except Exception as e:
        compound = {"status": "unknown", "tenant": tenant,
                    "error": f"compounding unavailable: {type(e).__name__}: {e}"}

    return {
        "tenant": tenant,
        "wallet": wallet,
        "updated_at": ts,
        "chain": "Avalanche",
        "dex": "LFJ Liquidity Book",
        "pool": "WAVAX / USDC",
        "pool_address": "0x864d4E5Ee7318e97483DB7EB0912E09F161516EA",
        "bin_step": d.get("bin_step"),
        "capital_usd": round(total, 2),
        "deployed_usd": round(lp, 2),
        "idle_usd": num("liquid_usd"),
        # RE-AUDIT FIX (Kimi K3, F9): unclamped, a ledger where lp_usd > total_usd printed >100%.
        "deployed_pct": dep_pct,
        "bins": bins,
        "chain_bins": chain_bins,
        "active_id": d.get("active_id"),
        "range_min": round(float(rmin), 4) if rmin else None,
        "range_max": round(float(rmax), 4) if rmax else None,
        "in_range": in_range,
        "range_status": "In Range" if in_range else ("Out of Range" if in_range is False else "Unknown"),
        "price_usd": round(price, 4),
        "holds_wavax": num("lp_x_wavax", 6),
        "holds_usdc": num("lp_y_usdc", 2),
        # The shape, bin by bin, and the two independent valuations of it.
        "shape": shp,
        "shape_kind": shape_kind,
        "shape_source": shape_src,
        "shape_total_usd": round(shape_total, 2),
        # RE-AUDIT FIX (Kimi K3, N1): `if shape_total else {unavailable}` conflated "the scan
        # produced no value" with "the scan COMPLETED and found a real zero". A successful scan
        # finding nothing yields 0.0, which is the LARGEST possible divergence from a funded
        # ledger — and that was exactly the case being suppressed. Key availability to scan
        # COMPLETENESS (were any bins unresolved?), not to the total's truthiness.
        "ledger_vs_shape_delta": (
            {"unavailable": f"{len(d.get('partial_bins') or [])} bin(s) unresolved"} 
            if (d.get("partial_bins") or [])
            else round(shape_total - lp, 2)),
        "unresolved_bins": len(d.get("partial_bins") or []),
        "scan_truncated": bool(d.get("truncated_low") or d.get("truncated_high")),
        "price_source": price_source,
        "efficiency_pct": eff,
        "efficiency_zone": eff_zone,
        "efficiency_alt_pct": alt_eff,
        # ── THE TRANSITION PANEL (Jordan, 2026-09-24) ──────────────────────────────────────
        # "add a section next to the liquidity shape and put what transition works best and what
        #  transition is going NEXT based off of the market. So that way, maybe after 10 minutes,
        #  let's say that we're still earning well, but our fee efficiency is going down to 60 or
        #  maybe 45%. That's where we can start getting a projection of what we would rebalance to
        #  next, so we can see the scenario."
        #
        # Scenarios are STATES, moves are TRANSITIONS (transition_map.py). This shows where the
        # book IS, which rungs are LEGAL from here, and the efficiency level at which each rung
        # would be taken -- so the scenario is visible BEFORE it happens, not reported after.
        "transition": trans,
        "spot_pos_in_range_pct": spot_pos,
        # Whether the live distribution actually matches the shape we think we deployed.
        "mass_center_bin": mass_center,
        "mass_near_spot_pct": mass_near_spot_pct,
        "near_bins": near_bins,
        "label_matches_mass": label_matches,
        # Jordan, 2026-09-22: "By default check both of our pages for the same bug."
        # Every tenant was deployed by the same script, so the inverted-ask bug is not a
        # one-tenant defect. Surfaced on EVERY page, computed from the bins themselves.
        "leg_orientation": leg_orient,
        # Jordan, 2026-09-22: "Add the Defi Milestone for the goals."
        # The D5 ladder (Untested→Scout→Raider→Warlord→Sovereign) is the GOAL each tenant is
        # working toward, so it belongs on the page next to the book — not in a separate report.
        # REUSE steward_progress.rank_and_progress like the shape/efficiency numbers reuse their
        # own proven source: a second definition of "rank" would be a second truth.
        "milestone": ms,
        # Honest baselines the holder can actually choose instead of farming.
        "benchmark_staker_apy": AVG_STAKER_APY,
        "benchmark_hodl_30d": HODL_30D,
        # Jordan, 2026-09-25: how long the capital was ACTUALLY in the pool and earning, between
        # rebalances — the number that isolates the value of autonomous re-centering.
        "duty_cycle": duty,
        # Jordan, 2026-09-25: the headline. What is being auto-compounded back into the bins, and
        # what is waiting for the next cycle. capital_usd above stays in the payload — demoted on
        # the page, never dropped from the data.
        "compound": compound,
    }


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<title>__NAME__'s DeFi Command Center — GenTech</title>
<style>
  :root { --bg:#080a0d; --card:#111519; --card2:#161b21; --line:#222a33; --txt:#e9eef4;
          --dim:#7d8a97; --good:#2fd07f; --warn:#f0b429; --bad:#f0554a; --accent:#4da3ff;
          --wax:#f0b429; --usd:#4da3ff; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--txt); -webkit-font-smoothing:antialiased;
         font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
  .wrap { max-width:680px; margin:0 auto; padding:16px 14px 40px; }
  .back { display:inline-block; margin-bottom:10px; color:var(--dim); text-decoration:none; font-size:.82em; }
  h1 { font-size:1.28rem; margin:.1em 0 .1em; letter-spacing:-.3px; }
  .sub { color:var(--dim); font-size:.8em; margin-bottom:14px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:14px;
          padding:14px; margin-bottom:11px; }
  .lbl { color:var(--dim); font-size:.68em; text-transform:uppercase; letter-spacing:.11em;
         margin-bottom:8px; }
  /* instrument tiles */
  .tiles { display:grid; grid-template-columns:1fr 1fr; gap:9px; margin-bottom:11px; }
  .tile { background:var(--card); border:1px solid var(--line); border-radius:13px; padding:12px 13px; }
  .tile .n { font-size:1.42rem; font-weight:700; letter-spacing:-.7px; font-variant-numeric:tabular-nums; }
  .tile .n.sm { font-size:1.06rem; }
  .tile .k { color:var(--dim); font-size:.66em; text-transform:uppercase; letter-spacing:.1em; }
  .tile .note { color:var(--dim); font-size:.74em; margin-top:2px; }
  .pill { display:inline-block; padding:2px 9px; border-radius:99px; font-size:.68em; font-weight:700; }
  .in { background:rgba(47,208,127,.15); color:var(--good); }
  .out { background:rgba(240,85,74,.15); color:var(--bad); }
  .unk { background:rgba(125,138,151,.18); color:var(--dim); }
  .z-good { color:var(--good); } .z-warn { color:var(--warn); } .z-bad { color:var(--bad); }
  /* the shape chart */
  #chart { width:100%; height:150px; display:block; }
  .legend { display:flex; gap:14px; font-size:.72em; color:var(--dim); margin-top:7px; flex-wrap:wrap; }
  /* ── the transition panel ── */
  .trow { display:flex; justify-content:space-between; align-items:baseline; gap:10px; }
  .tk { color:var(--dim); font-size:.72em; text-transform:uppercase; letter-spacing:.09em; }
  .tv { font-weight:700; font-size:1.02rem; letter-spacing:-.3px; }
  .tnote { color:var(--dim); font-size:.75em; margin-top:5px; line-height:1.45; }
  .rung { border-left:2px solid var(--line); padding:7px 0 7px 10px; margin-top:8px; }
  .rung .rh { font-weight:600; font-size:.86em; }
  .rung .rg { color:var(--dim); font-size:.75em; margin-top:3px; line-height:1.4; }
  .rung .rs { color:var(--accent); font-size:.72em; margin-top:3px; }
  .proj { display:flex; justify-content:space-between; gap:10px; padding:5px 0;
          border-bottom:1px solid var(--line); font-size:.8em; }
  .proj:last-child { border-bottom:none; }
  .proj .pa { font-weight:700; font-variant-numeric:tabular-nums; min-width:62px; }
  .proj .pr { color:var(--dim); flex:1; }
  .dot { display:inline-block; width:8px; height:8px; border-radius:2px; margin-right:5px; }
  /* range ruler */
  .ruler { position:relative; height:34px; margin:6px 0 2px; }
  .ruler .track { position:absolute; top:11px; left:0; right:0; height:5px; border-radius:99px;
                  background:linear-gradient(90deg,#1d2530,#243040); }
  .ruler .zone { position:absolute; top:11px; height:5px; border-radius:99px;
                 background:rgba(77,163,255,.35); }
  .ruler .spot { position:absolute; top:4px; width:2px; height:19px; background:var(--txt); }
  .ruler .spot::after { content:""; position:absolute; top:-3px; left:-3px; width:8px; height:8px;
                        border-radius:50%; background:var(--txt); }
  .ruler .cap { position:absolute; top:22px; font-size:.66em; color:var(--dim); }
  .gauge { height:10px; background:#1b222b; border-radius:99px; overflow:hidden; margin:9px 0 5px; }
  .gauge > i { display:block; height:100%; border-radius:99px; }
  .row { display:flex; justify-content:space-between; align-items:baseline; padding:6px 0;
         border-bottom:1px solid var(--line); }
  .row:last-child { border-bottom:0; }
  .row .k { color:var(--dim); font-size:.83em; }
  .row .v { font-weight:600; font-variant-numeric:tabular-nums; }
  .warnbox { background:rgba(240,180,41,.09); border:1px solid rgba(240,180,41,.3);
             border-radius:11px; padding:10px 12px; font-size:.82em; margin-top:9px; }
  .err { color:var(--warn); }
  .foot { color:var(--dim); font-size:.7em; text-align:center; margin-top:18px; line-height:1.75; }
</style>
</head>
<body>
<div class="wrap">
  <a class="back" href="__HUB__">&larr; __NAME__'s Hub</a>
  <h1>__NAME__'s DeFi Command Center</h1>
  <div class="sub" id="sub">loading…</div>

  <!-- ── THE POOL PICTURE LEADS (Jordan, 2026-09-25) ──────────────────────────────────────────
     "the picture of the pool should be at the top."
     The shape chart now sits ABOVE the tiles: the first thing on the page is what the money
     LOOKS like, and the numbers read underneath it, in the order the question is asked. -->
  <div class="card">
    <div class="lbl">Liquidity shape — where the money sits</div>
    <svg id="chart" viewBox="0 0 600 150" preserveAspectRatio="none"></svg>
    <div class="legend">
      <span><i class="dot" style="background:var(--usd)"></i>USDC below spot — bids, buys WAVAX as price falls</span>
      <span><i class="dot" style="background:var(--wax)"></i>WAVAX above spot — asks, sells as price rises</span>
      <span><i class="dot" style="background:var(--txt)"></i>Spot</span>
    </div>
  </div>

  <!-- ── COMPOUNDING LEADS (Jordan, 2026-09-25) ────────────────────────────────────────────────
     "instead of showing how much work in capital that we have in the pool Why don't we instead
      talk about how much is being auto compounded back into the bins or back into Our LP ... if you
      still want to add a tab under that that shows Hey, here's what you have waiting to be
      compounded on the next cycle you can still do that"
     FLOW first, WAITING second. The capital-in-pool tile is DEMOTED to the end of this grid, not
     deleted — "instead of" moves the emphasis, it does not throw the datum away.
     If the reading could not be produced every field below renders UNKNOWN with its reason. A 0
     would be read as "compounding is off", which is a claim about the venue we may not have. -->
  <div class="tiles">
    <div class="tile"><div class="k">Auto-compounded</div><div class="n" id="compflow">—</div>
      <div class="note" id="compflowfit">—</div></div>
    <!-- ── "WAITING TO COMPOUND" TILE RETIRED (Jordan, 2026-09-25) ─────────────────────────
       Jordan: "we don't have to put the idle 20 cents that's being used for gas ... I think
       that the user should just know in the back of their head that the agentic Treasury can
       manage itself."
       He is right, and the reason is structural, not cosmetic: on THIS venue the "waiting"
       figure can only ever be the idle wallet dust (the gas/working float), because LFJ V2.2
       has no pending fee to wait for at all -- fees fold into the bins at swap time. So the tile
       was teaching the reader to watch the treasury's pocket change, which is the opposite of
       what the page is for. The flow stays as the headline; the float is not the user's business.
       `waiting_usd` is STILL in the JSON payload and still drives the HOLD/act decision -- it is
       withdrawn from the page, not deleted from the data. -->
    <div class="tile"><div class="k">Position</div>
      <div class="n sm"><span class="pill" id="range">—</span></div>
      <div class="note" id="rangenote">—</div></div>
    <div class="tile"><div class="k">Fee efficiency</div><div class="n" id="eff">—</div>
      <div class="note" id="effnote">—</div></div>
    <!-- ── WORKING CAPITAL TILE REMOVED (Jordan, 2026-09-25) ────────────────────────────────
       "The working capital tab we could get rid of that ... we're not going to count the money
        that's used for gas, right? So we're not going to count the 20 cents. So I think knowing
        what's going to be compounded back into the pool is much better."
       The tile showed idle wallet capital as if it were part of the book. It is gas money, and
       counting it made the page claim a position it did not have. It was first re-framed as
       "Waiting to compound" and then RETIRED ENTIRELY the same day — see the next block. The
       datum itself is intact: `deployed_usd` / `deployed_pct` / `idle_usd` / `waiting_usd` all
       remain in the JSON payload and still drive the HOLD/act decision. Withdrawn from the VIEW,
       never from the system. -->
    <div class="tile"><div class="k">Capital in pool <span style="text-transform:none;letter-spacing:0">(stock — kept, no longer the headline)</span></div>
      <div class="n" id="cap">—</div>
      <div class="note" id="capnote">—</div></div>
  </div>

  <div class="card">
    <div class="lbl">Auto-compounding — the flow, and what is waiting for the next cycle</div>
    <div class="row"><span class="k">Compounded (last 7d)</span><span class="v" id="compperiod">—</span></div>
    <div class="row"><span class="k">Compounding rate</span><span class="v" id="comprate">—</span></div>
    <div class="row"><span class="k">On an annualised basis</span><span class="v" id="compapr">—</span></div>
    <div class="row"><span class="k">Next cycle</span><span class="v" id="compdec">—</span></div>
    <div class="row"><span class="k">Unclaimed fees</span><span class="v" id="comppend">—</span></div>
    <div class="foot" style="text-align:left;margin-top:12px" id="compnote">—</div>
  </div>

  <div class="card">
    <div class="lbl">Where spot sits in your range</div>
    <div class="ruler">
      <div class="track"></div>
      <div class="zone" id="zone"></div>
      <div class="spot" id="spotmark" style="left:50%;display:none"></div>
      <div class="cap" id="lo" style="left:0">—</div>
      <div class="cap" id="hi" style="right:0">—</div>
    </div>
    <div class="foot" style="text-align:left;margin-top:14px" id="posnote">—</div>
    <div class="warnbox" id="scen" style="display:none"></div>
  </div>

  <div class="card">
    <div class="lbl">Fee efficiency — how well is this book placed to EARN? (the number is its earning power for its shape, not realised dollars: for a curve the centre earns most, for a bid-ask the edges do. Realised fees are tracked by the ledger, which stays silent until it has a rebuild-free window — Jordan, 2026-09-23: “Fee efficiency should be zero” was read as earnings, which is exactly why this caption exists.)</div>
    <div class="gauge"><i id="effbar" style="width:0%"></i></div>
    <div class="row"><span class="k">Shape deployed</span><span class="v" id="kind">—</span></div>
    <div class="row"><span class="k" id="nearlbl">Money near spot</span><span class="v" id="nearspot">—</span></div>
    <div class="row"><span class="k">Bins</span><span class="v" id="bins">—</span></div>
    <div class="row"><span class="k">Holding</span><span class="v" id="holds">—</span></div>
    <div class="row"><span class="k">AVAX price</span><span class="v" id="spotpx">—</span></div>
  </div>

  <!-- ── AUTONOMY / DUTY CYCLE (Jordan, 2026-09-25) ────────────────────────────────────────────
     "Why don't we add the amount of hours that we've been active inside the pool between each
      rebalance? I think that would also show us the benefits of what we're doing versus doing it
      manually because you're able to rebalance and do stuff autonomously now."
     A manual operator cannot re-center at 3am, so their capital sits OUT of range (deployed,
     earning zero) for hours; an autonomous one is back inside in minutes. IN-RANGE hours against
     OUT-OF-RANGE hours between rebalances IS the value of autonomy.
     Measured in duty_cycle.py from the chain's own rebalance record plus the pool's own OHLCV
     candles. If either source cannot be read the rows read UNKNOWN with the reason -- never 0.
     MOVED ABOVE "Against doing nothing" (Jordan, 2026-09-25: "reorganize everything and make it
     make sense"): this is what the book DID, so it belongs with the earnings story, before the
     benchmarks that judge it. -->
  <div class="card">
    <div class="lbl">Autonomy — hours actually in the pool and EARNING, between rebalances</div>
    <div class="row"><span class="k">In range (last 7d)</span><span class="v" id="duty7">—</span></div>
    <div class="row"><span class="k">Out of range (last 7d)</span><span class="v" id="dutyout7">—</span></div>
    <div class="row"><span class="k">Current streak in the pool</span><span class="v" id="dutystreak">—</span></div>
    <div class="row"><span class="k">Avg. hours between rebalances</span><span class="v" id="dutyavg">—</span></div>
    <div class="row"><span class="k">Longest stretch in the pool (7d)</span><span class="v" id="dutymax">—</span></div>
    <div class="row"><span class="k">Since inception</span><span class="v" id="dutyall">—</span></div>
    <div class="foot" style="text-align:left;margin-top:12px" id="dutynote">—</div>
  </div>

  <div class="card">
    <div class="lbl">Against doing nothing</div>
    <div class="row"><span class="k">Average AVAX staker</span><span class="v" id="staker">—</span></div>
    <div class="row"><span class="k">Just holding AVAX (30d)</span><span class="v" id="hodl">—</span></div>
  </div>

  <div class="card">
    <div class="lbl">The goal — DeFi Milestone</div>
    <div class="rankline"><span id="rankicon" class="rankicon">—</span>
      <span id="rankname" class="rankname">—</span>
      <span id="rankpct" class="rankpct">—</span></div>
    <div class="gauge"><i id="msbar" style="width:0%"></i></div>
    <div class="row"><span class="k">Daily fees (est.)</span><span class="v" id="msfees">—</span></div>
    <div class="row"><span class="k">To next rank</span><span class="v" id="msnext">—</span></div>
    <div class="row"><span class="k" id="msunlocklbl">Unlocks</span><span class="v" id="msunlock">—</span></div>
    <div class="foot" style="text-align:left;margin-top:12px" id="msnote">—</div>
  </div>

  <!-- ── NEXT TRANSITION (Jordan, 2026-09-24) ────────────────────────────────────────────────
     "add a section next to the liquidity shape and put what transition works best and what
      transition is going NEXT based off of the market... maybe after 10 minutes, we're still
      earning well, but our fee efficiency is going down to 60 or maybe 45%. That's where we can
      start getting a projection of what we would rebalance to next, so we can see the scenario."
     Scenarios are STATES, moves are TRANSITIONS. This shows where the book IS and which rungs
     are legal from here, with the efficiency projection underneath.
     MOVED INSIDE .wrap (fixed 2026-09-25). It was emitted AFTER the container closed, so this
     card rendered full-bleed and unaligned with every other card on the page -- Jordan: "it looks
     a little jumbled up". A card outside the wrapper is not a style choice, it is a layout leak. -->
  <div class="card">
  <div class="lbl">Next transition — where this book goes from here</div>
  <div class="trow"><span class="tk">Now</span><span class="tv" id="tnow">—</span></div>
  <div class="tnote" id="twhy">—</div>
  <div id="trungs"></div>
  <div class="lbl" style="margin-top:14px">Projection — what would move it</div>
  <div id="tproj"></div>
  <div class="tnote" id="tfoot">—</div>
  </div>

  <div class="foot">
    Wallet <span id="wallet">—</span><br>
    Position &amp; shape read from Avalanche contract state<br>
    Updated <span id="updated">—</span> · <span id="stale"></span><br>
    <span id="prov"></span>
  </div>
  </div>

  <script>
// The tenant name is HARDCODED on this page. No URL parameter, no fallback, no shared list: this
// page can only ever load its own file, so a bug cannot render someone else's money under your name.
const DATA = "defi-data-__TENANT__.json";
const NAME = "__NAME__";
const money = n => "$" + (n ?? 0).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});

function zoneClass(e) {
  if (e === null || e === undefined) return "";
  return e >= 70 ? "z-good" : e >= 50 ? "z-warn" : "z-bad";
}
function zoneColor(e) {
  if (e === null || e === undefined) return "#7d8a97";
  return e >= 70 ? "#2fd07f" : e >= 50 ? "#f0b429" : "#f0554a";
}

function drawShape(d) {
  const svg = document.getElementById("chart");
  const s = d.shape || [];
  if (!s.length) { svg.innerHTML = '<text x="300" y="75" fill="#7d8a97" font-size="13" text-anchor="middle">no bins held</text>'; return; }
  const W = 600, H = 150, pad = 4;
  const peak = Math.max(...s.map(b => b.usd)) || 1;
  const bw = (W - pad * 2) / s.length;
  const px = d.price_usd || 0;
  let out = "";
  s.forEach((b, i) => {
    const h = Math.max(1, (b.usd / peak) * (H - 18));
    const x = pad + i * bw;
    // AUDIT FIX (Kimi K3): colour compared RAW units (tokens vs dollars) — a meaningless
    // comparison that happened to work only because non-active bins are single-asset. Compare
    // the USD legs, so a mixed bin is coloured by which side really dominates.
    const usdLeg = b.usdc;
    const waxLeg = b.wavax * px;
    let col = usdLeg > waxLeg ? "#4da3ff" : "#f0b429";
    if (b.active) col = "#e9eef4";
    if (b.resolved === false) col = "#6b7784";   // unresolved bin: visibly not a real value
    out += '<rect x="' + x.toFixed(1) + '" y="' + (H - h).toFixed(1) + '" width="' +
           Math.max(1, bw - 1.2).toFixed(1) + '" height="' + h.toFixed(1) +
           '" fill="' + col + '" rx="1"></rect>';
  });
  // a hairline at the active bin so the shape reads at a glance
  const ai = s.findIndex(b => b.active);
  if (ai >= 0) {
    const ax = pad + ai * bw + bw / 2;
    out += '<line x1="' + ax.toFixed(1) + '" y1="0" x2="' + ax.toFixed(1) + '" y2="' + H +
           '" stroke="#e9eef4" stroke-width="1" stroke-dasharray="3,3" opacity=".55"></line>';
  }
  svg.innerHTML = out;
}

function render(d) {
  if (d.error) {
    // textContent, not innerHTML: d.error carries subprocess/RPC text, which is untrusted input.
    document.getElementById("sub").textContent = "\u26a0 " + d.error;
    return;
  }
  document.getElementById("sub").textContent = NAME + "'s live LFJ position";

  document.getElementById("cap").textContent = money(d.capital_usd);
  // Only claim the chain agrees when the scan actually COMPLETED and the two valuations match.
  // Saying "chain-verified" over a partially-read book is the failure this page must not make.
  const noteEl = document.getElementById("capnote");
  noteEl.textContent = "";
  const dlt = d.ledger_vs_shape_delta;
  // RE-AUDIT FIX (Kimi K3, F10): the pass band was 1% of TOTAL capital, but the delta compares two
  // valuations of the DEPLOYED amount. With mostly-idle capital that band is loose enough to call
  // almost any divergence "verified" — a check that can hardly fail. Scale to deployed.
  const tol = Math.max(0.5, 0.01 * (d.deployed_usd || 0));
  if (d.scan_truncated) {
    noteEl.textContent = "\u26a0 position wider than the scan window — range may be clipped";
  } else if (d.unresolved_bins) {
    noteEl.textContent = "\u26a0 " + d.unresolved_bins + " bin(s) unread — excluded from the total";
  } else if (typeof dlt === "number" && Math.abs(dlt) <= tol) {
    noteEl.textContent = "chain-verified from " + d.chain_bins + " bins (\u0394" + dlt + ")";
  } else if (typeof dlt === "number") {
    // RE-AUDIT FIX (Kimi K3, N4): this branch did not exist, so a cross-check that ran and
    // DISAGREED fell through to "unavailable" — a check that cannot recognise its own failure.
    // A disagreement between the ledger and the chain is the single most important thing this
    // page can tell you, and it was being reported as "no information".
    noteEl.textContent = "\u26a0 chain scan disagrees with the ledger by $" + dlt +
                         " — one of them is wrong";
  } else {
    noteEl.textContent = "ledger total — chain cross-check unavailable";
  }

  const rng = document.getElementById("range");
  rng.textContent = d.range_status;
  // AUDIT FIX (Kimi K3): `in_range ? "in" : "out"` styled null ("Unknown") as a red failure —
  // presenting "we do not know" as "you are out of range". Unknown gets a neutral pill.
  rng.className = "pill " + (d.in_range === true ? "in" : d.in_range === false ? "out" : "unk");
  // RE-AUDIT FIX (Kimi K3, F5): this read the LEDGER count and presented it as a chain
  // fact — the same family as N7, one row over. Use the scanned count.
  document.getElementById("rangenote").textContent =
    (d.chain_bins === null || d.chain_bins === undefined ? "—" : d.chain_bins) + " bins held";

  const e = d.efficiency_pct;
  const el = document.getElementById("eff");
  el.textContent = (e === null || e === undefined) ? "—" : e + "%";
  el.className = "n " + zoneClass(e);
  document.getElementById("effnote").textContent =
    // ── DO NOT ASSERT A MISMATCH OUR OWN DATA CONTRADICTS (fixed 2026-09-23) ────────────────
    // This rewrote the honest zone text ("WATCH — LOW EFFICIENCY") into the words "low — shape
    // mismatch" for EVERY low reading, while the payload carries `label_matches_mass`. Jordan
    // read it, believed the machine was telling him he held the wrong shape, and asked what was
    // actually true. It was not true: the label matched the mass, and the reading was low because
    // spot had drifted to 43% of a band built 15/30. A low number and a wrong shape are different
    // findings — a display must not silently convert one into the other.
    (d.label_matches_mass === false
      ? "low — the live distribution does NOT match the " + (d.shape_kind || "?") + " label"
      : (d.efficiency_zone || "—"))
       .replace("WATCH — LOW EFFICIENCY", "low — spot has drifted off this shape\u2019s peak")
       .replace("HEALTHY", "healthy").replace("ACT NOW", "act now");
  const bar = document.getElementById("effbar");
  bar.style.width = (e || 0) + "%";
  bar.style.background = zoneColor(e);

  // ── WORKING CAPITAL TILE REMOVED (Jordan, 2026-09-25) ──────────────────────────────────────
  // The two bindings that used to be here --
  //     document.getElementById("depl").textContent = (d.deployed_pct || 0) + "%";
  //     document.getElementById("deplnote").textContent = money(d.deployed_usd) + ... idle ...
  // -- are DELETED WITH THE TILE, not left behind. With no #depl in the document, either line
  // would throw a TypeError on null, and because they sit inside the single render pass that
  // would take out EVERY field below them -- a blank page, not a missing tile. Removing a DOM
  // node and leaving its writer is how a tidy-up becomes an outage.
  // `deployed_usd` / `deployed_pct` / `idle_usd` are still in the payload and still shown as the
  // compounding decision, which is the honest frame for gas money.

  drawShape(d);

  // range ruler
  // RE-AUDIT FIX (Kimi K3, N11): a null range rendered "$null" on both ends of the ruler.
  const hasRange = (d.range_min !== null && d.range_min !== undefined &&
                    d.range_max !== null && d.range_max !== undefined);
  document.getElementById("lo").textContent = hasRange ? "$" + d.range_min : "—";
  document.getElementById("hi").textContent = hasRange ? "$" + d.range_max : "—";
  const z = document.getElementById("zone");
  const p = hasRange ? d.spot_pos_in_range_pct : null;
  if (p !== null && p !== undefined) {
    const cur = Math.max(0, Math.min(100, p));
    document.getElementById("spotmark").style.left = cur + "%";
    document.getElementById("spotmark").style.display = "block";
    z.style.left = "0%"; z.style.right = "0%";
    // AUDIT FIX (Kimi K3): the marker was clamped but the TEXT printed the raw value, so an
    // out-of-range spot read "sits at -40% of your range". Say what is actually true instead.
    const where = p < 0 ? "BELOW your range — nothing is being earned until price comes back up"
                : p > 100 ? "ABOVE your range — nothing is being earned until price comes back down"
                : p > 70 ? "near the top edge."
                : p < 30 ? "near the bottom edge."
                : "near the middle.";
    document.getElementById("posnote").textContent =
      (p >= 0 && p <= 100)
        ? "Spot $" + d.price_usd + " sits at " + p + "% of your range — " + where
        : "Spot $" + d.price_usd + " is " + where + " (range $" + d.range_min + "–$" + d.range_max + ")";
  } else {
    // RE-AUDIT FIX (Kimi K3, F11): the marker sat at its 50% CSS default when nothing was
    // computed, drawing a confident "you are mid-range" out of no data at all. Hide it instead.
    document.getElementById("spotmark").style.display = "none";
    document.getElementById("posnote").textContent =
      "Spot position unknown — " + (d.shape_kind ? "range unavailable" : "shape not recorded");
  }

  // ── THE NEXT TRANSITION (Jordan, 2026-09-24) ─────────────────────────────────────────────
  // Scenarios are STATES, moves are TRANSITIONS. Show where the book IS and which rungs are
  // legal from here, then the efficiency projection underneath. A classifier tells you what the
  // market is NOW; this tells you what the book can become next, so the scenario is visible
  // BEFORE it happens rather than reported after.
  (function renderTransition() {
    const t = d.transition;
    if (!t || t.error) {
      document.getElementById("tnow").textContent = "—";
      document.getElementById("twhy").textContent = t && t.error
        ? "Transition map unavailable — " + t.error
        : "Transition map unavailable for this book.";
      document.getElementById("tfoot").textContent = "";
      return;
    }
    const pct = r => (r === null || r === undefined) ? "—" : Math.round(r * 100) + "%";
    document.getElementById("tnow").textContent =
      t.state + "  ·  " + (t.state_shape || "—") + " " + (t.state_bins || "—") +
      " bins  ·  " + pct(t.state_ratio_pct === null || t.state_ratio_pct === undefined
                          ? null : t.state_ratio_pct / 100) + " ask/WAVAX";
    document.getElementById("twhy").textContent = t.why || "";

    const rungs = (t.rungs || []).slice().sort((a, b) => (a.steps || 9) - (b.steps || 9));
    document.getElementById("trungs").innerHTML = rungs.map(r =>
      '<div class="rung"><div class="rh">→ ' + r.to + '  (' + (r.shape || "—") +
      (r.bins ? " " + r.bins + " bins" : "") + (r.ratio !== null && r.ratio !== undefined
        ? "  " + Math.round(r.ratio * 100) + "% ask" : "") + ')</div>' +
      (r.needs ? '<div class="rg">needs: ' + r.needs + '</div>' : '') +
      (r.steps > 1 ? '<div class="rs">' + r.steps + ' rungs away — walked, not jumped</div>' : '') +
      '</div>').join("");

    const now = (t.now_eff === null || t.now_eff === undefined) ? null : t.now_eff;
    document.getElementById("tproj").innerHTML = (t.projection || []).map(p => {
      const active = now === null ? false
        : (p.at.indexOf(">=") === 0 ? now >= 70
          : p.at.indexOf("<") === 0 ? now < 50
          : (now >= 50 && now < 70));
      return '<div class="proj"><span class="pa" style="' +
        (active ? "color:var(--accent)" : "color:var(--dim)") + '">' + p.at + '</span>' +
        '<span class="pr">' + p.action + '</span></div>';
    }).join("");
    document.getElementById("tfoot").textContent = now === null
      ? "Fee efficiency unreadable — no projection without it."
      : "This book is at " + now + "% (" + (t.now_eff_zone || "—") + "). " +
        "The rungs above are the only legal moves from here; each one needs its guard to be true.";
  })();

  const sc = [];
  if (e !== null && e !== undefined && e < 70) {
    const alt = d.shape_kind === "curve" ? "bid-ask (U-shape)" : "curve (bell)";
    // AUDIT FIX (Kimi K3): this used to be fabricated as `100 - e`. It is now whatever the real
    // efficiency function says for the other shape, and if we do not have it we do not claim it.
    const altTxt = (d.efficiency_alt_pct === null || d.efficiency_alt_pct === undefined)
      ? "" : " The same liquidity as a " + alt + " would read about " + d.efficiency_alt_pct + "%.";
    sc.push("Your " + d.shape_kind + " shape is earning " + e + "% at this spot position." + altTxt);
  }
  // Say it plainly when the live distribution does not match the shape's name. The efficiency
  // figure above assumes a bell clusters at the centre and a U at the edges; if the real
  // distribution says otherwise, that number is describing a position you do not hold.
  if (d.label_matches_mass === false) {
    sc.push("But the live distribution does not match the '" + d.shape_kind + "' label: only " +
            d.mass_near_spot_pct + "% of the money sits within " + (d.near_bins || 3) + " bins of spot, so the money is " +
            "banked away from where it trades. The reading above assumes a shape you are not " +
            "actually holding — treat it as an estimate, not a measurement.");
  }
  const sw = document.getElementById("scen");
  // Jordan, 2026-09-22: "By default check both of our pages for the same bug." The inverted-ask
  // bug lives in the DEPLOY script, so it affects every tenant, not just the one that was noticed.
  // Read from the bins themselves, so it reports the position, not a config label.
  const lo = d.leg_orientation;
  if (lo && lo.verdict && lo.verdict !== "OK") {
    const bad = [];
    if (lo.ask && !lo.ask.toward_spot)
      { bad.push("ask (above spot): " + money(lo.ask.nearest_usd) + " nearest vs " +
                 money(lo.ask.furthest_usd) + " furthest"); }
    if (lo.bid && !lo.bid.toward_spot)
      { bad.push("bid (below spot): " + money(lo.bid.nearest_usd) + " nearest vs " +
                 money(lo.bid.furthest_usd) + " furthest"); }
    sc.push("A leg is deployed UPSIDE DOWN — " + bad.join("; ") + ". Liquidity should be heaviest " +
            "nearest spot; here it is heaviest at the FAR edge, so the bulk of the capital converts " +
            "last and earns least. The deploy script is fixed; rebuilding this position moves money, " +
            "so it is waiting on your go-ahead.");
  }
  if (sc.length) { sw.style.display = "block"; sw.textContent = "⚠︎ " + sc.join(" "); }
  else { sw.style.display = "none"; }

  // ── THE GOAL — DeFi Milestone (Jordan, 2026-09-22: "Add the Defi Milestone for the goals") ──
  // Same honesty rule as every other read on this page: if the ladder could not be computed we
  // render "—", never a fabricated "Untested / 0%". A missing read must not look like a real rank.
  const msz = d.milestone;
  // The server sends `rank_icon` for the CURRENT rank only; the next rank's icon is not a field,
  // so map it here from the same ladder steward_progress uses. Kept in one place so it cannot
  // disagree with the server for the current rank.
  // LITERAL emoji, never backslash-u escapes: this block lives inside a Python non-raw string, so
  // Python would interpret an escaped surrogate pair as REAL surrogate codepoints and the UTF-8
  // write of the page dies with "surrogates not allowed" — AFTER the JSON already wrote, so the
  // data looks fine while the page silently stops updating. (Hit and fixed 2026-09-22.)
  const MSICONS = {"Untested":"🌱","Scout":"🔭","Raider":"⚔️","Warlord":"👑","Sovereign":"🏰"};
  const msSet = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  if (!msz || msz.error || msz.rank === undefined || msz.rank === null) {
    msSet("rankicon", "—"); msSet("rankname", "—"); msSet("rankpct", "—");
    msSet("msfees", "—"); msSet("msnext", "—"); msSet("msunlock", "—");
    document.getElementById("msbar").style.width = "0%";
    msSet("msnote", msz && msz.error
      ? "Milestone unavailable — " + msz.error
      : "Milestone unavailable — no reliable fee estimate for this position.");
  } else {
    const icon = msz.rank_icon || "";
    msSet("rankicon", icon);
    msSet("rankname", msz.rank || "—");
    const p = (msz.progress_pct === null || msz.progress_pct === undefined) ? null : msz.progress_pct;
    msSet("rankpct", p === null ? "" : p + "% to next");
    document.getElementById("msbar").style.width = (p === null ? 0 : Math.max(0, Math.min(100, p))) + "%";
    const df = msz.current_daily_fees;
    msSet("msfees", (df === null || df === undefined) ? "—"
      : "$" + Number(df).toFixed(4) + "/day  \u00b7  " + money(msz.next_target_daily_fees) + " for " + (msz.next_rank || "next"));
    // ── PROGRESS AS A PERCENTAGE, NOT A DOLLAR-GAP (Jordan, 2026-09-24) ────────────────────
    // *"In the rank section, replace the more/day to progress percentage. For example:
    //   To next rank - 4% progress to scout."*
    // "$4.84 more/day" makes the reader hold the target in their head and do the division. The
    // bar and the badge above already speak in percent, so this row now agrees with them.
    const _pNext = (p === null || p === undefined) ? null : p;
    msSet("msnext", (msz.next_rank
      ? (_pNext === null
          ? "— progress to " + (MSICONS[msz.next_rank] || "") + " " + msz.next_rank
          : _pNext + "% progress to " + (MSICONS[msz.next_rank] || "") + " " + msz.next_rank)
      : "Top rank reached"));
    // NOTE: rank_and_progress returns `unlocks` (the NEXT tier's unlock) — verified against the
    // live function 2026-09-22. There is no next_unlocks/current_unlocks/next_rank_icon key;
    // reading those names rendered `undefined` silently, which is the false-value bug class.
    msSet("msunlock", msz.unlocks || "—");
    msSet("msunlocklbl", msz.next_rank ? "Unlocks at " + msz.next_rank : "Unlocked");
    msSet("msnote", "Ranked on estimated daily fees"
      + (msz.estimated ? " (a projection from the deployed book, not a settled ledger figure)" : "")
      + ". Ladder: Untested → 🔭 Scout $5 → ⚔️ Raider $20 → 👑 Warlord $55 → 🏰 Sovereign $200 per day.");
  }

  // ── AUTONOMY — DUTY CYCLE (Jordan, 2026-09-25) ──────────────────────────────────────────────
  // "Why don't we add the amount of hours that we've been active inside the pool between each
  //  rebalance? ... you're able to rebalance and do stuff autonomously now."
  // IN RANGE = deployed with spot inside the held bins (earning). OUT OF RANGE = deployed with
  // spot outside them (earning zero). The ratio between them is what autonomy buys, so they are
  // shown separately and FLAT (withdrawn) time is never folded into "out of range".
  // SAME HONESTY RULE AS THE MILESTONE: an unreadable source renders an explicit UNKNOWN with the
  // reason. A 0 here would read as "fully out of range" -- a claim about the book -- when in truth
  // nothing was measured, which is the failure mode this treasury has hit repeatedly.
  const dset = (id, v) => { const el = document.getElementById(id); if (el) el.textContent = v; };
  const dhh = h => (h === null || h === undefined) ? "—" : (Math.round(h * 10) / 10) + "h";
  const dpct = p => (p === null || p === undefined) ? "—" : p + "%";
  // ── COMPOUNDING — THE HEADLINE (Jordan, 2026-09-25) ────────────────────────────────────────
  // FLOW first, then WAITING. Every field degrades to UNKNOWN *with its reason*; no field may
  // render a 0 to mean "could not read it" -- a 0 here would read as "compounding is off", which
  // is a claim about the venue, and this project's most repeated bug is a false zero.
  const cp = d.compound;
  const cn = v => (v === null || v === undefined);
  const cusd = v => cn(v) ? null : (v < 1 ? "$" + Number(v).toFixed(4) : "$" + Number(v).toFixed(2));
  const flowOk = !!cp && cp.status === "ok" && !cn(cp.period_low_usd) && !cn(cp.period_high_usd);
  if (flowOk) {
    const same = cp.period_low_usd === cp.period_high_usd;
    dset("compflow", same ? cusd(cp.period_low_usd) : cusd(cp.period_low_usd) + " – " + cusd(cp.period_high_usd));
    dset("compflowfit", "folded back into the bins, over " + cp.period_days + "d"
      + (cp.bracket_x && cp.bracket_x > 2
          ? " · two sources disagree ×" + Number(cp.bracket_x).toFixed(2) + " — a RANGE, not a number"
          : (cp.single_source ? " · single source — no cross-check available" : "")));
    dset("compperiod", (same ? cusd(cp.period_low_usd)
        : cusd(cp.period_low_usd) + " – " + cusd(cp.period_high_usd)) + " over " + cp.period_days + " days");
    dset("comprate", cn(cp.rate_pct_per_day_low) ? "UNKNOWN"
        : Number(cp.rate_pct_per_day_low).toFixed(6) + " – " + Number(cp.rate_pct_per_day_high).toFixed(6) + " %/day");
    dset("compapr", cn(cp.apr_pct_low) ? "UNKNOWN"
        : Number(cp.apr_pct_low).toFixed(2) + "% – " + Number(cp.apr_pct_high).toFixed(2) + "% /yr");
    const dv = cp.derivations || {};
    const parts = [];
    Object.keys(dv).forEach(k => {
      const o = dv[k] || {};
      if (!cn(o.per_day_usd)) parts.push(k + " $" + Number(o.per_day_usd).toFixed(4) + "/day");
      else if (o.error) parts.push(k + " UNKNOWN (" + o.error + ")");
    });
    dset("compnote", "Derivations: " + (parts.join(" · ") || "none") + ". They do not share a "
      + "numerator, so where they agree the figure is solid and where they disagree the spread is "
      + "shown rather than one end picked."
      + (cp.pending_fee_note ? " " + cp.pending_fee_note + "." : ""));
  } else {
    ["compflow", "compperiod", "comprate", "compapr"].forEach(i => dset(i, "UNKNOWN"));
    dset("compflowfit", "UNKNOWN — " + ((cp && cp.error) || "no compounding reading was produced for this build"));
    dset("compnote", "UNKNOWN — " + ((cp && cp.error) || "no compounding reading was produced for this build")
      + " (showing UNKNOWN, not a zero.)");
  }
  // ── WAITING: WITHDRAWN FROM THE PAGE (Jordan, 2026-09-25) ──────────────────────────────────
  // The three writers that used to fill #compwait / #compwaitnote / #compwaitrow are gone with
  // their nodes, on purpose. On this venue the "waiting" number is only ever the idle wallet
  // float, so surfacing it told the reader to watch the treasury's pocket change. `cp.waiting_usd`
  // is untouched in the payload and still decides the HOLD/act branch below -- the datum is
  // dropped from the VIEW, not from the system. (dset() is null-safe, so these would no-op
  // harmlessly, but a writer aimed at a node that no longer exists is a lie to the next reader.)
  dset("compdec", (cp && cp.decision) ? cp.decision.action + " — " + cp.decision.reason
                                     : "UNKNOWN — no gas/viability reading");
  dset("comppend", (cp && cp.pending_fee_note)
      ? "none claimable — LFJ V2.2 folds fees into the bins at swap time"
      : "UNKNOWN");

  const dy = d.duty_cycle;
  const dutyRows = ["duty7", "dutyout7", "dutystreak", "dutyavg", "dutymax", "dutyall"];
  if (!dy || dy.status !== "ok") {
    dutyRows.forEach(i => dset(i, "UNKNOWN"));
    dset("dutynote", "UNKNOWN — "
      + ((dy && dy.error) ? dy.error : "no duty-cycle reading was produced for this build")
      + " (showing UNKNOWN, not a zero.)");
  } else {
    const W = dy.windows || {};
    const w7 = W["7d"] || {}, wA = W["all"] || {};
    dset("duty7", (w7.deployed_hours === null || w7.deployed_hours === undefined
      ? "—"                                     // nothing measured: UNKNOWN reads as UNKNOWN
      : (w7.deployed_hours === 0
          ? "0h — not deployed at any point in this window"   // a REAL zero, said out loud
          : dhh(w7.hours_in_range) + " of " + dhh(w7.deployed_hours) + " deployed · "
            + dpct(w7.in_range_share_pct) + " in range"
            + ((w7.accounting_covers_pct !== null && w7.accounting_covers_pct !== undefined
                && w7.accounting_covers_pct < 99)
                ? " (price series covers " + w7.accounting_covers_pct + "% of the window)"
                : ""))));
    dset("dutyout7", (w7.hours_out_of_range === undefined || w7.hours_out_of_range === null)
      ? "—"
      : dhh(w7.hours_out_of_range)
        + (w7.unresolved_share_pct ? " (+" + w7.unresolved_share_pct + "% unresolved at "
                                     + (w7.candle_tf || "candle") + " resolution)" : ""));
    dset("dutystreak", dy.deployed_now ? dhh(dy.current_streak_hours) : "flat — not deployed");
    dset("dutyavg", (w7.avg_hours_between_rebalances === null
                     || w7.avg_hours_between_rebalances === undefined)
      ? "—"
      : dhh(w7.avg_hours_between_rebalances) + " over " + (w7.rebalances || 0) + " rebalances");
    dset("dutymax", dhh(w7.longest_stretch_hours));
    // Bounds are shown only when they actually differ. A point-sampled series has no straddling
    // candles, so its low and high are identical — printing "88.6% (bounds 88.6%–88.6%)" would
    // dress a sampled estimate up as an exact one. Where the bounds ARE tight the reason is in
    // the note (the index, its resolution, and what it cannot see).
    dset("dutyall", (wA.deployed_hours
      ? dhh(wA.hours_in_range) + " of " + dhh(wA.deployed_hours) + " deployed · "
        + dpct(wA.in_range_share_pct)
        + ((wA.in_range_share_low_pct !== wA.in_range_share_high_pct)
            ? " (bounds " + dpct(wA.in_range_share_low_pct) + "–"
              + dpct(wA.in_range_share_high_pct) + ")"
            : "")
      : "—"));
    // The provenance the reader needs to judge the number: where the rebalances come from, where
    // the price path comes from, and what resolution the estimate is good to. The index that
    // ANSWERED is named, not the one that usually answers — the fallback is a different
    // instrument at a different resolution and must not be passed off as the primary.
    dset("dutynote",
      "Rebalances read on chain: one removeLiquidity → addLiquidity cycle from this wallet ("
      + (dy.rebalance_count || 0) + " on record; last " + (dy.last_rebalance_utc || "—")
      + " at block " + (dy.last_rebalance_block || "—") + "). Price path: "
      + ((dy.source && dy.source.price) || "index not reported")
      + " (" + (w7.window_label || "—") + "; " + (wA.window_label || "—") + ")"
      + (dy.price_shape ? " — " + dy.price_shape : "") + ". "
      + (w7.unresolved_share_pct
          ? "A candle that straddles a band edge is genuinely unknowable at this resolution, so "
            + "the share is bounded: " + dpct(w7.in_range_share_low_pct) + "–"
            + dpct(w7.in_range_share_high_pct) + " for the 7-day window. "
          : "")
      + "FLAT (withdrawn) time is reported separately at " + dhh(w7.hours_flat)
      + " over the last 7d and is not counted as out of range.");
  }

  document.getElementById("kind").textContent  = d.shape_kind || "unknown";
  document.getElementById("nearspot").textContent =
    (d.mass_near_spot_pct === null || d.mass_near_spot_pct === undefined) ? "—" : d.mass_near_spot_pct + "%";
  // the window is scaled to binStep on the data side; say so here rather than hardcoding "3"
  document.getElementById("nearlbl").textContent =
    "Money within " + (d.near_bins || 3) + " bins of spot";
  document.getElementById("bins").textContent  = (d.chain_bins ?? d.bins) + " bins";
  document.getElementById("holds").textContent =
    (d.holds_wavax === null || d.holds_wavax === undefined ||
     d.holds_usdc === null || d.holds_usdc === undefined)
      ? "—"
      : d.holds_wavax.toFixed(4) + " WAVAX + " + money(d.holds_usdc);
  document.getElementById("spotpx").textContent = "$" + d.price_usd;
  document.getElementById("staker").textContent = d.benchmark_staker_apy + "%/yr";
  // RE-AUDIT FIX (Kimi K3, N12): the sign was hardcoded "+", so a negative 30d move printed "+-12.3%".
  const h = d.benchmark_hodl_30d;
  document.getElementById("hodl").textContent = (h >= 0 ? "+" : "") + h + "%";
  document.getElementById("wallet").textContent = d.wallet;
  document.getElementById("updated").textContent = d.updated_at || "—";

  // AUDIT FIX (Kimi K3): the page claimed "every number read from Avalanche, not from config"
  // while showing two benchmark figures that are NOT chain reads — and the freshest of them is a
  // one-time 29.9-day measurement rendered forever as a live number. A stale figure shown as live
  // is the thing this footer exists to prevent, so it now says exactly what is what.
  // RE-AUDIT FIX (Kimi K3, F4): a FUTURE timestamp gives a negative age, which satisfied
  // `ageMin < 45` and read "fresh" — a check that cannot fail. Clamp at 0.
  const rawAge = d.updated_at ? Math.round((Date.now() - new Date(d.updated_at).getTime()) / 60000) : null;
  const ageMin = rawAge === null ? null : Math.max(0, rawAge);
  document.getElementById("stale").textContent =
    (ageMin === null) ? "age unknown"
    : ageMin < 45 ? "fresh" + (ageMin >= 2 ? " (" + ageMin + " min old)" : "")
    : "\u26a0 " + Math.round(ageMin / 60 * 10) / 10 + " h old — refresh may be stalled";
  document.getElementById("prov").textContent =
    "Capital, position, shape and efficiency: measured on-chain." +
    (d.price_source === "chain" ? " AVAX price: chain fallback (ledger price unavailable)." : "") +
    " Staker/hold benchmarks: reference figures, not live reads \u2014 holding data as of the " +
    "measurement date, not this minute.";
}

async function load() {
  try {
    const r = await fetch(DATA + "?t=" + Date.now(), {cache: "no-store"});
    if (!r.ok) throw new Error("HTTP " + r.status);
    render(await r.json());
  } catch (err) {
    // textContent: the error string can carry server/RPC text and must never be parsed as HTML.
    document.getElementById("sub").textContent =
      "\u26a0 Could not load position data (" + err.message + "). Not showing stale numbers.";
  }
}
load();
setInterval(load, 120000);   // keep it fresh while the page is open
</script>
</body>
</html>
"""


def _hub_url(name):
    """Link back to the person's hub, but ONLY if that hub actually exists.

    Dadrian has no hub page yet, so a hardcoded back-link would send him to a 404 from his own
    dashboard — the kind of small brokenness that makes a page feel untrustworthy. Check the real
    server and fall back to the landing page; the link is then always live.
    """
    import urllib.request
    hub = f"https://gentechlabs.net/{name}.html"
    try:
        req = urllib.request.Request(hub, method="HEAD",
                                     headers={"User-Agent": "Mozilla/5.0 (compatible; GenTech/1.0)"})
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status == 200:
                return hub
    except Exception:
        pass
    return "https://gentechlabs.net/"


def _write_everywhere(fname, blob):
    """Write to BOTH destinations, or complain loudly.

    AUDIT FIX (Kimi K3): `if os.path.isdir(dest)` silently skipped a missing destination — which
    is precisely the repo-committed/VPS-404 divergence this module's own docstring blames for the
    previous failure, reproduced with no signal. If the VPS path is absent, the repo gets a fresh
    file and nginx serves a stale one, and nothing anywhere says so.
    """
    missing = []
    for dest in (REPO, VPS):
        if not os.path.isdir(dest):
            missing.append(f"{dest} (missing)")
            continue
        try:
            # RE-AUDIT FIX (Kimi K3, F8): write to a temp file and rename — a crash mid-write left
            # a truncated file that nginx would happily serve as broken HTML.
            tmp = os.path.join(dest, f".{fname}.tmp")
            with open(tmp, "w") as f:
                f.write(blob)
            os.replace(tmp, os.path.join(dest, fname))
        except OSError as e:
            # RE-AUDIT FIX (Kimi K3, N8): an I/O error (permissions, disk full) raised UNCAUGHT and
            # killed the whole run at the first tenant — the same blast radius as the bug this
            # warning was added to fix. Warn per destination and carry on.
            missing.append(f"{dest} ({type(e).__name__}: {e})")
    if missing:
        print(f"  \u26a0 NOT WRITTEN for {fname}: {'; '.join(missing)} — "
              f"that surface will serve stale data")
    return missing


def write_pages(tenants):
    """One page per tenant, tenant name baked in. Returns the filenames written."""
    out = []
    for name in tenants:
        html = (PAGE.replace("__TENANT__", name)
                    .replace("__NAME__", name.capitalize())
                    .replace("__HUB__", _hub_url(name)))
        fn = f"{name}-defi.html"
        _write_everywhere(fn, html)
        out.append(fn)
    return out


def main():
    reg = json.load(open(REGISTRY))
    tenants = [(n, t) for n, t in (reg.get("tenants") or {}).items()
               if t.get("status") == "ACTIVE" and t.get("wallet")]

    names = []
    for name, t in tenants:
        data = build(name, t)
        blob = json.dumps(data, indent=2)
        _write_everywhere(f"defi-data-{name}.json", blob)
        status = data.get("error") or f"${data.get('capital_usd')} {data.get('range_status')}"
        print(f"  {name:10} {status}")
        names.append(name)

    pages = write_pages(names)
    print(f"  wrote {len(pages)} page(s): {', '.join(pages)}")

    # RE-AUDIT FIX (Kimi K3, N9 / F6): only ACTIVE tenants are written, so a tenant who is
    # deactivated or removed leaves their data file and page being served INDEFINITELY — a public
    # page showing a dead position as if it were current. Sweep them.
    #
    # Round-2 wrote this as a filename REGEX, which had two holes (F6): a name with uppercase or a
    # hyphen was never swept (so the original bug persisted for exactly those tenants), and an
    # ACTIVE tenant momentarily missing its wallet was dropped from `names` and its LIVE page got
    # deleted. Derive the sweep set from the REGISTRY instead: every tenant that is not currently
    # writable is a candidate, and an ACTIVE-but-walletless tenant is deliberately spared.
    all_names = set((reg.get("tenants") or {}).keys())
    keep = set(names) | {n for n, t in (reg.get("tenants") or {}).items()
                         if t.get("status") == "ACTIVE"}   # never delete a live tenant's page
    swept = []
    for dest in (REPO, VPS):
        if not os.path.isdir(dest):
            continue
        for fn in os.listdir(dest):
            m = re.match(r"defi-data-(.+)\.json$", fn) or re.match(r"(.+)-defi\.html$", fn)
            if m and m.group(1) in all_names and m.group(1) not in keep:
                try:
                    os.remove(os.path.join(dest, fn))
                    swept.append(f"{dest}/{fn}")
                except OSError:
                    pass
    if swept:
        print(f"  swept {len(swept)} file(s) for tenant(s) no longer ACTIVE: {', '.join(swept)}")

    # A tiny index so the hub directory can list who has a page (no balances in it).
    idx = {"tenants": names, "updated_at": __import__("datetime").datetime.utcnow()
           .isoformat(timespec="seconds") + "Z"}
    _write_everywhere("defi-tenants.json", json.dumps(idx, indent=2))
    print(f"  wrote {len(names)} tenant data file(s) to repo + VPS")


if __name__ == "__main__":
    main()
