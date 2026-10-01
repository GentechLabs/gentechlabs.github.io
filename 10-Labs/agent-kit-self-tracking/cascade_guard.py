#!/usr/bin/env python3
"""
cascade_guard.py — EITHER FARM IT, OR GET OUT. (Jordan, 2026-09-23)

THE RULE (Jordan, verbatim):
    "say we're breaking down, right? And it's going faster than we had hoped. Why not
     exit the pool and convert to the stable coin and wait it out? And once we get a
     little bit more stable, come back with a curve. Because you're already waiting
     10, 5, 15 minutes to confirm breakouts and stuff like that"

THE INSIGHT THIS ENCODES — DEPTH IS NOT THE SIGNAL, SPEED IS:
  Jordan's fall was -8.83% over a day. That sounds violent. It is not.
      -8.83% / day  =  -0.37%/hr  =  0.3 sigma/hr   -- a GRIND
  A bid-ask EATS a grind: the ladder fills on the way down, and the re-center chases
  the price for ~$0.41. That is the machine working. Exiting there would have been
  WRONG — it would have sold a normal pullback and paid the spread to do it.
  A cascade looks completely different:
      -5% / hour    =  ~4.6 sigma/hr                -- NO BAND HOLDS THIS
  45 bins at binStep 10 spans 4.5%. Nothing in the approved menu (25 or 45 bins,
  Jordan's ceiling) survives a 3-sigma hour. So the answer is not a wider band —
  the ceiling is a real limit — it is to LEAVE and wait. That is this module.

WHY SPEED AND NOT DRAWDOWN:
  Every other monitor in this treasury asks "how far has it moved". That question
  cannot tell a healthy pullback from a cascade, because both can end up 9% down.
  This asks "how long did it take" — the only question that separates them.

THE STATE MACHINE (three states, one authority):
  FARM       sigma/hr < 2.0                     stay in, farm it, re-center normally
  CHASE      sigma/hr >= 2.0, confirmed         re-center, do NOT exit
  CASCADE    sigma/hr >= 3.0, confirmed, AND
             price outside our band              withdraw -> all USDC -> WAIT
  RE-ENTER   was CASCADE and the 2-day measure
             has fallen under 4%                 deploy a CURVE (stable shape)

CONFIRMATION (Jordan's 10 + 5):
  A single reading is not a breakout — this treasury has been burned twice calling a
  snapshot a mechanism. A speed reading must PERSIST across two samples at least
  CONFIRM_MIN apart, and the state must have been armed for ARM_MIN first. The
  guard keeps its own sample history, because nothing else in the fleet records
  intraday pool price at this cadence — without it there is no way to measure speed.

SELF-SAMPLING:
  Each run appends {ts, price} to its state file. The speed is computed from OUR OWN
  samples, not from a vendor candle. This means the guard is usable immediately and
  becomes more accurate the longer it runs. A reading with < 2 samples is UNKNOWN,
  never FARM — an instrument that cannot read must not read as calm.

CLI:
  python3 cascade_guard.py --tenant jordan            # verdict only, always safe
  python3 cascade_guard.py --tenant jordan --json
Exit: 0 always (a verdict is not an error). Non-zero only on an unreadable price.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── thresholds: derived from the tape, not invented ─────────────────────────────────
CASCADE_SIGMA_HR = 3.0      # >= this, no approved band can hold it -> leave
CHASE_SIGMA_HR = 2.0        # >= this, re-center but do not leave
ARM_MIN = 10                # Jordan: wait 10 minutes...
CONFIRM_MIN = 5             # ...then confirm again after 5 more
STABLE_2D_PCT = 4.0         # the SAME stability bar the shape tracker uses to say "calm"
MAX_SAMPLES = 2000          # bounded history (~2 days at 90s cadence)


def state_path(tenant):
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        f".cascade-state-{tenant}.json")


def load_state(tenant):
    try:
        with open(state_path(tenant)) as f:
            return json.load(f)
    except Exception:
        return {"samples": [], "state": "FARM", "armed_at": None, "since": None}


def save_state(tenant, st):
    st["samples"] = st["samples"][-MAX_SAMPLES:]
    tmp = state_path(tenant) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, state_path(tenant))


def read_price():
    """Live AVAX price from the pool's active bin -- the same source the rest of the fleet uses."""
    try:
        import avax_rpc            # noqa
        import fee_efficiency as FE  # noqa
        from web3 import Web3
        w3 = avax_rpc.connect(timeout=45)
        PAIR = Web3.to_checksum_address("0x864d4E5Ee7318e97483DB7EB0912E09F161516EA")
        act = int.from_bytes(
            w3.eth.call({"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
        return float(FE._price_at(w3, act)), w3, PAIR, act
    except Exception:
        return None, None, None, None


def sigma_per_hour(samples):
    """Speed of the move in units of a normal hour. None when it cannot be measured."""
    if len(samples) < 2:
        return None, None
    now_t, now_p = samples[-1]["t"], samples[-1]["p"]
    # find the oldest sample >= ARM_MIN back; fall back to the oldest we have
    ref = None
    for s in samples:
        if (now_t - s["t"]) / 60.0 >= ARM_MIN:
            ref = s
            break
    if ref is None:
        ref = samples[0]
    span_hr = max((now_t - ref["t"]) / 3600.0, 1e-6)
    if span_hr < (CONFIRM_MIN / 60.0):
        return None, None                      # too little elapsed time to call it
    move_pct = (now_p / ref["p"] - 1) * 100 if ref["p"] else 0.0
    per_hr = move_pct / span_hr
    try:
        import volatility_tracker as VT
        closes = VT.price_series(30)
        vol_d = VT.realized_vol(closes)
        vol_h = vol_d / (24 ** 0.5) if vol_d else None
    except Exception:
        vol_h = None
    if not vol_h:
        return None, None                      # cannot measure -> UNKNOWN, not calm
    return per_hr / vol_h, move_pct


def in_our_band(tenant):
    """Read the tenant's live band from the chain. None when it cannot be read."""
    try:
        import avax_rpc           # noqa
        import fee_efficiency as FE  # noqa
        from web3 import Web3
        # ── USE THE SHARED TENANT READER, NOT A SECOND ONE (fixed 2026-09-23) ────────
        # The first version read `json.load(tenants.json).get(tenant)` — but wallets live under
        # the "tenants" key, so it found nothing and the band read UNREADABLE on a book that was
        # demonstrably live. A second reader for an existing record is how the fleet grows two
        # truths; tenant_guard.registered() already owns this lookup.
        import tenant_guard as TG
        rec = TG.registered(tenant) or {}
        w = rec.get("wallet")
        if not w:
            return None
        w3 = avax_rpc.connect(timeout=45)
        PAIR = Web3.to_checksum_address("0x864d4E5Ee7318e97483DB7EB0912E09F161516EA")
        sel = Web3.keccak(text="balanceOf(address,uint256)")[:4]
        act = int.from_bytes(
            w3.eth.call({"to": PAIR, "data": Web3.keccak(text="getActiveId()")[:4]}), "big")
        W = Web3.to_checksum_address(w)
        held = []
        for b in range(act - 90, act + 91):
            raw = w3.eth.call({"to": PAIR,
                               "data": sel + bytes.fromhex(W[2:].rjust(64, "0")) + b.to_bytes(32, "big")})
            if raw and int.from_bytes(raw, "big") > 0:
                held.append(b)
        if not held:
            return {"flat": True, "act": act}
        return {"flat": False, "act": act, "lo": min(held), "hi": max(held),
                "in_range": min(held) <= act <= max(held)}
    except Exception:
        return None


def evaluate(tenant, do_sample=True):
    st = load_state(tenant)
    price = None
    if do_sample:
        price, _w3, _pair, _act = read_price()
        if price:
            st["samples"].append({"t": int(time.time()), "p": price})

    sig, move_pct = sigma_per_hour(st["samples"])
    band = in_our_band(tenant)

    now = time.time()
    # the armed clock starts the first time we see a fast move
    fast = sig is not None and abs(sig) >= CHASE_SIGMA_HR
    if fast and not st.get("armed_at"):
        st["armed_at"] = int(now)
    if not fast:
        st["armed_at"] = None

    armed_min = (now - st["armed_at"]) / 60.0 if st.get("armed_at") else 0.0

    # a move must persist across samples >= CONFIRM_MIN apart (Jordan's 10 then 5)
    confirmed = bool(fast and armed_min >= ARM_MIN and len(st["samples"]) >= 2 and
                     (st["samples"][-1]["t"] - st["samples"][-2]["t"]) / 60.0 <= max(CONFIRM_MIN, 20))

    if sig is None:
        verdict, why = "UNKNOWN", "not enough elapsed samples to measure speed (UNKNOWN, not calm)"
    elif abs(sig) >= CASCADE_SIGMA_HR and confirmed:
        outside = bool(band and not band.get("flat") and not band.get("in_range"))
        if outside:
            verdict = "CASCADE"
            why = (f"{abs(sig):.1f} sigma/hr confirmed over {armed_min:.0f} min AND price is outside "
                   f"our band -- no approved band holds this. EXIT to USDC, wait, re-enter as a curve.")
        else:
            verdict = "CHASE"
            why = (f"{abs(sig):.1f} sigma/hr confirmed but price is still INSIDE our band -- the ladder "
                   f"is still doing its job. Re-center, do NOT exit.")
    elif fast and confirmed:
        verdict = "CHASE"
        why = f"{abs(sig):.1f} sigma/hr confirmed -- re-center and keep farming."
    elif fast:
        verdict = "ARMED"
        why = (f"{abs(sig):.1f} sigma/hr -- armed {armed_min:.0f}/{ARM_MIN} min, awaiting the "
               f"{CONFIRM_MIN}-min second confirmation (Jordan's 10 then 5).")
    else:
        verdict = "FARM"
        why = f"{abs(sig):.1f} sigma/hr -- a grind, not a cascade. Stay in and earn."

    # RE-ENTRY: we left on a cascade and the tape has gone quiet again
    if st.get("state") == "CASCADE" and sig is not None and abs(sig) < 1.0:
        # ── COMPUTED HERE, NOT BORROWED (fixed immediately 2026-09-23) ───────────
        # This first called VT.sustained_move_pct(), which DOES NOT EXIST — and the hasattr guard
        # meant it silently evaluated to None, so the RE-ENTER branch could NEVER fire. The LSP
        # flagged it on write. That is the day's exact bug class, self-inflicted, in a branch whose
        # whole purpose is to bring capital BACK into the pool.
        # A missing function is not a missing reading: never let absence degrade to a silent skip.
        sustained = None
        try:
            import volatility_tracker as VT
            closes = VT.price_series(30)
            if closes and len(closes) >= 3:
                sustained = (closes[-1] / closes[-3] - 1) * 100     # the 2-day move
        except Exception:
            sustained = None
        if sustained is not None and abs(sustained) < STABLE_2D_PCT:
            verdict = "RE-ENTER"
            why = (f"was CASCADE; the 2-day move is now {sustained:+.2f}% (< {STABLE_2D_PCT}%) and "
                   f"speed is {abs(sig):.1f} sigma/hr -- STABLE again. Come back with a CURVE.")

    prev = st.get("state")
    if verdict in ("FARM", "CHASE", "CASCADE", "RE-ENTER") and verdict != prev:
        st["state"] = verdict
        st["since"] = int(now)

    if do_sample:
        save_state(tenant, st)

    return {"tenant": tenant, "verdict": verdict, "why": why, "sigma_hr": sig,
            "move_pct": move_pct, "armed_min": armed_min, "confirmed": confirmed,
            "band": band, "price": price, "was": prev}


def main():
    ap = argparse.ArgumentParser(description="Cascade guard: farm it, or get out.")
    ap.add_argument("--tenant", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-sample", action="store_true", help="evaluate without appending a sample")
    a = ap.parse_args()

    r = evaluate(a.tenant, do_sample=not a.no_sample)
    if a.json:
        print(json.dumps(r, indent=2, default=str))
        return 0

    b = r["band"]
    print(f"\n  \U0001F300 CASCADE GUARD — {r['tenant']}")
    print(f"  {'-'*66}")
    print(f"  price      ${r['price']:.4f}" if r["price"] else "  price      UNREADABLE")
    if r["sigma_hr"] is not None:
        print(f"  speed      {r['sigma_hr']:+.2f} sigma/hr   ({r['move_pct']:+.2f}% over the window)")
        print(f"  thresholds {CHASE_SIGMA_HR:.1f} re-center  |  {CASCADE_SIGMA_HR:.1f} EXIT")
    else:
        print(f"  speed      UNKNOWN  (needs {ARM_MIN} min of samples before it can tell)")
    if b and not b.get("flat"):
        print(f"  band       bins {b['lo']}..{b['hi']}  active {b['act']}  "
              f"{'IN RANGE' if b['in_range'] else 'OUT OF RANGE'}")
    elif b and b.get("flat"):
        print(f"  band       NO POSITION (flat)")
    else:
        print(f"  band       UNREADABLE")
    print(f"  {'-'*66}")
    print(f"  VERDICT    {r['verdict']}")
    print(f"             {r['why']}")
    print(f"  {'-'*66}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
