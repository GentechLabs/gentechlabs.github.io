#!/usr/bin/env python3
"""
venue-compat.py — the venue compatibility layer for capital-moving agents.

WHY THIS EXISTS (Jordan, Sep 11 2026):
  "it's almost the same as like a video game company testing for different
   platforms for compatibility... we have to test the different major places
   that liquidity is going for each rail to make it compatible and we're gonna
   be troubleshooting a lot, updating a lot."

  Every venue lies in its own way. On Sep 10 2026 four DIFFERENT venue
  assumptions failed silently, AFTER capital had moved:

    1. position tracking by tokenId index 0 -- a re-center MINTS A NEW tokenId,
       leaving the old one drained, so readers watched a $0.22 remnant
    2. LP events assumed TransferSingle -- LFJ emits TransferBatch, so a scan
       reported "0 bins touched" while the wallet held 15
    3. config assumed --shape bid-ask gives concentrated edges -- LFJ only
       deploys Gaussian curve (the flag changes bin SPREAD, not distribution)
    4. deposit assumed composition is preserved -- the add SWAPPED USDC->WAVAX,
       leaving a 100% single-sided, out-of-range position

  All four passed `status=1`. "The tx succeeded" is NOT "we ended up where we
  intended."

THE MODEL
  A venue profile declares what the venue ACTUALLY does, not what we wish it did:
    - preconditions  -- things that must hold BEFORE we send capital
    - postconditions -- things that must hold AFTER, or the action is a FAILURE
    - failure_modes  -- documented ways this venue has burned us, with evidence

  `assert_post()` is the important one: it turns "status=1" into "assert the
  RESULTING STATE." This is V5's claim-verification item applied to money.

USAGE
  python3 venue-compat.py --list
  python3 venue-compat.py --show lfj
  python3 venue-compat.py --preflight lfj --action deposit --shape bid-ask
  python3 venue-compat.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys

# ── Venue profiles ────────────────────────────────────────────────────────
# Ground truth, earned on-chain. Keep the evidence with the claim.

VENUES = {
    "blackhole_cl": {
        "chain": "avalanche",
        "kind": "dex-lp-cl",
        "adapter": "blackhole_cl_adapter.py",
        "maturity": "complete",          # mint/stake/harvest/compound/re-center
        "position_model": "tokenId (NFT, ERC721)",
        "event_model": "Transfer (ERC721)",
        "shapes": ["curve", "bid-ask"],  # real edge-weighted BID_ASK exists
        "failure_modes": [
            {
                "id": "recenter-mints-new-tokenid",
                "what": "re-center (withdraw -> burn -> re-mint) MINTS A NEW tokenId; "
                        "the old one is left drained.",
                "impact": "any reader using tokenOfOwnerByIndex(wallet, 0) tracks the "
                          "EMPTY remnant and reports ~$0 instead of the real position.",
                "evidence": "Sep 11 2026: readers watched #3476545 (~$0.22) while real "
                            "capital sat in #3478420 (~$11.13).",
                "check": "select position by HIGHEST LIQUIDITY, never by index.",
            },
            {
                "id": "gauge-withdraw-reverts",
                "what": "gauge withdraw(0x2e1a7d4d) reverted 22 times on Sep 10. "
                        "NOTE (Treasury correction, Sep 11): the selector is "
                        "withdraw(uint256), NOT withdrawIncentive "
                        "(which is 0x10a46c2e). HQ originally mislabeled this.",
                "impact": "repeated failed calls burn gas on every retry.",
                "evidence": "Sep 10 2026: 22 failed txs, 13:00-16:30 UTC. Caller "
                            "identified as the re-center path in "
                            "blackhole_cl_adapter.py; the gauge is now QUARANTINED in "
                            "capital-guard, so --recenter refuses before signing.",
                "check": "verify the gauge call is valid before signing; never "
                         "blind-retry. Gate the caller, not just the retry.",
            },
            {
                "id": "rpc-lag-after-status-1",
                "what": "a fresh read immediately after a status=1 tx can show stale state.",
                "impact": "verifiers conclude the action failed when it succeeded.",
                "evidence": "pitfall #41: redeploy verifier read 0 bins; settled re-read "
                            "confirmed 11.",
                "check": "re-read with retry; never conclude from a single post-tx read.",
            },
        ],
        "preconditions": [
            {"id": "shape-supported", "kind": "enum", "field": "shape",
             "allowed": ["curve", "bid-ask"]},
        ],
        "postconditions": [
            {"id": "position-visible", "what": "a position with liquidity > 0 exists "
                                               "for this wallet after the action"},
            {"id": "tokenid-captured", "what": "the NEW tokenId is recorded (never assume "
                                               "the id is unchanged)"},
        ],
    },

    "lfj": {
        "chain": "avalanche",
        "kind": "dex-lp-bin",
        "adapter": "steward_execute.py / gta_avax_lp_execute.py",
        "maturity": "partial",           # curve-only
        "position_model": "bins (ERC1155, one id per bin)",
        "event_model": "TransferBatch",  # NOT TransferSingle
        "shapes": ["curve"],             # bid-ask NOT implemented
        "failure_modes": [
            {
                "id": "batch-not-single-events",
                "what": "LFJ add/remove emits ERC1155 TransferBatch, not TransferSingle.",
                "impact": "a TransferSingle scan reports ZERO bins touched -- a confident "
                          "false zero -- while the wallet actually holds them.",
                "evidence": "Sep 11 2026: find_lfj_bins.py printed 'bins touched: 0' "
                            "while the wallet held 15 bins.",
                "check": "scan TransferBatch AND decode (uint256[] ids, uint256[] values) "
                         "with proper offsets.",
            },
            {
                "id": "shape-bid-ask-is-a-lie",
                "what": "--shape bid-ask only changes bin SPREAD (+/-5); the distribution "
                        "is still Gaussian curve. A real edge-weighted LFJ bid-ask "
                        "deployer DOES NOT EXIST.",
                "impact": "config/reports claim BID_ASK while chain shows a curve.",
                "evidence": "Sep 10 2026: shape detector classified the position as "
                            "CURVE (90% confidence) after a '--shape bid-ask' deploy.",
                "check": "refuse shape=bid-ask on LFJ until the deployer exists; "
                         "use blackhole_cl for real concentrated edges.",
            },
            {
                "id": "add-swaps-composition-onesided",
                "what": "adding liquidity can SWAP your composition to one side, leaving "
                        "a single-sided position.",
                "impact": "you deposit 5.5 USDC + 0.71 WAVAX and end up holding only "
                          "WAVAX -- the wrong side of the pair.",
                "evidence": "Sep 10 2026: deposited 5.5 USDC + 0.7115 WAVAX (~$10.96); "
                            "ended holding 0.52 WAVAX and ZERO USDC.",
                "check": "AFTER the add, assert BOTH sides are non-zero (or that "
                         "single-sided was intended).",
            },
            {
                "id": "recenter-can-push-out-of-range",
                "what": "a re-center can leave every bin ABOVE the active bin.",
                "impact": "position is 100% out of range and earns nothing while looking "
                          "perfectly healthy (reserves non-zero, LP tokens held).",
                "evidence": "Sep 11 2026: 15 bins held, active bin 8362973, ALL held bins "
                            "8362980-8362994 above it -- out of range, earning nothing.",
                "check": "AFTER any action, assert the position straddles the active bin "
                         "(at least one bin <= active <= one bin).",
            },
            {
                "id": "exit-restores-value-as-wrong-token",
                "what": "exiting a mispositioned bin LP returns your value in ONE token, "
                        "not the pair. Withdrawing the out-of-range position returned "
                        "~0.52 WAVAX and 0 USDC -- the composition you deposited "
                        "(5.5 USDC + 0.71 WAVAX) is NOT restored by the exit.",
                "impact": "an 'exit' is not a 'restore'. The wallet ends up holding the "
                          "wrong token, so recovery is only half done -- a swap leg is "
                          "still required to get back to the intended composition.",
                "evidence": "Sep 11 2026 recovery (tx 0x4dfac7a1): 15 bins drained to zero, "
                            "~0.52 WAVAX returned. Wallet after: 1.4902 WAVAX, 0.0 USDC. "
                            "The Sep 10 deposit was 5.5 USDC + 0.7115 WAVAX.",
                "check": "after an exit, assert composition matches intent; if the venue "
                         "returns one-sided, plan the swap leg explicitly rather than "
                         "assuming the exit restored the pair.",
            },
        ],
        "preconditions": [
            {"id": "shape-supported", "kind": "enum", "field": "shape",
             "allowed": ["curve"],
             "refuse_message": "LFJ only deploys Gaussian curve. A true edge-weighted "
                               "bid-ask deployer does not exist. Use blackhole_cl for "
                               "concentrated edges."},
        ],
        "postconditions": [
            {"id": "both-sides-nonzero", "what": "position holds BOTH tokenX and tokenY "
                                                 "(unless single-sided was intended)"},
            {"id": "in-range", "what": "at least one held bin is <= active bin (position "
                                       "straddles the active price)"},
            {"id": "bins-captured", "what": "the bin ids actually held are recorded"},
        ],
    },

    "meteora": {
        "chain": "solana",
        "kind": "dex-lp-dlmm",
        "adapter": "meteora_adapter.py",
        "maturity": "scaffold",          # returns "pending", no real tx
        "position_model": "DLMM position",
        "event_model": "unknown",
        "shapes": ["curve"],
        "failure_modes": [
            {"id": "not-implemented",
             "what": "adapter returns 'pending' placeholders; no real Solana "
                     "instruction encoding exists.",
             "impact": "reports LOOK like they worked. Never treat 'pending' as success.",
             "evidence": "Sep 11 2026 scaffold review.",
             "check": "treat any 'pending' result as NOT EXECUTED."},
        ],
        "preconditions": [
            {"id": "execution-implemented", "kind": "gate", "allowed": False,
             "refuse_message": "Meteora execution is a scaffold (no real tx). "
                               "Do not send capital."},
        ],
        "postconditions": [],
    },

    "orca": {
        "chain": "solana", "kind": "dex-lp-cl", "adapter": None,
        "maturity": "not_built", "shapes": [],
        "position_model": "unknown", "event_model": "unknown",
        "failure_modes": [{"id": "not-built", "what": "no adapter exists.",
                           "impact": "cannot execute.", "evidence": "registry",
                           "check": "do not route capital here."}],
        "preconditions": [{"id": "execution-implemented", "kind": "gate", "allowed": False,
                           "refuse_message": "Orca adapter not built."}],
        "postconditions": [],
    },

    "raydium": {
        "chain": "solana", "kind": "dex-lp-amm", "adapter": None,
        "maturity": "not_built", "shapes": [],
        "position_model": "unknown", "event_model": "unknown",
        "failure_modes": [{"id": "not-built", "what": "no adapter exists.",
                           "impact": "cannot execute.", "evidence": "registry",
                           "check": "do not route capital here."}],
        "preconditions": [{"id": "execution-implemented", "kind": "gate", "allowed": False,
                           "refuse_message": "Raydium adapter not built."}],
        "postconditions": [],
    },

    "xlayer": {
        "chain": "x-layer", "kind": "unassessed", "adapter": None,
        "maturity": "unassessed", "shapes": [],
        "position_model": "unknown", "event_model": "unknown",
        "failure_modes": [{"id": "not-assessed",
                           "what": "we claim X-Layer as a chain but have no inventory of "
                                   "its top liquidity venues.",
                           "impact": "cannot state compatibility -- blocks Jordan's "
                                     "public-release gate.",
                           "evidence": "Jordan Sep 11 2026 release gate.",
                           "check": "inventory venues first; then port per venue."}],
        "preconditions": [{"id": "execution-implemented", "kind": "gate", "allowed": False,
                           "refuse_message": "X-Layer venues not assessed yet."}],
        "postconditions": [],
    },

    "hyperliquid": {
        "chain": "hl-l1", "kind": "perp", "adapter": None,
        "maturity": "signal_only", "shapes": [],
        "position_model": "n/a", "event_model": "n/a",
        "failure_modes": [{"id": "compliance-gated",
                           "what": "US gray zone -- read-only by policy.",
                           "impact": "cannot execute.", "evidence": "compliance pivot",
                           "check": "signal-only."}],
        "preconditions": [{"id": "execution-implemented", "kind": "gate", "allowed": False,
                           "refuse_message": "Hyperliquid is read-only (US gray zone)."}],
        "postconditions": [],
    },

    "arc_cctp": {
        "chain": "arc", "kind": "chain-rail", "adapter": "arc_rail.py",
        "maturity": "rail_verified",     # rail reads/verified; NO execution adapter yet
        "shapes": [],
        "position_model": "n/a (no venue carrying yield on day one)",
        "event_model": "n/a",
        "notes": ("Arc mainnet (chainId 5042). Assessed 2026-09-16 launch day. It is a "
                  "LIVE RAIL but NOT a yield home: Aave V4 USDC supply 0.00% (Main spoke "
                  "cap full), Morpho Blue Arc USDC 0.00% ($148.0M supplied vs $9.79 "
                  "borrowed), Aerodrome Slipstream Arc $300.8K TVL. Registered so the "
                  "chain is KNOWN; refused for entry because there is nothing to earn."),
        "failure_modes": [
            {"id": "rpc-requires-user-agent",
             "what": "rpc.mainnet.arc.io returns HTTP 403 body 'error code: 1010' "
                     "(Cloudflare) for a BARE request -- it requires a User-Agent "
                     "header. Alternate hostnames (rpc.arc.io, rpc.arc.network, "
                     "arc-mainnet.rpc.circle.com) do not resolve.",
             "impact": "our other scripts default to bare urllib, so a naive Arc probe "
                       "reads 403 and can be mis-filed as 'chain down' -- or a "
                       "non-raising parser reads the failure as a ZERO.",
             "evidence": "Sep 16 2026, measured 3 ways: no-UA -> 403; browser-UA -> 200 "
                         "0x13b2; generic UA -> 200 0x13b2.",
             "check": "always send a User-Agent; use arc_rail.py, whose rpc() RAISES "
                      "instead of returning a falsy value."},
            {"id": "gas-usdc-decimal-split",
             "what": "the gas token IS USDC but at a DIFFERENT scale: native gas is "
                     "18-decimal, while ERC-20 USDC 0x3600..0000 is 6-decimal (decimals() "
                     "verified == 6 on mainnet).",
             "impact": "any code assuming one decimal count for 'USDC' is off by 10^12 on "
                       "one side -- not a rounding error, a wrong-magnitude transfer.",
             "evidence": "Sep 16 2026: gas 67.12-72.58 Gwei = ~0.000000067 native-USDC "
                         "per gas unit; a 200k-gas tx is ~1.34 USDC cents.",
             "check": "read decimals() per representation; never assume a single scale "
                      "for 'USDC' on Arc."},
            {"id": "zero-yield-day-one",
             "what": "every lending venue on Arc pays 0.00%.",
             "impact": "parking dry powder on Arc earns strictly LESS than the same USDC "
                       "on Avalanche (centrifuge 4.85%) -- Arc is a transit rail, not a "
                       "parking spot.",
             "evidence": "Sep 16 2026 council: Aave V4 0.00%, Morpho 0.00%, Slipstream "
                         "$300.8K TVL.",
             "check": "do not route reserve capital to Arc until a deploy trigger fires "
                      "(USDC APY >= 4.0% sustained, or Slipstream USDC side >= $5M, and "
                      "reserve >= $200). Re-review 2026-10-16."},
        ],
        "preconditions": [{"id": "execution-implemented", "kind": "gate", "allowed": False,
                           "refuse_message": "Arc has no execution adapter and no yield "
                                             "venue. Rail is verified read-only; funding "
                                             "path is CCTP domain 26 when a trigger fires."}],
        "postconditions": [],
    },
}


# ── Preflight ─────────────────────────────────────────────────────────────

def preflight(venue: str, action: str, **kwargs):
    """Return (ok, [problems]). Refuses if any precondition fails."""
    problems = []
    v = VENUES.get(venue)
    if v is None:
        return False, [f"unknown venue '{venue}' -- not in the compatibility registry"]

    if v.get("maturity") in ("not_built", "scaffold", "unassessed", "signal_only"):
        problems.append(
            f"venue '{venue}' maturity is '{v['maturity']}' -- it cannot move capital. "
            f"See failure_modes[{v['failure_modes'][0]['id']}]."
        )

    for pc in v.get("preconditions", []):
        if pc["kind"] == "enum":
            supplied = kwargs.get(pc["field"])
            if supplied is not None and supplied not in pc["allowed"]:
                problems.append(
                    pc.get("refuse_message")
                    or f"{pc['field']}='{supplied}' not allowed on {venue} "
                       f"(allowed: {pc['allowed']})"
                )
        elif pc["kind"] == "gate" and not pc.get("allowed", False):
            problems.append(pc.get("refuse_message", f"gate '{pc['id']}' closed"))

    return (len(problems) == 0), problems


# ── Postconditions ────────────────────────────────────────────────────────

def check_postconditions(venue: str, observed: dict):
    """
    observed = the RESULTING STATE after the action. Returns (ok, [violations]).

    This is the fix for "status=1 is not success". Every Sep 10 failure passed
    status=1 and still left the position wrong.

    Recognised keys (only those present are checked):
      tokenX_amount, tokenY_amount   -> both-sides-nonzero
      bins_held (list of ints), active_bin -> in-range
      bin_ids / token_id             -> captured
    """
    v = VENUES.get(venue)
    if v is None:
        return False, [f"unknown venue '{venue}'"]

    violations = []

    ids = {p["id"] for p in v.get("postconditions", [])}

    if "both-sides-nonzero" in ids:
        if "tokenX_amount" in observed and "tokenY_amount" in observed:
            x, y = observed["tokenX_amount"], observed["tokenY_amount"]
            if x == 0 and y == 0:
                violations.append("both-sides-nonzero: position holds NOTHING on either side")
            elif (x == 0 or y == 0) and not observed.get("single_sided_intended"):
                violations.append(
                    f"both-sides-nonzero: position is ONE-SIDED "
                    f"(tokenX={x}, tokenY={y}) and single-sided was not intended. "
                    f"This is the Sep 10 LFJ composition bug -- the add swapped "
                    f"your composition."
                )

    if "in-range" in ids:
        bins = observed.get("bins_held") or []
        active = observed.get("active_bin")
        if bins and active is not None:
            if not any(b <= active for b in bins):
                violations.append(
                    f"in-range: ALL {len(bins)} held bins are ABOVE the active bin "
                    f"{active} -> 100% out of range, earning nothing. "
                    f"(Sep 11 LFJ: bins {min(bins)}-{max(bins)}, active {active}.)"
                )

    if not violations and not observed:
        violations.append("no resulting state supplied -- postconditions unverifiable. "
                          "A capital action with no post-check is not verified.")

    return (len(violations) == 0), violations


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--show")
    ap.add_argument("--preflight")
    ap.add_argument("--action", default="deposit")
    ap.add_argument("--shape")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.list:
        for name, v in VENUES.items():
            mark = {"complete": "✅", "partial": "⚠️", "scaffold": "⚠️",
                    "not_built": "❌", "unassessed": "❌", "signal_only": "⛔"}.get(
                        v["maturity"], "?")
            print(f"  {mark} {name:13s} {v['chain']:10s} {v['kind']:12s} "
                  f"maturity={v['maturity']:11s} fm={len(v['failure_modes'])}")
        return 0

    if args.show:
        v = VENUES.get(args.show)
        if not v:
            print(f"unknown venue '{args.show}'")
            return 1
        if args.json:
            print(json.dumps(v, indent=2))
            return 0
        print(f"\n=== {args.show} ({v['chain']} / {v['kind']}) ===")
        print(f"  maturity     : {v['maturity']}")
        print(f"  adapter      : {v.get('adapter')}")
        print(f"  position     : {v.get('position_model')}")
        print(f"  events       : {v.get('event_model')}")
        print(f"  shapes       : {v.get('shapes')}")
        print(f"\n  FAILURE MODES ({len(v['failure_modes'])}) -- how this venue lies:")
        for fm in v["failure_modes"]:
            print(f"    • {fm['id']}")
            print(f"        what:     {fm['what']}")
            print(f"        impact:   {fm['impact']}")
            print(f"        evidence: {fm['evidence']}")
            print(f"        check:    {fm['check']}")
        return 0

    if args.preflight:
        kw = {}
        if args.shape:
            kw["shape"] = args.shape
        ok, problems = preflight(args.preflight, args.action, **kw)
        if ok:
            print(f"✅ PREFLIGHT PASS — {args.preflight}/{args.action} may proceed")
            return 0
        print(f"🚨 PREFLIGHT REFUSED — {args.preflight}/{args.action}")
        for p in problems:
            print(f"    • {p}")
        return 1

    if args.selftest:
        print("=== selftest: preconditions ===")
        cases = [
            ("lfj", "deposit", {"shape": "bid-ask"}, False, "LFJ bid-ask must refuse"),
            ("lfj", "deposit", {"shape": "curve"}, True, "LFJ curve ok"),
            ("blackhole_cl", "deposit", {"shape": "bid-ask"}, True, "BH bid-ask ok"),
            ("meteora", "deposit", {}, False, "Meteora scaffold must refuse"),
            ("orca", "deposit", {}, False, "Orca not built must refuse"),
            ("xlayer", "deposit", {}, False, "X-Layer unassessed must refuse"),
            ("hyperliquid", "deposit", {}, False, "HL compliance-gated must refuse"),
            ("arc_cctp", "deposit", {}, False, "Arc: no yield venue + no exec adapter must refuse"),
        ]
        fails = 0
        for venue, action, kw, want_ok, label in cases:
            ok, probs = preflight(venue, action, **kw)
            status = "PASS" if ok == want_ok else "**FAIL**"
            if ok != want_ok:
                fails += 1
            print(f"  [{status}] {label} (ok={ok}, expected {want_ok})")
            for p in probs:
                print(f"           ↳ {p[:100]}")

        print("\n=== selftest: postconditions ===")
        pcases = [
            ("lfj", {"tokenX_amount": 0.52, "tokenY_amount": 0.0}, False,
             "one-sided composition must fail (Sep 10 bug)"),
            ("lfj", {"tokenX_amount": 1.0, "tokenY_amount": 5.0}, True,
             "two-sided composition passes"),
            ("lfj", {"tokenX_amount": 0.52, "tokenY_amount": 0.0,
                     "bins_held": [8362980, 8362994], "active_bin": 8362973}, False,
             "out-of-range must fail (Sep 11 bug)"),
            ("lfj", {"tokenX_amount": 1.0, "tokenY_amount": 5.0,
                     "bins_held": [8362970, 8362975], "active_bin": 8362973}, True,
             "straddling active bin passes"),
            ("lfj", {}, False, "no resulting state must fail (unverifiable)"),
        ]
        for venue, obs, want_ok, label in pcases:
            ok, viols = check_postconditions(venue, obs)
            status = "PASS" if ok == want_ok else "**FAIL**"
            if ok != want_ok:
                fails += 1
            print(f"  [{status}] {label} (ok={ok}, expected {want_ok})")
            for v_ in viols:
                print(f"           ↳ {v_[:110]}")

        print(f"\n{'✅ all selftests passed' if fails == 0 else f'🚨 {fails} selftest FAILURES'}")
        return 0 if fails == 0 else 1

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
