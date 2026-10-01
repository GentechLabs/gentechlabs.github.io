#!/usr/bin/env python3
"""
capital-guard.py — venue-aware, fail-closed pre-flight check for capital moves.

WHY (Jordan, Sep 11 2026):
  "we need to make sure nothing like this happens again... whenever we make
   certain commands we don't want the money to end up somewhere else."
  "we got to also keep this in mind when it comes to different platforms as well
   when we start swapping... when we swap rails the guard must be venue-aware,
   not just address-aware."

TWO LAYERS OF REFUSAL:

  1. ADDRESS-LEVEL  — is this destination an approved rail at all?
                      Unknown or non-ACTIVE -> REFUSE. Fail closed.

  2. VENUE-LEVEL    — does the venue actually SUPPORT this action?
                      (delegates to venue-compat.py). A venue that is
                      scaffold/not-built/unassessed/compliance-gated, or one
                      that can't do the requested shape, is REFUSED even if its
                      address is approved.

     The Sep 10 lesson: an address check alone cannot tell you that
     `lfj + shape=bid-ask` silently produces a curve, or that adding liquidity
     swaps your composition one-sided. Address approval is necessary, not
     sufficient.

  3. SWITCH MODE    — `switch --from X --to Y` validates BOTH ends plus the
                      pairing. An address check can't tell you whether a swap
                      out of LFJ into Blackhole is what you intend.

EXIT: 0 = all approved; 1 = at least one REFUSED (fail closed).

USAGE
  python3 capital-guard.py rails
  python3 capital-guard.py check --to 0x41100c6d… --chain avalanche
  python3 capital-guard.py check --to 0x41100c6d… --venue blackhole_cl --action deposit --shape bid-ask
  python3 capital-guard.py switch --from lfj --to blackhole_cl --amount-usd 4
  python3 capital-guard.py guard --plan plan.json
  python3 capital-guard.py selftest
"""
import argparse
import hashlib
import json
import os
import sys
import time
from typing import Optional

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.environ.get(
    "CAPITAL_GUARD_CONFIG",
    os.path.join(HERE, "capital-guard-rails.json"),
)

# ── Named wallets (Jordan, Sep 15 2026) ───────────────────────────────────
# "Name the destination, not the address." Durable wallets get a name so we
# refer to `--to jordan` instead of pasting an address. Exchange deposit
# addresses rotate, so they live under `transient` and never resolve here.
WALLETS_PATH = os.environ.get(
    "CAPITAL_GUARD_WALLETS",
    os.path.join(HERE, "wallets.json"),
)


def resolve_name(name):
    """Resolve a friendly wallet name -> address. Returns (address, entry) or
    (None, None) if it is not a known name. Only DURABLE wallets resolve;
    transient exchange addresses are deliberately excluded."""
    if not name or name.startswith("0x"):
        return None, None
    try:
        with open(WALLETS_PATH) as f:
            w = json.load(f)
        e = (w.get("wallets") or {}).get(name.strip().lower())
        if e and e.get("address"):
            return e["address"], e
    except Exception:
        return None, None
    return None, None


# ── Per-address approvals (Jordan, Sep 15 2026) ───────────────────────────
# "Each time I send a wallet, I'll just say I approve you to send to this
# wallet. That'll be our security feature, since the Coinbase wallets are
# always rotating and you can't really keep them."
#
# So: a TRANSIENT destination (rotating exchange deposit address) is only
# spendable if an approval recorded for THAT EXACT address exists and is
# unconsumed. Addresses are never generalized: approving one Coinbase address
# never approves another. Durable named wallets do not need one.
APPROVALS_PATH = os.environ.get(
    "CAPITAL_GUARD_APPROVALS",
    os.path.join(HERE, "approvals.json"),
)


def load_approvals():
    try:
        with open(APPROVALS_PATH) as f:
            return json.load(f)
    except Exception:
        return {"version": 1, "approvals": []}


def save_approvals(a):
    tmp = APPROVALS_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(a, f, indent=2)
    os.replace(tmp, APPROVALS_PATH)


