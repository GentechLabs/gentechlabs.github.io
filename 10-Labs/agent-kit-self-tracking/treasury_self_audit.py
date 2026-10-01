#!/usr/bin/env python3
"""TREASURY SELF-AUDIT — "what could I be missing?"

Jordan Sep 11 2026: "what if you decided to run an audit yourself... we should
have the thought process of what could I be missing?"

Every bug found on Sep 11 shared ONE root cause: the code assumed something
about the world that nobody verified against ground truth.

  - vfat API shape changed      -> assumed field path, never re-validated
  - index-0 position selection  -> assumed "first NFT is our position"
  - config-derived valuation    -> assumed funded_usd was truth, not a guess
  - harvest read wallet balance -> assumed claimed == claimable
  - invalid swap route          -> assumed a pool contained BLACK (it didn't)
  - wrong router                -> assumed the router matched the factory
  - success printed pre-status  -> assumed a sent tx succeeded

This script hunts those classes mechanically, so they surface BEFORE Jordan
finds them. Each check is a pattern that catches a whole bug family.

Usage:  python3 treasury_self_audit.py [--json]
Exit:   0 = clean, 1 = findings
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from steward_identity import (wallet as _sw_wallet, key_path as _sw_keypath)

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

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
RPC = _avax_url()
VAULT = "/root/vaults/gentech/10-Labs/agent-kit-self-tracking"
REPOS = "/root/repos/gentechlabs.github.io/10-Labs/agent-kit-self-tracking"

# Files that actually run in the treasury.
CORE = [
    "blackhole_cl_adapter.py", "discover_positions.py", "auto_compound.py",
    "steward_fee_ledger.py", "steward_farm_report.py", "steward_state.py",
    "rebalance_swap.py", "blackhole_fee_reader.py", "steward_execute.py",
    "steward_rebalance.py", "steward_progress.py", "strategy_desk.py",
    "vfat_blackhole.py",
]

findings: list[dict] = []


def add(sev, cls, where, msg, fix=""):
    findings.append({"sev": sev, "class": cls, "where": where, "msg": msg, "fix": fix})


def rpc(method, params):
    d = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    req = urllib.request.Request(RPC, json.dumps(d).encode(),
                                 {"Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=25)).get("result")
    except Exception:
        return None


def read(f):
    p = os.path.join(SCRIPTS, f)
    try:
        return open(p).read()
    except Exception:
        return ""


# ── CHECK 1: success printed before tx-status verification ───────────────
# Bug class that produced the compound false-positive: "✅ compounded" printed
# on a REVERTED tx because the success line preceded the status check.
def check_success_before_status():
    for f in CORE:
        src = read(f)
        if not src:
            continue
        lines = src.splitlines()
        for i, ln in enumerate(lines):
            if "✅" not in ln or "status=" not in ln:
                continue
            # a guard may sit BEFORE the print (preferred) or shortly after.
            # Checking only forward produced false positives on correctly
            # ordered code, so scan both directions.
            before = "\n".join(lines[max(0, i - 6):i])
            after = "\n".join(lines[i + 1:i + 9])
            guarded = bool(re.search(r"status['\"]?\]?\s*!=\s*1|status\s*!=\s*1", before + after))
            if not guarded:
                add("HIGH", "success-before-status", f"{f}:{i+1}",
                    "prints ✅ with status before verifying it",
                    "move the print AFTER `if rcpt['status'] != 1: return/exit`")


# ── CHECK 2: position selection by INDEX instead of by VALUE ────────────
# A re-center mints a NEW tokenId and leaves a drained remnant. Selecting
# index 0 grabs the empty one.
def check_index_selection():
    for f in CORE:
        src = read(f)
        if not src:
            continue
        for m in re.finditer(r"tokenOfOwnerByIndex\([^)]*,\s*i\s*\)", src):
            ln = src[:m.start()].count("\n") + 1
            # Is this inside a helper that ranks by liquidity?
            ctx = src[max(0, m.start() - 900):m.start()]
            # valid when it ranks by liquidity, OR when it is the explicit
            # "find a DIFFERENT tokenId" fallback after a re-mint (it compares
            # against token_id, which the ranked selector already chose).
            ranked = ("liq > best_liq" in ctx or "best_liq" in ctx
                      or "tid != token_id" in src[m.start():m.start() + 200])
            if not ranked:
                add("HIGH", "index-selection", f"{f}:{ln}",
                    "selects position by loop index without ranking by liquidity",
                    "use select_blackhole_position() (highest liquidity)")


# ── CHECK 3: hardcoded addresses actually exist on chain ────────────────
# Addresses that are legitimately NOT contracts on Avalanche:
#  - our own wallet (an EOA by definition)
#  - token addresses belonging to OTHER chains (base/ethereum/arbitrum maps)
SKIP_ADDRS = {"0x572abd6461bed2258615e6b99c585ab7c5d05037"}
OTHER_CHAIN_HINTS = ("base", "ethereum", "arbitrum", "optimism", "polygon")


def check_addresses():
    seen = set()
    for f in CORE:
        src = read(f)
        lines = src.splitlines()
        for a in re.findall(r"0x[a-fA-F0-9]{40}", src):
            if a.lower() in seen or a.lower() in SKIP_ADDRS:
                continue
            seen.add(a.lower())
            # skip if the address sits near another chain's name (token map)
            near = False
            for i, ln in enumerate(lines):
                if a in ln:
                    ctx = " ".join(lines[max(0, i - 6):i + 3]).lower()
                    if any(h in ctx for h in OTHER_CHAIN_HINTS):
                        near = True
                        break
            if near:
                continue
            code = rpc("eth_getCode", [a, "latest"])
            if code is None:
                add("LOW", "address-unverified", f,
                    f"could not verify {a} (RPC unavailable)")
            elif code in ("0x", "0x0"):
                add("HIGH", "address-unverified", f,
                    f"{a} has NO contract code (EOA or wrong chain)",
                    "verify the address against the protocol docs/factory")


# ── CHECK 4: swap routes reference pools that actually hold the token ───
def check_swap_routes():
    src = read("blackhole_cl_adapter.py") + read("rebalance_swap.py")
    pools = set(re.findall(r'"(0x[a-fA-F0-9]{40})"', src))
    for p in pools:
        code = rpc("eth_getCode", [p, "latest"])
        if code in ("0x", "0x0", None):
            continue
        # token0()/token1() -> does it look like a pool?
        t0 = rpc("eth_call", [{"to": p, "data": "0x0dfe1681"}, "latest"])
        if not t0:
            continue
        add("INFO", "swap-route", "blackhole_cl_adapter.py",
            f"pool {p} tokens verified; confirm any route using it holds the "
            f"INPUT token (a BLACK route must use a pool containing BLACK)")


# ── CHECK 5: values derived from config instead of chain ────────────────
def check_config_derived():
    """Flag config-derived valuation ONLY on a rail that is still live.

    The LFJ bin reader still computes `funded_usd - wallet`, but LFJ is retired
    (not in treasury_config.json), so that path is dead code and not a live
    risk. Only report it if the rail it belongs to is actually configured.
    """
    try:
        cfg = json.load(open(os.path.join(SCRIPTS, "treasury_config.json")))
        cfg_text = json.dumps(cfg).lower()
    except Exception:
        cfg_text = ""
    lfj_live = "lfj" in cfg_text

    for f in CORE:
        src = read(f)
        if "funded_usd" not in src:
            continue
        ln = src[:src.index("funded_usd")].count("\n") + 1
        # is this the retired LFJ path?
        ctx = src[max(0, src.index("funded_usd") - 3000):src.index("funded_usd")]
        if "lfj" in ctx.lower() and not lfj_live:
            add("INFO", "config-derived-value", f"{f}:{ln}",
                "retired LFJ rail still uses funded_usd arithmetic (dead code — "
                "LFJ is not in treasury_config.json)",
                "delete the LFJ reader, or ignore while the rail stays retired")
            continue
        add("MED", "config-derived-value", f"{f}:{ln}",
            "values positions from config `funded_usd` arithmetic, not chain truth",
            "value via decreaseLiquidity/balanceOf simulation")


# ── CHECK 6: copy divergence across vault/repos/profile ─────────────────
def check_copy_divergence():
    import hashlib
    for f in CORE:
        hs = {}
        for d, label in [(SCRIPTS, "profile"), (VAULT, "vault"), (REPOS, "repos")]:
            p = os.path.join(d, f)
            if os.path.exists(p):
                hs[label] = hashlib.md5(open(p, "rb").read()).hexdigest()[:8]
        if len(set(hs.values())) > 1:
            add("MED", "copy-divergence", f,
                f"copies differ: {hs}",
                "edit the VAULT then run scripts/sync-treasury-scripts.sh")


# ── CHECK 10: sync-list coverage — is every cron-run script enrolled/frozen? ──
# Bug class exposed 2026-09-11 (third instance of one class that day): a script
# the cron ring EXECUTES was missing from sync-treasury-scripts.sh SCRIPTS[].
# Because that script syncs vault -> repos + profile, an unlisted file gets no
# protection AND an out-of-band revision silently becomes authoritative.
# gta_executor.py proved it: the vault "source of truth" was 11 days stale and
# was missing the Aug-31 fresh-scan truth guard, while only the profile copy had
# it. Adding the file to the list without fixing the vault first would have
# REGRESSED the guard across both good copies.
# Rule: every script a cron executes must be (a) enrolled in SCRIPTS[], or
# (b) md5-identical in every location it exists in. "Someone remembered" is not
# a control.
def check_sync_coverage():
    import hashlib

    # 1. the protected set, parsed from the sync script itself (no duplication)
    sync = ""
    for c in ("/root/vaults/gentech/scripts/sync-treasury-scripts.sh",):
        if os.path.exists(c):
            sync = open(c).read()
            break
    if not sync:
        add("MED", "sync-coverage", "sync-treasury-scripts.sh",
            "cannot locate the sync script — coverage unverifiable",
            "check the path in check_sync_coverage()")
        return
    import re as _re
    # anchor the close on a line-start ")" — a non-greedy "\)" stops at the
    # first paren inside a comment (this check had that bug on its first run)
    m = _re.search(r"SCRIPTS=\((.*?)\n\)", sync, _re.S)
    enrolled = set(_re.findall(r"[\w.-]+\.(?:py|sh|json)", m.group(1))) if m else set()

    # 2. what the cron ring actually executes (profile jobs.json)
    # absolute: the cron ring lives in the profile regardless of which copy
    # of this audit is executing (vault / repos / profile)
    jobs_p = "/root/.hermes/profiles/gentech-treasury/cron/jobs.json"
    executed = set()
    try:
        j = json.load(open(jobs_p))
        for x in (j if isinstance(j, list) else j.get("jobs", [])):
            sc = x.get("script")
            if sc:
                executed.add(sc)
    except Exception:
        add("MED", "sync-coverage", "cron/jobs.json",
            "cannot read cron jobs.json — executed-script set unknown",
            "verify the path in check_sync_coverage()")
        return

    # 3. follow one hop: a .sh wrapper names the .py it execs
    queue = set(executed)
    seen = set()
    while queue:
        f = queue.pop()
        if f in seen:
            continue
        seen.add(f)
        p = os.path.join(SCRIPTS, f)
        if not f.endswith(".sh") or not os.path.exists(p):
            continue
        for dep in _re.findall(r"[\w.-]+\.py", open(p).read()):
            queue.add(dep)

    # 4. judge each: enrolled, or md5-identical wherever it exists
    for f in sorted(seen):
        locs = {}
        for d, label in ((SCRIPTS, "profile"), (VAULT, "vault"), (REPOS, "repos")):
            fp = os.path.join(d, f)
            if os.path.exists(fp):
                locs[label] = hashlib.md5(open(fp, "rb").read()).hexdigest()[:8]
        if f in enrolled:
            # enrolled files are covered by check_copy_divergence too; flag only
            # if it exists in one place and that place is NOT the vault
            if len(locs) == 1 and "vault" not in locs:
                add("MED", "sync-coverage", f,
                    f"enrolled but vault copy missing (only {list(locs)})",
                    "copy it into the vault — vault is the source of truth")
            continue
        if len(locs) > 1 and len(set(locs.values())) > 1:
            add("HIGH", "sync-coverage", f,
                f"cron-executed, NOT enrolled, copies DIVERGE: {locs}",
                "promote the newest revision into the VAULT, then enroll it in "
                "sync-treasury-scripts.sh SCRIPTS[]")
        elif len(locs) == 1 and "profile" in locs:
            add("MED", "sync-coverage", f,
                "cron-executed, exists ONLY in the profile (not enrolled, no "
                "vault copy) — nothing protects it from drift",
                "move it to the vault and enroll it, or document it as "
                "profile-local")
        elif len(locs) > 1 and len(set(locs.values())) == 1:
            add("LOW", "sync-coverage", f,
                f"cron-executed and md5-identical, but not enrolled: {locs}",
                "enroll in sync-treasury-scripts.sh SCRIPTS[] so it is enforced")


# ── CHECK 7: reads a balance where it means "claimable/accrued" ─────────
def check_balance_vs_claimable():
    src = read("blackhole_cl_adapter.py")
    if "collectRewards" in src and "claimable" not in src:
        add("HIGH", "balance-vs-claimable", "blackhole_cl_adapter.py",
            "checks a token BALANCE where it means CLAIMABLE rewards",
            "simulate collectRewards (balance is 0 until a collect runs)")


# ── CHECK 8: API response shape assumptions ─────────────────────────────
def check_api_shape():
    src = read("vfat_blackhole.py")
    if src and "data.items" in src and 'data.get("items"' not in src:
        add("HIGH", "api-shape", "vfat_blackhole.py",
            "reads `data.items` only; vfat moved items to top level",
            'items = data.get("items", data.get("data", {}).get("items", []))')




# ── CHECK 9: standing token approvals (the ether.fi/Veda attack class) ──
# An approval is a persistent grant: any contract you ever approved can pull
# that token until you revoke it. The Sep 11 ExVul alert (ether.fi Liquid,
# ~15.45 ETH via the Veda AtomicQueue) drained users who had "simply approved"
# a contract. A retired rail with a live UNLIMITED approval is exactly that.
RPC = RPC  # reuse

# Spenders the treasury STILL uses. Anything else holding an allowance is stale.
LIVE_SPENDERS = {
    # our NFPM (position manager) — needs allowance to move pool tokens
    "0x3fed017ec0f5517cdf2e8a9a4156c64d74252146",
}
TOKENS = {
    "USDC":  ("0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E", 6),
    "WAVAX": ("0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", 18),
    "BLACK": ("0xcd94a87696FAC69EdAE3a70fE5725307Ae1c43f6", 18),
}
WALLET = _sw_wallet()


def check_approvals():
    """Flag live approvals — especially unlimited ones to unused contracts."""
    for name, (tok, dec) in TOKENS.items():
        # find every spender that ever received an Approval from us
        topic = "0x" + __import__("web3").Web3.keccak(
            text="Approval(address,address,uint256)").hex()
        owner_topic = "0x" + "0" * 24 + WALLET[2:].lower()
        head = rpc("eth_blockNumber", [])
        if not head:
            continue
        head = int(head, 16)
        spenders = set()
        b = head - 500000
        while b <= head:
            e = min(b + 1999, head)
            r = rpc("eth_getLogs", [{"fromBlock": hex(b), "toBlock": hex(e),
                                     "address": tok,
                                     "topics": [topic, owner_topic]}])
            for l in (r or []):
                spenders.add("0x" + l["topics"][2][-40:])
            b = e + 1
        for sp in spenders:
            data = "0xdd62ed3e" + WALLET[2:].rjust(64, "0") + sp[2:].rjust(64, "0")
            res = rpc("eth_call", [{"to": tok, "data": data}, "latest"])
            if not res or res == "0x":
                continue
            v = int(res, 16)
            if v == 0:
                continue
            unlimited = v > 2 ** 200
            stale = sp.lower() not in LIVE_SPENDERS
            code = rpc("eth_getCode", [sp, "latest"])
            dead = code in ("0x", "0x0")
            if unlimited and stale:
                add("HIGH", "stale-approval", f"{name} -> {sp}",
                    f"UNLIMITED allowance to a contract we no longer use"
                    + ("" if not dead else " (and it has NO code)"),
                    "revoke: approve(spender, 0) — an approval is a standing grant")
            elif unlimited:
                add("LOW", "wide-approval", f"{name} -> {sp}",
                    "unlimited allowance to a live spender (acceptable, but wide)",
                    "consider a bounded allowance instead of MaxUint256")
            elif stale:
                add("MED", "stale-approval", f"{name} -> {sp}",
                    f"live allowance ({v/10**dec:.6f}) to a contract we no longer use",
                    "revoke: approve(spender, 0)")




# ── CHECK 10: security-sentinel exposure drift ──────────────────────────
# The sentinel only reports incidents matching OUR_PROTOCOLS / OUR_CHAINS.
# If the treasury moves rails and that list is not updated, the sentinel keeps
# running, keeps reporting "ok", and silently stops covering us. Same class as
# every other bug found on Sep 11: a component that stops looking in the right
# place without failing.

# Words that appear throughout the sentinel for unrelated reasons (token names,
# pool types). Matching on these produced the false-negative bug.
GENERIC_TOKENS = {"wavax", "usdc", "usdt", "black", "token", "pool", "position",
                  "avalanche", "avax", "chain", "vault", "steak", "farm"}


def check_sentinel_drift():
    try:
        cfg = json.load(open(os.path.join(SCRIPTS, "treasury_config.json")))
    except Exception as e:
        add("LOW", "sentinel-drift", "treasury_config.json",
            f"could not read config to cross-check the sentinel ({e})")
        return

    # collect every protocol/type named in the live config
    live = set()
    for _chain, pools in (cfg.get("pools") or {}).items():
        for p in (pools or []):
            for k in ("name", "type", "protocol", "dex"):
                v = str(p.get(k) or "").lower()
                if v:
                    live.add(v)
    if not live:
        return

    # pull the sentinel's declared coverage
    try:
        src = read("security_sentinel.py")
    except Exception:
        add("MED", "sentinel-drift", "security_sentinel.py",
            "sentinel script missing — the attack monitor cannot run",
            "restore security_sentinel.py")
        return

    # IMPORTANT: scope the search to the OUR_PROTOCOLS block ONLY. Searching
    # the whole file produced a check that could not fail — a rail's other name
    # tokens (wavax, usdc) appear elsewhere in the file as addresses/comments,
    # so deleting the protocol from the coverage list still matched.
    m = re.search(r"OUR_PROTOCOLS\s*=\s*\{(.*?)\n\}", src, re.S)
    if not m:
        add("MED", "sentinel-drift", "security_sentinel.py",
            "could not locate OUR_PROTOCOLS in the sentinel — coverage cannot "
            "be verified",
            "restore the OUR_PROTOCOLS dict")
        return
    declared = m.group(1).lower()
    # also accept a protocol named in the EXPOSED_TECHNIQUES mapping
    mt = re.search(r"EXPOSED_TECHNIQUES\s*=\s*\{(.*?)\n\}", src, re.S)
    if mt:
        declared += " " + mt.group(1).lower()

    for name in sorted(live):
        # a config rail is covered if a MEANINGFUL, NON-GENERIC token of its
        # name appears in the coverage list itself
        toks = [t for t in re.split(r"[^a-z0-9]+", name) if len(t) > 3]
        toks = [t for t in toks if t not in GENERIC_TOKENS]
        if not toks:
            continue
        if not any(t in declared for t in toks):
            add("MED", "sentinel-drift", "security_sentinel.py",
                f"live rail '{name}' is NOT in the sentinel's coverage list "
                f"(OUR_PROTOCOLS) — attacks on it would be missed silently",
                "add the protocol to OUR_PROTOCOLS in security_sentinel.py")

    # the sentinel must actually be scheduled, or coverage is theoretical
    try:
        jobs = json.load(open(os.path.expanduser(
            "~/.hermes/profiles/gentech-treasury/cron/jobs.json")))
    except Exception:
        jobs = None
    if jobs is not None:
        jl = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
        sent = [j for j in jl if "sentinel" in str(j.get("name", "")).lower()]
        if not sent:
            add("MED", "sentinel-drift", "cron/jobs.json",
                "security sentinel is not scheduled — no attack monitoring runs",
                "re-create the Security Sentinel cron")
        elif not any(j.get("enabled") for j in sent):
            add("HIGH", "sentinel-drift", "cron/jobs.json",
                "security sentinel cron EXISTS BUT IS DISABLED — monitoring is off",
                "resume the Security Sentinel cron")



def check_identity_hardcoding(SRC_DIR):
    """CHECK 11 — a script able to SIGN must not hardcode who it signs FOR.

    A literal wallet (or a direct key-path read) in a signer means a second
    operator running that file would act on the FIRST operator's treasury.
    That is the "funds moved to the wrong place" class, so it is a finding
    even though the script works perfectly for its original author.
    """
    import pathlib as _pl
    import re as _re
    findings = []
    skip = {"steward_identity.py", "migrate_identity.py",
            "add_identity_check.py", "treasury_self_audit.py"}
    for p in sorted(_pl.Path(SRC_DIR).glob("*.py")):
        if p.name in skip or ".bak" in p.name:
            continue
        try:
            src = p.read_text()
        except Exception:
            continue
        if not any(h in src for h in ("sign_transaction", "send_raw_transaction",
                                      "from_key(")):
            continue                       # cannot sign -> out of scope
        if "steward_identity" in src:
            continue                       # resolves identity properly
        # A key sourced from a NAMED env var is a legitimate multi-chain
        # operator (e.g. Hyperliquid, Solana) — the risk we care about is
        # HARDCODED identity, not the absence of our EVM resolver. Being too
        # blunt here produces false positives and erodes trust in the check.
        env_sourced = _re.search(
            r"os\.environ\.get\(\s*[\"'][A-Z_]{4,}[\"']", src)
        if "/root/.blockrun/almanak-steward-key" in src:
            reason = ("reads the signing-key path directly instead of "
                      "resolving identity via steward_identity")
        elif _re.search(r"0x[a-fA-F0-9]{40}", src):
            reason = ("hardcodes a wallet address and can sign — a second "
                      "operator would sign for the first operator's treasury")
        elif env_sourced:
            continue                       # key from a named env var: fine
        else:
            reason = ("can sign but does not resolve identity via "
                      "steward_identity")
        findings.append({
            "class": "identity-hardcoding",
            "sev": "MED",
            "where": p.name,
            "msg": reason,
            "fix": "import steward_identity and use signer() / wallet()",
        })
    return findings



def main():
    check_success_before_status()
    check_index_selection()
    check_addresses()
    check_config_derived()
    check_copy_divergence()
    check_balance_vs_claimable()
    check_api_shape()
    check_swap_routes()
    check_approvals()
    check_sentinel_drift()
    check_sync_coverage()

    if "--json" in sys.argv:
        print(json.dumps({"findings": findings, "count": len(findings)}, indent=2))
        return 1 if findings else 0

    order = {"HIGH": 0, "MED": 1, "LOW": 2, "INFO": 3}
    findings.sort(key=lambda x: order.get(x["sev"], 9))
    print("🔍 TREASURY SELF-AUDIT — hunting bug CLASSES, not instances\n")
    if not findings:
        print("  ✅ clean — no findings")
        return 0
    # CHECK 11 — identity resolution (multi-tenant safety)
    try:
        findings.extend(
            check_identity_hardcoding(
                os.path.dirname(os.path.abspath(__file__))))
    except Exception:
        pass

    cur = None
    for fd in findings:
        if fd["class"] != cur:
            cur = fd["class"]
            print(f"\n── {cur} ──")
        print(f"  [{fd['sev']:4s}] {fd['where']}")
        print(f"         {fd['msg']}")
        if fd["fix"]:
            print(f"         fix: {fd['fix']}")

    print(f"\n{len(findings)} finding(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
