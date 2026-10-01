#!/usr/bin/env python3
"""Refresh the LIVE treasury-state.json capital block from CHAIN TRUTH.

WHY THIS EXISTS
  The state file once said `deployed_usd: 6.1` while the chain said $24.40.
  Every cron reads this file before it speaks or acts, so a stale capital block
  silently misinforms the whole ring.

Sep 15 2026 REWRITE — the file used to HARDCODE the figures:
    DEPLOYED_USD = 24.40   # <-- constant, but labelled "chain-read"
  That is a fabricated provenance claim: it kept reporting $24.40 for three
  days and would keep reporting it after the farm was fully exited to $0.33.
  Jordan's rule is "we want the truth, no stale data" — so the numbers now come
  from a REAL settled chain read every time (value_now.py --json). If that read
  fails, this script REFUSES to write rather than invent a figure.

MIRROR DIRECTION
  The live (repos) file is RUNTIME state written by the executor, so the vault
  mirror is refreshed FROM it — never the other way (vault->repos would clobber
  live state).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

LIVE = Path("/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking/treasury-state.json")
VAULT = Path("/root/vaults/gentech/10-Labs/agent-kit-self-tracking/treasury-state.json")
PROFILE = Path("/root/.hermes/profiles/gentech-treasury/scripts/treasury-state.json")

HERE = Path(__file__).resolve().parent
VALUE_NOW = HERE / "value_now.py"

GATE_FLOOR_USD = 25.0


def chain_read():
    """Settled chain read. Returns dict or None.

    ── IT WAS READING A VENUE WE DO NOT HOLD (fixed 2026-09-28) ─────────────────────────────────
    This called ONLY `value_now.py`, which values the Blackhole CL NFT on **Base**. Our live books
    are **LFJ Liquidity Book on Avalanche**. So the treasury's own source of truth reported
    `deployed_usd: 0.00` and a winddown note reading *"FLAT — the treasury holds no deployed
    liquidity"* — while the chain had **$146.79 (jordan) + $47.34 (dadrian) deployed and earning**.
    Measured, same minute:

        treasury-state.json : deployed_usd 0.0   |  "FLAT — holds no deployed liquidity"
        steward_progress    : lp_usd     146.79  |  in_range True

    **The treasury's brain said it was flat while it was earning.** Everything that reads this file
    — the council, the mode logic, the milestone rank, the reports — was reasoning from a zero.
    That is the false-value family at the highest level we have: not a wrong number, but the
    document that defines our position saying we have none.

    Now it reads BOTH venues and sums them, reporting each leg separately so a future divergence is
    visible rather than averaged away.
    """
    bh = None
    for attempt in range(1, 4):
        try:
            out = subprocess.run([sys.executable, str(VALUE_NOW), "--json"],
                                 capture_output=True, text=True, timeout=180)
            for line in out.stdout.splitlines():
                if line.startswith("__JSON__"):
                    bh = json.loads(line[len("__JSON__"):])
                    break
            if bh:
                break
        except Exception as e:
            print(f"  value_now attempt {attempt} failed: {str(e)[:90]}")

    # The REAL venue: our own discover_positions, the same reader the pages and steward_progress
    # use. Per-tenant so one tenant's failure cannot zero another's — and any tenant that fails to
    # read makes the whole figure UNRELIABLE rather than silently smaller.
    lfj_total = 0.0
    per_tenant = {}
    lfj_ok = True
    _saved = {k: os.environ.get(k) for k in ("STEWARD_TENANT", "STEWARD_WALLET")}
    try:
        from steward_progress import _active_tenants, _tenant_wallet, read_wallet_value
    except Exception as e:
        return None
    for t in _active_tenants():
        try:
            w = _tenant_wallet(t)
            if not w:
                per_tenant[t] = "UNREADABLE: no wallet in registry"
                lfj_ok = False
                continue
            # BOTH must be set. `read_wallet_value()` resolves `STEWARD_WALLET` (env) or the config
            # file — and that file holds JORDAN's wallet. Setting only STEWARD_TENANT (my first
            # attempt) left the wallet at the config default, so BOTH tenants read Jordan's book
            # and the total double-counted him: measured $175.50 instead of the true $194.10
            # (jordan $146.77 + dadrian $47.33). A per-tenant loop must set the WALLET, because
            # the wallet is what identifies the tenant.
            os.environ["STEWARD_TENANT"] = t
            os.environ["STEWARD_WALLET"] = w
            v = read_wallet_value()
            if "error" in v:
                per_tenant[t] = f"UNREADABLE: {v['error']}"
                lfj_ok = False
                continue
            lp = float(v.get("lp_usd") or 0.0)
            lfj_total += lp
            per_tenant[t] = round(lp, 2)
        except Exception as e:
            per_tenant[t] = f"UNREADABLE: {type(e).__name__}"
            lfj_ok = False
    # Restore: this runs inside cron processes that carry on afterwards, and leaking a tenant's
    # wallet into the environment would make a LATER read in the same process wrong.
    for k, val in _saved.items():
        if val is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = val

    if bh is None and not per_tenant:
        return None
    if bh is None:
        return None

    deployed = float(bh.get("deployed_usd") or 0.0) + lfj_total
    dry = float(bh.get("dry_powder_usd") or 0.0)
    return {
        "deployed_usd": round(deployed, 2),
        "dry_powder_usd": round(dry, 2),
        "blackhole_deployed_usd": round(float(bh.get("deployed_usd") or 0.0), 2),
        "lfj_deployed_usd": round(lfj_total, 2),
        "lfj_per_tenant": per_tenant,
        "lfj_read_complete": lfj_ok,
        # If ANY tenant failed to read, the total is a lower bound, not a measurement. Saying so is
        # the difference between "we hold $194" and "we hold at least $194 and cannot see the rest".
        "deployed_is_lower_bound": (not lfj_ok),
        "loose_wavax_usd": bh.get("loose_wavax_usd", 0.0),
        "loose_usdc_usd": bh.get("loose_usdc_usd", 0.0),
        "loose_avax_usd": bh.get("loose_avax_usd", 0.0),
        "avax_usd": bh.get("avax_usd", 0.0),
        "measured_at": bh.get("measured_at"),
        "source": "chain-read (value_now Blackhole + discover_positions LFJ, settled)",
    }


def main():
    live = json.loads(LIVE.read_text())
    before = dict(live.get("capital") or {})

    truth = chain_read()
    if truth is None:
        # Fail closed: never invent a capital figure.
        print("🚨 REFUSED — chain read failed; NOT writing a capital block from "
              "stale or hardcoded numbers.", file=sys.stderr)
        return 1

    deployed = float(truth["deployed_usd"])
    dry = float(truth["dry_powder_usd"])

    _lower = truth.get("deployed_is_lower_bound")
    live["capital"] = {
        "deployed_usd": deployed,
        "dry_powder_usd": dry,
        "gate_floor_usd": GATE_FLOOR_USD,
        "source": truth["source"],
        "measured_at": truth["measured_at"],
        # Name every leg. A single total that silently sums two venues is how "the CL position is
        # $0.00" was read as "the treasury is flat" while LFJ held real money.
        "blackhole_deployed_usd": truth.get("blackhole_deployed_usd"),
        "lfj_deployed_usd": truth.get("lfj_deployed_usd"),
        "lfj_per_tenant": truth.get("lfj_per_tenant"),
        "deployed_is_lower_bound": _lower,
        "note": (f"Live chain read: DEPLOYED ${deployed:.2f} "
                 f"(LFJ Liquidity Book/Avalanche ${truth.get('lfj_deployed_usd', 0):.2f} "
                 f"across {truth.get('lfj_per_tenant')} + Blackhole CL/Base "
                 f"${truth.get('blackhole_deployed_usd', 0):.2f}); idle ${dry:.2f} "
                 f"(WAVAX ${truth['loose_wavax_usd']:.2f} + USDC ${truth['loose_usdc_usd']:.2f} "
                 f"+ AVAX ${truth['loose_avax_usd']:.2f}). AVAX ${truth['avax_usd']:.2f}. "
                 + ("⚠️ AT LEAST THIS MUCH — a tenant failed to read, so the total is a LOWER "
                    "BOUND, not a measurement. " if _lower else "")
                 + "Any older cb_btc_spot entry is a separate Base position and is NOT included."),
    }
    print(f"  capital: deployed ${before.get('deployed_usd')} -> ${deployed} "
          f"| idle ${before.get('dry_powder_usd')} -> ${dry}")

    if deployed < 0.01 and dry < 1.0 and not _lower:
        # Only claim FLAT on a COMPLETE read. An unreadable tenant is indistinguishable from an
        # empty one — declaring "we hold nothing" from a failed read is the exact bug this file
        # just had, one level down.
        live["winddown_note"] = (
            f"FLAT — the treasury holds no deployed liquidity as of "
            f"{truth['measured_at']}. Both venues read zero: LFJ Liquidity Book "
            f"${truth.get('lfj_deployed_usd', 0):.2f}, Blackhole CL "
            f"${truth.get('blackhole_deployed_usd', 0):.2f}. "
            f"The Blackhole CL farm was exited by orchestrator decision on 2026-09-15 "
            f"(USDC remitted to Jordan). Idle balance is ${dry:.2f}."
        )
    else:
        live["winddown_note"] = (
            f"SUPERSEDED — kept for history. Aug 21 the AVAX farm was pulled flat. "
            f"Current capital per the live chain read above ({truth['measured_at']})."
        )

    txt = json.dumps(live, indent=2) + "\n"
    LIVE.write_text(txt)
    VAULT.write_text(txt)          # mirror refreshed FROM live (correct direction)
    PROFILE.write_text(txt)

    print(f"  ✅ live written   {LIVE}")
    print(f"  ✅ vault mirrored {VAULT}")
    print(f"  ✅ profile    {PROFILE}")

    # verify by reading back — a write is not a write until it is re-read
    a = json.loads(LIVE.read_text())
    b = json.loads(VAULT.read_text())
    ok = (a["mode"] == b["mode"]
          and a["capital"]["deployed_usd"] == b["capital"]["deployed_usd"])
    print(f"  verify: deployed=${a['capital']['deployed_usd']} "
          f"mode={a['mode']} vault={'OK' if a['mode']==b['mode'] else 'DRIFTED'} "
          f"{'✅ IN SYNC' if ok else '❌ STILL DRIFTED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