def find_approval(address, chain=None, amount_usd=None):
    """Return a matching UNCONSUMED approval for this exact address, or None."""
    a = (address or "").lower()
    for ap in load_approvals().get("approvals", []):
        if (ap.get("address") or "").lower() != a:
            continue
        if ap.get("consumed_at"):
            continue
        if chain and ap.get("chain") and ap["chain"] != chain:
            continue
        cap = ap.get("max_usd")
        if cap is not None and amount_usd is not None and amount_usd > float(cap):
            continue
        return ap
    return None


def require_approval(address, chain, amount_usd, rail):
    """Transient destinations need an unconsumed per-address approval."""
    ap = find_approval(address, chain, amount_usd)
    if ap:
        return True, ap, None
    pend = [x for x in load_approvals().get("approvals", [])
            if (x.get("address") or "").lower() == (address or "").lower()
            and not x.get("consumed_at")]
    if pend:
        return False, None, ("an approval exists for this address but its cap is "
                             f"below this amount (cap ${pend[0].get('max_usd')})")
    return False, None, ("TRANSIENT destination with NO recorded approval. "
                         "Jordan must say 'I approve you to send to this wallet' "
                         "for THIS address, then record it with: "
                         f"capital-guard.py approve --to {address} --approved-by jordan")

# ── Venue compat (optional but wired when present) ────────────────────────
_VC = None
try:
    import importlib.util
    _p = os.path.join(HERE, "venue-compat.py")
    if os.path.exists(_p):
        _spec = importlib.util.spec_from_file_location("venue_compat", _p)
        _VC = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_VC)
except Exception as _e:      # pragma: no cover
    print(f"⚠️  capital-guard: venue-compat unavailable ({_e}) — "
          f"venue-level checks DISABLED (address checks still enforced)")
    _VC = None


# ── Approved rails ────────────────────────────────────────────────────────
# `venue` links the address to its compatibility profile.
DEFAULT_RAILS = {
    "version": 2,
    "note": ("Approved capital destinations, venue-linked. Anything not listed -> "
             "REFUSED. Venue-level support is checked via venue-compat."),
    "rails": [
        {
            "chain": "avalanche",
            "address": "0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7",
            "name": "Blackhole WAVAX/USDC CL pool",
            "venue": "blackhole_cl",
            "status": "ACTIVE",
        },
        {
            "chain": "avalanche",
            "address": "0x3fed017ec0f5517cdf2e8a9a4156c64d74252146",
            "name": "Blackhole NFPM (position manager)",
            "venue": "blackhole_cl",
            "status": "ACTIVE",
        },
        {
            "chain": "base",
            "address": "0x7ebff188f2eba16518c02864589b1403a5d1296a",
            "name": "x402 gateway payTo (Base)",
            "venue": None,          # not an LP venue — no compat profile
            "status": "ACTIVE",
        },
        # ── Not approved ──────────────────────────────────────────────────
        {
            "chain": "avalanche",
            "address": "0x864d4e5ee7318e97483db7eb0912e09f161516ea",
            "name": "LFJ LB pair (WAVAX/USDC)",
            "venue": "lfj",
            "status": "PARKED",
            "reason": ("Exited. Sep 10 incident: capital landed here, the add swapped "
                       "composition one-sided, and a re-center left every bin out of "
                       "range. Re-enable only on a deliberate decision."),
        },
        {
            "chain": "avalanche",
            "address": "0x18556da13313f3532c54711497a8fedac273220e",
            "name": "LFJ router",
            "venue": "lfj",
            "status": "PARKED",
            "reason": "Same rail as the parked LFJ pair. No routing into LFJ while parked.",
        },
        {
            "chain": "avalanche",
            "address": "0x3ade52f9779c07471f4b6d5997444c3c2124c1c0",
            "name": "Blackhole gauge",
            "venue": "blackhole_cl",
            "status": "QUARANTINED",
            "reason": ("22 failed withdraw(uint256) calls on Sep 10 (re-center path in "
                       "blackhole_cl_adapter.py) burned gas on every retry. Quarantined "
                       "until the call path is fixed and re-verified."),
        },
    ],
}


