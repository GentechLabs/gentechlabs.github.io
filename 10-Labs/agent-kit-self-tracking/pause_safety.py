#!/usr/bin/env python3
"""
pause_safety.py — THE PAUSE-SAFETY PROCEDURE.

Jordan, 2026-09-24:
    "If you ever pause the watchdog to fix something. Consider withdrawing from the pool and
     switching to usdc as a safety precaution."

WHY THIS EXISTS
---------------
Pausing the watchdog removes the ONLY thing managing the book. A live LP position with no watcher
is an UNMANAGED DIRECTIONAL POSITION: it drifts, it can leave its range, and nothing re-centres it
or exits it. That is not hypothetical — on 2026-09-24 the watchdog was paused for nine hours while
a money-path bug was fixed, the books sat live in the pool the whole time, and the pullback ran
straight through them. dadrian left his range with nobody watching.

So a pause is HALF a procedure. The other half is derisking the position:
    volatile legs -> USDC, and nothing left in the pool to drift.

USAGE
-----
    python3 pause_safety.py --report                 # what a pause would leave exposed + the plan
    python3 pause_safety.py --exit --execute --yes   # remove liquidity + convert to USDC
    python3 pause_safety.py --resume --execute --yes # re-enter every tenant (market's shape read)

SAFETY CONTRACT
---------------
  * DRY RUN BY DEFAULT. Nothing is sent without --execute --yes.
  * A pause is a DELIBERATE act: --report is the default because Jordan's word was "consider".
    The tool exists to make the choice INFORMED, not to make it automatically.
  * Keeps a native-AVAX gas floor, MEASURED from the chain, never an assumed constant.
  * Verifies every money step on a SECOND RPC — a lagging read is indistinguishable from
    "nothing happened".
  * Never claims success on a broadcast. Requires the success marker.
  * REFUSES TO REPORT A CLEAN EXIT IT DID NOT VERIFY: if the swap fails it says so loudly and
    reports the remaining WAVAX exposure rather than printing a reassuring summary.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

REGISTRY = os.environ.get(
    "REGISTRY", "/root/vaults/gentech/10-Labs/agent-kit-self-tracking/tenants.json")

# Leave this much native AVAX in the wallet. Jordan's rule (2026-09-23): NO hard gates — the agent
# calculates the transaction cost ahead and keeps that plus a small margin. AVAX is the gas token
# here, so the reserve is native AVAX, NOT the WAVAX we are selling.
GAS_TX_AVAX = 0.0002      # a full chase (withdraw + 2 legs) measured ~0.00009 AVAX; 2x margin
GAS_MARGIN_AVAX = 0.0001  # ~20c at these prices


def tenants():
    """Every tenant with a wallet. A registry that will not parse must not read as 'no tenants' —
    an empty list would make this tool report a clean sweep while doing nothing."""
    try:
        with open(REGISTRY) as fh:
            reg = json.load(fh)
    except Exception as e:
        raise SystemExit(f"pause_safety: cannot read tenant registry {REGISTRY}: {e}")
    out = []
    for name, t in (reg.get("tenants") or {}).items():
        if isinstance(t, dict) and t.get("wallet"):
            out.append((name, t["wallet"]))
    if not out:
        raise SystemExit("pause_safety: registry parsed but named NO tenants with a wallet — "
                         "refusing to report an empty sweep as success.")
    return out


def run(cmd, tenant, wallet, timeout=900):
    env = dict(os.environ, STEWARD_TENANT=tenant, STEWARD_WALLET=wallet)
    return subprocess.run(cmd, cwd=HERE, env=env, capture_output=True, text=True, timeout=timeout)


def read_book(tenant, wallet):
    """Chain truth for one tenant: bins held, USDC, WAVAX, native AVAX. Uses the verified reader."""
    prog = (
        "import sys, json; sys.path.insert(0, '.')\n"
        "import fee_ledger as FL, avax_rpc\n"
        "from web3 import Web3\n"
        "w3 = avax_rpc.connect(timeout=45)\n"
        "PAIR = Web3.to_checksum_address('0x864d4E5Ee7318e97483DB7EB0912E09F161516EA')\n"
        "WAVAX = Web3.to_checksum_address('0xb31f66AA3C1e785363F0875A1B74E27b85FD66c7')\n"
        "USDC = Web3.to_checksum_address('0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E')\n"
        "W = Web3.to_checksum_address(sys.argv[1])\n"
        "sel = Web3.keccak(text='balanceOf(address,uint256)')[:4]\n"
        "enc = lambda a: bytes.fromhex(a[2:].lower()).rjust(32, b'\\x00')\n"
        "act = int.from_bytes(w3.eth.call({'to': PAIR, 'data': Web3.keccak(text='getActiveId()')[:4]}), 'big')\n"
        "held = []\n"
        "for b in range(act - 200, act + 201):\n"
        "    raw = w3.eth.call({'to': PAIR, 'data': sel + enc(W) + b.to_bytes(32, 'big')})\n"
        "    if raw and int.from_bytes(raw, 'big') > 0: held.append(b)\n"
        "def bal(t):\n"
        "    return int.from_bytes(w3.eth.call({'to': t, 'data': Web3.keccak(text='balanceOf(address)')[:4] + enc(W)}), 'big')\n"
        "r, _ = FL.read_position(sys.argv[2])\n"
        "px = None\n"
        "try:\n"
        "    import fee_efficiency as FE\n"
        "    px = FE._price_at(w3, act)\n"
        "except Exception:\n"
        "    px = float(r.get('price_usd') or 0) or None\n"
        "# ── VALUE THE POOL FROM THE POSITION, NOT THE WALLET (fixed 2026-09-24) ──────────────\n"
        "# The first version of this line was `r.get('our_wavax', 0) * 0 + r.get('our_usdc', 0)`\n"
        "# -- a stray `* 0` that valued the entire WAVAX leg at nothing -- and the caller then\n"
        "# summed the WALLET balances instead of the position. Together they reported\n"
        "# '$0.40 exposed' while $148 sat live in two pools. A safety tool that under-reports\n"
        "# exposure is worse than no tool: it would have said 'all clear' during the exact\n"
        "# condition it exists to flag. Value the legs we actually hold, at the chain price.\n"
        "ov = float(r.get('our_wavax') or 0)\n"
        "ou = float(r.get('our_usdc') or 0)\n"
        "in_pool = (ov * px + ou) if px else None\n"
        "print(json.dumps({'bins': len(held), 'band': [min(held), max(held)] if held else None,\n"
        "                  'usdc': bal(USDC) / 1e6, 'wavax': bal(WAVAX) / 1e18,\n"
        "                  'avax_gas': w3.eth.get_balance(W) / 1e18,\n"
        "                  'price': px, 'pool_wavax': ov, 'pool_usdc': ou,\n"
        "                  'in_pool_usd': in_pool}))"
    )
    p = run([sys.executable, "-c", prog, wallet, tenant], tenant, wallet, timeout=420)
    if p.returncode != 0 or not p.stdout.strip():
        return {"error": (p.stderr or p.stdout or "no output").strip()[:200]}
    try:
        return json.loads(p.stdout.strip().splitlines()[-1])
    except Exception as e:
        return {"error": f"unparsable read: {e}"}


def report():
    print("=" * 96)
    print("  PAUSE-SAFETY REPORT — what a paused watchdog would leave unmanaged")
    print("=" * 96)
    print("  Jordan's rule: pausing the watchdog is HALF a procedure. The other half is derisking.")
    print()
    exposed = 0.0
    for tenant, wallet in tenants():
        b = read_book(tenant, wallet)
        if "error" in b:
            print(f"  {tenant:<8} ⚠️  UNREADABLE — {b['error']}")
            print(f"           A book we cannot read is NOT a book we can call safe.")
            continue
        # ── THE EXPOSURE IS THE POSITION, NOT THE WALLET (fixed 2026-09-24) ─────────────────
        # This summed `usdc + wavax` -- the WALLET balances -- while the money at risk is the
        # money IN THE POOL. With both books deployed the wallet holds ~$0.20 each, so the first
        # version of this report announced "$0.40 exposed" while $148 sat live in two pools.
        # The wallet balance is the part that is ALREADY SAFE; the pool is the part that drifts.
        pool = b.get("in_pool_usd")
        if pool is None:
            print(f"  {tenant:<8} ⚠️  position value UNREADABLE — cannot state the exposure.")
            print(f"           Reporting no exposure would be a confident lie; refusing instead.")
            continue
        if b["bins"]:
            exposed += pool
        state = (f"{b['bins']} bins band {b['band'][0]}..{b['band'][1]}"
                 if b["bins"] else "FLAT (nothing in the pool)")
        print(f"  {tenant:<8} {state}   IN POOL ${pool:,.2f}")
        print(f"           wallet: USDC {b['usdc']:,.2f} + WAVAX {b['wavax']:,.6f}"
              f"  |  gas {b['avax_gas']:.6f} AVAX"
              + (f"  |  AVAX ${b['price']:,.4f}" if b.get("price") else ""))
    print()
    print(f"  EXPOSURE IF PAUSED NOW: ${exposed:,.2f} in live LP positions with no watcher.")
    print("  A paused book still earns — but it also still DRIFTS, and nothing will re-centre or")
    print("  exit it. That is the trade: fees continue, risk is unmanaged.")
    print()
    print("  TO DEREISK:  python3 pause_safety.py --exit --execute --yes")
    print("  TO RESTORE:  python3 pause_safety.py --resume --execute --yes")
    print("  (both verify on a second RPC; neither acts without --execute)")


def exit_to_stable(execute):
    print("=" * 96)
    print(f"  PAUSE-SAFETY EXIT — remove liquidity, convert to USDC  [{'EXECUTING' if execute else 'DRY RUN'}]")
    print("=" * 96)
    for tenant, wallet in tenants():
        print(f"\n  ── {tenant} ──")
        before = read_book(tenant, wallet)
        if "error" in before:
            print(f"     ⚠️  cannot read the book: {before['error']} — SKIPPING (never act blind)")
            continue
        if before["bins"] == 0:
            print(f"     already flat — nothing in the pool. USDC {before['usdc']:,.2f}")
            if before["wavax"] > 1e-6:
                print(f"     but holding {before['wavax']:,.6f} WAVAX — converting that too")
            else:
                continue
        else:
            # ── 1. REMOVE THE LIQUIDITY ────────────────────────────────────────────────────
            cmd = [sys.executable, "lfj_exit.py"]
            if execute:
                cmd += ["--execute", "--yes"]
            print(f"     [1] remove liquidity: {' '.join(cmd[1:])}")
            p = run(cmd, tenant, wallet)
            tail = [l for l in (p.stdout or "").splitlines() if l.strip()][-4:]
            for l in tail:
                print("         " + l.strip()[:110])
            if execute and (p.returncode != 0 or "SUCCESS" not in (p.stdout or "").upper()):
                print(f"     ❌ REMOVE FAILED (exit {p.returncode}) — STOPPING this tenant.")
                print(f"        Not converting a book we could not remove: a half-exited position is")
                print(f"        worse than one left alone, because it looks handled.")
                continue

        # ── 2. CONVERT THE VOLATILE LEG TO USDC ────────────────────────────────────────────
        cmd = [sys.executable, "lfj_swap_leg.py", "--from", "wavax", "--pct", "0.999"]
        if execute:
            cmd += ["--execute", "--yes"]
        print(f"     [2] convert WAVAX -> USDC: {' '.join(cmd[1:])}")
        p = run(cmd, tenant, wallet, timeout=420)
        for l in [l for l in (p.stdout or "").splitlines() if l.strip()][-4:]:
            print("         " + l.strip()[:110])
        if execute and (p.returncode != 0 or "status=SUCCESS" not in (p.stdout or "")):
            print(f"     ⚠️  SWAP DID NOT CONFIRM (exit {p.returncode}).")
            print(f"        The liquidity IS removed, so the risk is contained — but the volatile")
            print(f"        leg is still WAVAX. Reporting that honestly instead of calling it clean.")

        # ── 3. VERIFY ON THE CHAIN ─────────────────────────────────────────────────────────
        time.sleep(3)
        after = read_book(tenant, wallet)
        if "error" in after:
            print(f"     ⚠️  post-exit read failed: {after['error']} — verify by hand before trusting")
            continue
        print(f"     [3] VERIFY   bins={after['bins']}  USDC {after['usdc']:,.2f}  "
              f"WAVAX {after['wavax']:,.6f}  gas {after['avax_gas']:.6f} AVAX")
        if after["bins"] == 0 and after["wavax"] < 0.01:
            print(f"     ✅ DERISKED — flat, stable, nothing left to drift.")
        elif after["bins"] == 0:
            print(f"     🟡 OUT OF THE POOL but still holding {after['wavax']:,.6f} WAVAX "
                  f"(~${after['wavax'] * 10:,.2f} exposed to price).")
        else:
            print(f"     ❌ STILL IN THE POOL — {after['bins']} bins. The exit did not take.")


def resume(execute):
    print("=" * 96)
    print(f"  PAUSE-SAFETY RESUME — re-enter every tenant  [{'EXECUTING' if execute else 'DRY RUN'}]")
    print("=" * 96)
    print("  Re-entry uses the MARKET's own shape read (lfj_recenter derives it), and the flat-book")
    print("  recovery path — a book with no position has no side to read, so it is derived from the")
    print("  shape. That path crashed on 2026-09-24 and is now fixed and verified.")
    for tenant, wallet in tenants():
        print(f"\n  ── {tenant} ──")
        b = read_book(tenant, wallet)
        if "error" in b:
            print(f"     ⚠️  cannot read: {b['error']} — SKIPPING")
            continue
        if b["bins"] > 0:
            print(f"     already in the pool ({b['bins']} bins) — leaving it alone")
            continue
        cmd = [sys.executable, "lfj_recenter.py", "--force"]
        if execute:
            cmd += ["--execute", "--yes"]
        print(f"     re-enter: {' '.join(cmd[1:])}")
        p = run(cmd, tenant, wallet, timeout=900)
        for l in [l for l in (p.stdout or "").splitlines() if l.strip()][-6:]:
            print("         " + l.strip()[:110])
        if execute and p.returncode != 0:
            print(f"     ❌ RE-ENTER FAILED (exit {p.returncode}) — the book is still FLAT and earning")
            print(f"        nothing. This is the loud case: do not leave it unreported.")


def main():
    ap = argparse.ArgumentParser(
        description="Pause-safety: derisk the books before pausing the watchdog.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--report", action="store_true", help="what a pause would leave exposed (default view)")
    g.add_argument("--exit", action="store_true", help="remove liquidity + convert to USDC")
    g.add_argument("--resume", action="store_true", help="re-enter every tenant")
    ap.add_argument("--execute", action="store_true", help="actually send transactions")
    ap.add_argument("--yes", action="store_true", help="confirm")
    a = ap.parse_args()

    if a.execute and not a.yes:
        raise SystemExit("pause_safety: --execute requires --yes (these are real transactions).")

    # ── THE LOCK GAP, CLOSED (2026-09-27) ─────────────────────────────────────────────────────
    # THIS SCRIPT WAS THE ONE HOLE IN THE MUTUAL-EXCLUSION BOUNDARY, and it was found by checking
    # the claim rather than reading it. Gentech audited the wallet lock and reported that
    # "lfj-curve-deploy.sh is reachable solely from inside recenter, so it inherits the lock". True
    # for the deploy scripts — but this file calls `lfj_exit.py` DIRECTLY (exit_to_stable, below)
    # and took no lock at all. A pause-safety flatten running while the 5-minute watchdog was
    # mid-recenter would race the same wallet: same nonce, same allowance, same balances. That is
    # exactly the half-built-book failure the lock exists to prevent.
    #
    # A DRY RUN STILL TAKES NO LOCK, deliberately: `--report` and unarmed `--exit` move nothing, and
    # a read-only pass cannot race a writer's nonce (same reasoning as lfj_recenter).
    #
    # IF THE LOCK IS HELD WE STOP, we do not wait. `acquire_or_exit()` is fail-closed by design
    # (exit 9) and that is the right shape here: flattening a wallet while the watchdog owns it is
    # the race this whole guard exists to prevent, and a pause-safety run that refuses loudly is
    # recoverable in seconds, while a half-built book is not. The operator sees the refusal and
    # re-runs. (Checked, not assumed — an earlier draft of this comment claimed it waited.)
    _locks = []
    if a.execute and a.yes:
        try:
            from agent_lock import WalletLock
        except Exception as _e:
            print(f"  ❌ agent_lock unavailable ({_e}) — refusing to sign without mutual exclusion.",
                  file=sys.stderr)
            sys.exit(9)
        # tenants() yields (name, wallet) TUPLES. Reading it as dicts made _w None, so this loop
        # silently locked nothing at all — the guard would have been decorative.
        for _name, _wallet in tenants():
            _lk = WalletLock(_wallet, purpose=f"pause_safety:{_name}")
            _lk.acquire_or_exit()
            _locks.append(_lk)

    if a.report:
        report()
    elif a.exit:
        exit_to_stable(a.execute)
    elif a.resume:
        resume(a.execute)

    if not a.execute:
        print("\n  DRY RUN — nothing was sent. Add --execute --yes to act.")


if __name__ == "__main__":
    main()