def load_rails():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return json.load(f)
        except Exception as e:
            print(f"🚨 capital-guard: cannot parse {CONFIG_PATH}: {e}")
            print("    Refusing everything (fail closed).")
            return {"version": 2, "rails": []}
    return DEFAULT_RAILS


def lookup(cfg, address, chain=None):
    """Find an approved rail by address. Returns the rail, or None.

    A rail MAY have no `address` — venue-level entries are approved by NAME rather than by an
    enumerated address, and the "Hyperliquid perps (crypto) — ARMED" rail is exactly that. This
    used to do `r["address"]` unconditionally, so any lookup that iterated as far as that entry
    raised KeyError and check() CRASHED instead of returning a verdict. That is the false-value
    family: an exception standing where a verdict belongs. A caller that treats a raised error as
    "couldn't verify" cannot tell a crash from a clean refusal — and a caller that tests only
    "did it refuse?" reads it as APPROVAL. Found 2026-09-27 while removing the tenant ceiling; it
    predates that change and no test covered an address that is not in the list.

    Entries with no address are skipped here on purpose, so control falls through to the VENUE
    check in check(), which is the designed path for a venue approved by name.
    """
    a = (address or "").lower()
    for r in cfg.get("rails", []):
        ra = (r.get("address") or "").lower()
        if ra and ra == a and (chain is None or r.get("chain") == chain):
            return r
    return None


def venue_check(venue, action, shape=None):
    """Venue-level support check via venue-compat. (ok, [problems])."""
    if _VC is None:
        return True, []
    if not venue:
        return True, []
    kw = {}
    if shape:
        kw["shape"] = shape
    ok, problems = _VC.preflight(venue, action, **kw)
    return ok, problems


def tenant_ceiling(tenant: str = None) -> Optional[float]:
    """The tenant's TOTAL capital ceiling — the most this collaborator will risk in the treasury.

    Jordan, 2026-09-26: *"his agentic treasury should follow the same RULES mine does. He would
    prefer I manage it for him ... He just wants to put money in it."*

    So the rules are shared and the CEILING is what is personal. The tenant registry has always
    SAID this was required — its onboarding requirements list *"an explicit capital ceiling the
    tenant is willing to lose entirely"* — but there was nowhere for it to live, so no ceiling was
    ever enforced and `caps` read `None` for every tenant.

    This is the collaborator's own money, so the ceiling is the one number that must never be
    assumed. A missing ceiling returns None and the caller REFUSES rather than permitting an
    unbounded deposit: for someone else's capital, "no limit configured" must not mean "no limit".
    """
    t = (tenant or os.environ.get("STEWARD_TENANT") or "jordan").strip().lower()
    try:
        reg = os.environ.get("STEWARD_REGISTRY") or os.path.join(HERE, "tenants.json")
        if not os.path.exists(reg):
            reg = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json"
        with open(reg) as f:
            d = json.load(f)
        rec = (d.get("tenants") or {}).get(t) or {}
        cap = rec.get("capital_ceiling_usd")
        return float(cap) if cap is not None else None
    except Exception:
        return None


def current_tenant_value(tenant: str = None) -> Optional[float]:
    """What the tenant's treasury is worth right now, read from the hub data for THAT tenant.

    Deliberately per-tenant: reading one shared file here would cap one person using another
    person's balance, which is the same one-book-wearing-two-names bug found in posture.py the
    same day. Returns None when it cannot be read — an unreadable balance is not zero, and treating
    it as zero would let an unlimited deposit through the exact hole this function closes.
    """
    t = (tenant or os.environ.get("STEWARD_TENANT") or "jordan").strip().lower()
    for p in (f"/var/www/gentechlabs/DeFi/defi-data-{t}.json",
              os.path.join(HERE, f"defi-data-{t}.json")):
        try:
            if not os.path.exists(p):
                continue
            with open(p) as f:
                d = json.load(f)
            for k in ("capital_usd", "deployed_usd"):
                v = d.get(k)
                if v is not None:
                    return float(v)
        except Exception:
            continue
    return None


def check_tenant_ceiling(amount_usd: float, tenant: str = None) -> tuple:
    """(ok, reason). Refuses a deposit that would take the tenant past their ceiling.

    Fails CLOSED at every step, on purpose. This guards a collaborator's money and Jordan does not
    want to be the one watching it — so the guard has to be right without him. Every one of these
    three conditions is a REFUSAL, not a warning:
      * no ceiling configured  -> we do not know their limit, so we do not spend past it
      * balance unreadable     -> we cannot tell what they already hold, so we cannot say if this fits
      * this deposit would exceed it -> refused, and the arithmetic is shown so it is arguable
    """
    t = (tenant or os.environ.get("STEWARD_TENANT") or "jordan").strip().lower()
    if amount_usd is None:
        return True, "no amount supplied — ceiling not evaluated (caller must still know the limit)"
    try:
        amt = float(amount_usd)
    except (TypeError, ValueError):
        return False, f"amount {amount_usd!r} is not a number — refusing rather than guessing"

    cap = tenant_ceiling(t)
    if cap is None:
        return False, (f"REFUSED — no capital ceiling registered for tenant {t!r}. The registry "
                       f"requires one ('an explicit capital ceiling the tenant is willing to lose "
                       f"entirely') and an unset limit must not mean unlimited.")
    cur = current_tenant_value(t)
    if cur is None:
        return False, (f"REFUSED — cannot read {t!r}'s current value, so this deposit cannot be "
                       f"checked against the ${cap:.2f} ceiling. An unreadable balance is not zero.")
    after = cur + amt
    if after > cap + 1e-9:
        return False, (f"REFUSED — this deposit would take {t!r} to ${after:.2f}, over the "
                       f"${cap:.2f} ceiling (now ${cur:.2f} + ${amt:.2f}). The ceiling is the amount "
                       f"they are willing to lose entirely; raise it deliberately or send less.")
    return True, f"within ceiling — {t!r} would hold ${after:.2f} of ${cap:.2f}"


def check(cfg, address, chain=None, amount_usd=None, purpose="", direction="in",
          venue=None, action="deposit", shape=None, skip_venue=False):
    """Two-layer check. direction='out' permits EXIT from a non-ACTIVE rail."""
    # ── NO CAPITAL CEILING (Jordan, 2026-09-27) ───────────────────────────────────────────────
    # The per-tenant ceiling check lived here and ran FIRST, before the rail lookup. Jordan removed
    # it the day after it was built:
    #     "we don't need anything blocking anything... We don't need any gates for how much money can
    #      be in the Agentic Treasury. Any other rules like that are stoppers. Take them out."
    #
    # It was a stopper, not a protection. The $50 was never his number or dadrian's — I derived it
    # from what dadrian had already funded and flagged it PROVISIONAL because I had no real figure.
    # An agent-invented limit enforced against the owner's own money is a gate on the boss.
    #
    # The rail check below STAYS. That is a different question: the rail list says "this is a known
    # place to send", and it is what stops an unknown address being paid or a parked venue being
    # re-entered. A destination still has to be approved; the AMOUNT no longer does.
    r = lookup(cfg, address, chain)

    if r is None:
        # An address may still be approved by venue name (e.g. a venue's own
        # addresses that aren't enumerated). Only accept if the venue is known
        # AND the address is not explicitly parked/quarantined.
        if venue and _VC and venue in getattr(_VC, "VENUES", {}):
            vok, vprobs = venue_check(venue, action, shape)
            if vok and direction == "in":
                return {
                    "ok": True, "verdict": "APPROVED-BY-VENUE",
                    "address": address, "chain": chain, "venue": venue,
                    "amount_usd": amount_usd, "purpose": purpose,
                    "note": "address not enumerated; approved by venue profile",
                }
            return {
                "ok": False, "verdict": "REFUSED",
                "reason": "address not enumerated AND venue check failed: "
                          + "; ".join(vprobs),
                "address": address, "chain": chain, "venue": venue,
            }
        return {
            "ok": False, "verdict": "REFUSED",
            "reason": "destination is NOT an approved rail",
            "address": address, "chain": chain,
        }

    status = r.get("status", "ACTIVE")
    v = venue or r.get("venue")

    if status != "ACTIVE":
        if direction == "out":
            return {
                "ok": True, "verdict": "APPROVED-EXIT",
                "reason": f"rail is {status}, but EXIT is permitted (never trap capital)",
                "address": address, "chain": r.get("chain"),
                "name": r.get("name"), "venue": v,
            }
        return {
            "ok": False, "verdict": "REFUSED",
            "reason": f"rail is {status} — {r.get('reason', 'no reason recorded')}",
            "address": address, "chain": r.get("chain"),
            "name": r.get("name"), "venue": v,
        }

    # ACTIVE rail — still verify the VENUE supports the action.
    # (The Sep 10 lesson: address approval is necessary, not sufficient.)
    if not skip_venue:
        vok, vprobs = venue_check(v, action, shape)
        if not vok:
            return {
                "ok": False, "verdict": "REFUSED",
                "reason": f"venue '{v}' cannot perform this action: "
                          + "; ".join(vprobs),
                "address": address, "chain": r.get("chain"),
                "name": r.get("name"), "venue": v,
            }

    # ── TRANSIENT destinations need a live per-address approval ───────────
    # Jordan's rule: rotating exchange addresses are approved ONE AT A TIME.
    # Approving one address never approves another, and an approval is
    # consumed on use so it cannot be replayed later.
    if r.get("kind") == "exchange_deposit_transient":
        ok_a, ap, why = require_approval(address, r.get("chain"), amount_usd, r)
        if not ok_a:
            return {
                "ok": False, "verdict": "REFUSED",
                "reason": why,
                "address": address, "chain": r.get("chain"),
                "name": r.get("name"), "venue": v,
            }
        return {
            "ok": True, "verdict": "APPROVED-TRANSIENT",
            "address": address, "chain": r.get("chain"), "name": r.get("name"),
            "venue": v, "amount_usd": amount_usd, "purpose": purpose,
            "approval_id": ap.get("id"),
            "note": (f"one-time approval {ap.get('id')} by "
                     f"{ap.get('approved_by','?')} on {ap.get('approved_on','?')} "
                     "— consumed on use, not reusable"),
        }

    return {
        "ok": True, "verdict": "APPROVED",
        "address": address, "chain": r.get("chain"), "name": r.get("name"),
        "venue": v, "amount_usd": amount_usd, "purpose": purpose,
    }


def check_switch(cfg, src_venue, dst_venue, amount_usd=None):
    """Validate BOTH ends of a rail switch, plus the pairing itself.

    Jordan: 'when we swap rails the guard must be venue-aware.' An address
    check alone cannot tell you whether moving out of LFJ into Blackhole is
    what you intended — this can.
    """
    problems = []

    if _VC is None:
        return False, ["venue-compat unavailable — cannot validate a rail switch"]

    venues = getattr(_VC, "VENUES", {})
    for label, v in (("source", src_venue), ("destination", dst_venue)):
        if v not in venues:
            problems.append(f"{label} venue '{v}' is not in the compatibility registry")

    if problems:
        return False, problems

    src, dst = venues[src_venue], venues[dst_venue]

    # Exit side: allowed as long as the venue exists (never trap capital),
    # but warn if it's a venue we can't actually operate.
    if src.get("maturity") in ("scaffold", "not_built"):
        problems.append(
            f"source '{src_venue}' maturity is '{src['maturity']}' — there is no real "
            f"withdraw path. A switch out of it is a PLAN only, not an execution."
        )

    # ── DESTINATION rail status (capital-guard's own gate) ────────────────
    # venue-compat only knows capability; it does NOT know that we PARKED a
    # venue. A switch INTO a venue with NO active entry rail must be refused.
    #
    # Semantics matter here (caught by this file's selftest, Sep 11 2026): a
    # venue can have one ACTIVE rail and one quarantined SUB-rail. Blackhole is
    # ACTIVE for the CL pool while its gauge is QUARANTINED — that must NOT
    # block depositing into Blackhole. So: refuse only when the destination has
    # NO active rail, and surface the non-active sub-rails as notes.
    venue_rails = [r for r in cfg.get("rails", []) if r.get("venue") == dst_venue]
    active_entry = [r for r in venue_rails if r.get("status", "ACTIVE") == "ACTIVE"]
    blocked_sub = [r for r in venue_rails
                   if r.get("status", "ACTIVE") in ("QUARANTINED", "PARKED")]

    if venue_rails and not active_entry:
        r0 = venue_rails[0]
        problems.append(
            f"destination '{dst_venue}' has NO active rail "
            f"(all {len(venue_rails)} are non-ACTIVE) — {r0.get('reason', 'no reason recorded')}"
        )

    blocked_notes = []
    for r in blocked_sub:
        blocked_notes.append(
            f"NOTE: {dst_venue} sub-rail '{r.get('name')}' is {r.get('status')} — "
            f"do not route to that specific address ({r['address'][:12]}…)"
        )

    # Entry side: must be able to accept capital.
    ok, vprobs = _VC.preflight(dst_venue, "deposit")
    if not ok:
        problems.extend([f"destination: {p}" for p in vprobs])

    # Cross-chain requires a bridge leg.
    if src.get("chain") != dst.get("chain"):
        problems.append(
            f"cross-chain switch ({src.get('chain')} -> {dst.get('chain')}): requires "
            f"the bridge leg (agentic_bridge.py). Confirm it is wired for this pair "
            f"before executing; report the bridge as not_verified if untested."
        )

    # Report what the destination can't do, so the plan is honest.
    notes = []
    if dst.get("shapes"):
        notes.append(f"destination shapes available: {dst['shapes']}")
    if src_venue == "lfj" or dst_venue == "lfj":
        notes.append("LFJ emits TransferBatch (not TransferSingle); exit returns "
                     "ONE-SIDED value — an exit is not a restore.")

    if problems:
        return False, problems + blocked_notes + (["NOTE: " + n for n in notes])
    return True, blocked_notes + ["NOTE: " + n for n in notes]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "guard", "rails", "switch", "selftest",
                                    "approve", "approvals", "consume"])
    ap.add_argument("--to")
    ap.add_argument("--chain")
    ap.add_argument("--venue")
    ap.add_argument("--action", default="deposit")
    ap.add_argument("--shape")
    ap.add_argument("--amount-usd", type=float)
    ap.add_argument("--purpose", default="")
    ap.add_argument("--plan")
    ap.add_argument("--direction", choices=["in", "out"], default="in")
    ap.add_argument("--from", dest="src_venue")
    ap.add_argument("--skip-venue", action="store_true",
                    help="address-only check (escape hatch; venue checks off)")
    ap.add_argument("--approved-by", default="jordan")
    ap.add_argument("--max-usd", type=float)
    ap.add_argument("--id")
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    cfg = load_rails()

    # ── Named wallets (Jordan, Sep 15 2026): "send to jordan" ─────────────
    # Resolve a friendly name to its address BEFORE the guard runs, so a name
    # is exactly as safe as pasting the address (the guard still checks it).
    if args.to and not args.to.startswith("0x"):
        resolved, entry = resolve_name(args.to)
        if resolved:
            print(f"📇 '{args.to}' -> {resolved}  ({entry.get('label','')})")
            args.to = resolved
            if not args.chain and entry.get("chain"):
                args.chain = entry["chain"]
        else:
            print(f"🚨 REFUSED — unknown wallet name '{args.to}'")
            print(f"   known durable names: "
                  f"{', '.join(sorted((json.load(open(WALLETS_PATH)).get('wallets') or {}).keys())) if os.path.exists(WALLETS_PATH) else 'none'}")
            print("   (exchange deposit addresses are transient and never resolve)")
            return 1

    if args.cmd == "approve":
        # Jordan says: "I approve you to send to this wallet."
        if not args.to:
            print("usage: capital-guard.py approve --to <address> --approved-by jordan")
            return 1
        addr = args.to
        if not addr.startswith("0x"):
            resolved, _ = resolve_name(addr)
            if resolved:
                addr = resolved
            else:
                print(f"🚨 cannot approve unknown name '{addr}'")
                return 1
        a = load_approvals()
        dup = [x for x in a["approvals"]
               if x["address"].lower() == addr.lower() and not x.get("consumed_at")]
        if dup:
            print(f"ℹ️  already approved (id {dup[0]['id']}, unconsumed)")
            return 0
        rid = "ap_" + hashlib.sha256(
            (addr.lower() + str(time.time())).encode()).hexdigest()[:12]
        a["approvals"].append({
            "id": rid, "address": addr,
            "chain": args.chain or "avalanche",
            "approved_by": args.approved_by,
            "approved_on": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
            "max_usd": args.max_usd,
            "note": args.note or "one-time send approval (rotating address)",
            "consumed_at": None,
        })
        save_approvals(a)
        print(f"✅ recorded approval {rid}")
        print(f"   address : {addr}")
        print(f"   by      : {args.approved_by}")
        print(f"   cap     : ${args.max_usd}" if args.max_usd else "   cap     : none")
        print("   one-time: consumed on use; approving this address does NOT "
              "approve any other address")
        return 0

    if args.cmd == "approvals":
        for x in load_approvals().get("approvals", []):
            state = ("CONSUMED " + x["consumed_at"]) if x.get("consumed_at") else "UNCONSUMED"
            cap = f"${x['max_usd']}" if x.get("max_usd") is not None else "no cap"
            print(f"  [{state:24s}] {x['id']}  {x['address']}  {cap}  "
                  f"by {x.get('approved_by')} on {x.get('approved_on')}")
        return 0

    if args.cmd == "consume":
        if not args.id:
            print("usage: capital-guard.py consume --id <approval id>")
            return 1
        a = load_approvals()
        hit = False
        for x in a["approvals"]:
            if x["id"] == args.id:
                if x.get("consumed_at"):
                    print(f"ℹ️  {args.id} already consumed at {x['consumed_at']}")
                    return 0
                x["consumed_at"] = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
                hit = True
        if not hit:
            print(f"🚨 no approval with id {args.id}")
            return 1
        save_approvals(a)
        print(f"✅ consumed {args.id} — it can never be reused")
        return 0

    if args.cmd == "rails":
        for r in cfg.get("rails", []):
            print(f"  [{r.get('status','?'):11s}] {r.get('chain','?'):10s} "
                  f"{r['address']}  {r.get('name','')}")
            if r.get("venue"):
                print(f"                ↳ venue: {r['venue']}")
            if r.get("reason"):
                print(f"                ↳ {r['reason']}")
        return 0

    if args.cmd == "check":
        res = check(cfg, args.to, args.chain, args.amount_usd, args.purpose,
                    args.direction, args.venue, args.action, args.shape,
                    args.skip_venue)
        if res["ok"]:
            print(f"✅ {res['verdict']} — {res.get('name')} ({res.get('chain')})")
            if res.get("venue"):
                print(f"   venue: {res['venue']}")
            if res.get("reason"):
                print(f"   {res['reason']}")
            if res.get("note"):
                print(f"   {res['note']}")
            return 0
        print(f"🚨 REFUSED — {res['reason']}")
        print(f"   destination: {res['address']}")
        return 1

    if args.cmd == "switch":
        if not args.src_venue or not args.to:
            print("switch requires --from <venue> --to <venue>")
            return 2
        ok, msgs = check_switch(cfg, args.src_venue, args.to, args.amount_usd)
        if ok:
            print(f"✅ SWITCH APPROVED — {args.src_venue} -> {args.to}")
            for m in msgs:
                print(f"   {m}")
            print("\n   (plan only — execution still requires postcondition "
                  "verification after the move)")
            return 0
        print(f"🚨 SWITCH REFUSED — {args.src_venue} -> {args.to}")
        for m in msgs:
            print(f"   • {m}")
        return 1

    if args.cmd == "guard":
        if not args.plan:
            print("guard requires --plan")
            return 2
        with open(args.plan) as f:
            plan = json.load(f)
        refused = []
        for item in plan:
            res = check(cfg, item.get("to"), item.get("chain"),
                        item.get("amount_usd"), item.get("purpose", ""),
                        item.get("direction", "in"), item.get("venue"),
                        item.get("action", "deposit"), item.get("shape"))
            label = item.get("purpose") or item.get("to")
            if res["ok"]:
                print(f"  ✅ {label} -> {res.get('name') or res.get('venue')}")
            else:
                print(f"  🚨 REFUSED: {label} — {res['reason']}")
                refused.append(item)
        if refused:
            print(f"\n🚨 {len(refused)} destination(s) REFUSED — DO NOT EXECUTE. Fail closed.")
            return 1
        print(f"\n✅ all {len(plan)} destination(s) approved.")
        return 0

    if args.cmd == "selftest":
        cases = [
            (dict(address="0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7",
                  venue="blackhole_cl", action="deposit", shape="curve"),
             True, "Blackhole deposit curve -> APPROVED"),
            (dict(address="0x41100c6d2c6920b10d12cd8d59c8a9aa2ef56fc7",
                  venue="blackhole_cl", action="deposit", shape="bid-ask"),
             True, "Blackhole deposit bid-ask -> APPROVED (real BID_ASK exists)"),
            (dict(address="0x864d4e5ee7318e97483db7eb0912e09f161516ea",
                  venue="lfj", action="deposit"),
             False, "LFJ deposit -> REFUSED (PARKED)"),
            (dict(address="0x864d4e5ee7318e97483db7eb0912e09f161516ea",
                  venue="lfj", direction="out"),
             True, "LFJ EXIT -> APPROVED (never trap capital)"),
            (dict(address="0x3ade52f9779c07471f4b6d5997444c3c2124c1c0",
                  venue="blackhole_cl", action="withdraw"),
             False, "Blackhole gauge -> REFUSED (QUARANTINED)"),
            (dict(address="0xDEADBEEF00000000000000000000000000000000"),
             False, "unknown address -> REFUSED"),
        ]
        fails = 0
        for kw, want_ok, label in cases:
            res = check(cfg, kw.get("address"), kw.get("chain"), None, "",
                        kw.get("direction", "in"), kw.get("venue"),
                        kw.get("action", "deposit"), kw.get("shape"))
            got = res["ok"]
            status = "PASS" if got == want_ok else "**FAIL**"
            if got != want_ok:
                fails += 1
            print(f"  [{status}] {label} (ok={got}, expected {want_ok})")
            if res.get("reason"):
                print(f"           ↳ {res['reason'][:110]}")

        print("\n  --- venue-aware switch checks ---")
        sw = [
            ("blackhole_cl", "lfj", False, "BH -> LFJ: destination PARKED, must refuse"),
            ("lfj", "blackhole_cl", True, "LFJ -> BH: exit + ACTIVE dest, approved"),
        ]
        for src, dst, want_ok, label in sw:
            ok, msgs = check_switch(cfg, src, dst, None)
            status = "PASS" if ok == want_ok else "**FAIL**"
            if ok != want_ok:
                fails += 1
            print(f"  [{status}] {label} (ok={ok}, expected {want_ok})")
            for m in msgs:
                print(f"           ↳ {m[:110]}")

        print(f"\n{'✅ all selftests passed' if fails == 0 else f'🚨 {fails} FAILURES'}")
        return 0 if fails == 0 else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
