#!/usr/bin/env python3
"""data-provenance-audit.py — name the source of every number that drives a treasury decision.

Jordan (2026-09-18): "we've had this issue before about where we're getting our data from and our
choosing stuff. on chain data is king always king."

That is the doctrine. This makes it enforceable rather than aspirational.

THE HIERARCHY
  CHAIN       eth_call / eth_getLogs against a contract. Definitive. Cannot be argued with.
  AGGREGATOR  DefiLlama, CMC, CoinGecko, DexScreener. Useful for DISCOVERY, never for a decision
              until it has been reproduced on-chain.
  CONFIG      hardcoded constants, cached JSON, hand-written notes. Fine as a label, dangerous as
              a fact — and the one that silently outranks everything else.

WHY THIS EXISTS — four failures in a single week, every one the same shape:
  1. DefiLlama said LFJ pays 90.7%. The pair's own fee parameters said 0.0518% take -> ~78% net
     after the 10% protocol share. The aggregator was never wrong out loud; it was just unused.
  2. Four WAVAX/USDC pools exist. THREE are empty and quote $10.15 / $29.12 / $34.85 against a real
     market of $7.96. They answer every call normally. Nothing about them looks broken.
  3. steward-buylist-overrides.json silently outranked the list we had just edited.
  4. A successful transfer read back as zero movement for several seconds (RPC lag).

Every one is a mechanism reporting success while doing nothing. The defense is not care — it is
naming the source, in the artifact, at the moment the number is used.

READ-ONLY: scans files, calls nothing, changes nothing.
"""
from __future__ import annotations

import os
import re
import sys
from collections import defaultdict

SCRIPTS_DIRS = [
    "/root/vaults/gentech/10-Labs/agent-kit-self-tracking",
    "/root/vaults/gentech/06-Content/Skills/scripts",
]

# ── how each kind of source is recognised ──────────────────────────────────
PATTERNS = [
    ("CHAIN",      r"\b(eth_call|eth_getLogs|eth_getCode|eth_getBalance|eth_getTransaction|"
                   r"w3\.eth\.|contract\.functions\.|\.call\(\)|send_raw_transaction|"
                   r"wait_for_transaction_receipt)\b"),
    ("AGGREGATOR", r"\b(yields\.llama\.fi|api\.llama\.fi|coins\.llama\.fi|pro-api\.coinmarketcap|"
                   r"api\.coingecko|api\.dexscreener|api\.exchange\.coinbase|api\.kraken|"
                   r"api\.snowtrace|api\.cftc|federalreserve)\b"),
    ("CONFIG",     r"\b(open\(.*\.json|json\.load\(|_STATE_FILE|STATE_FILE|OVERRIDES_FILE|"
                   r"CACHE|load_state|\bCACHED\b)"),
]

CONFIG_PATH_HINT = r'["\']([^"\']*\.json)["\']'


def strip_prose(src: str) -> str:
    """Remove comments and docstrings before scanning for values.

    The first version scanned raw source and reported three "stale constants" that were all PROSE:
    a comment explaining the bug, a docstring describing the old value, and a yield line that
    correctly warns "Coinbase 3.5% is UNVERIFIED by us". A checker that fires on the text describing
    a fixed bug is the same failure as a checker that cannot recognise a pass — and this audit exists
    precisely to catch that family. So strip prose first, then scan only executable code.
    """
    # triple-quoted blocks (docstrings)
    src = re.sub(r'"""(?:.|\n)*?"""', "", src)
    src = re.sub(r"'''(?:.|\n)*?'''", "", src)
    # line comments, but not a # inside a string literal on that line
    out = []
    for line in src.split("\n"):
        in_s = None
        cut = len(line)
        for i, ch in enumerate(line):
            if in_s:
                if ch == in_s and line[i - 1] != "\\":
                    in_s = None
            elif ch in "\"'":
                in_s = ch
            elif ch == "#":
                cut = i
                break
        out.append(line[:cut])
    return "\n".join(out)


def scan(path: str):
    try:
        raw = open(path, encoding="utf-8", errors="replace").read()
    except Exception:
        return None
    src = strip_prose(raw) if path.endswith(".py") else re.sub(r"^\s*#.*$", "", raw, flags=re.M)
    counts = defaultdict(int)
    for label, pat in PATTERNS:
        counts[label] = len(re.findall(pat, src))
    cfg_files = sorted(set(re.findall(CONFIG_PATH_HINT, src)))
    return counts, cfg_files, len(raw.splitlines())


def main() -> int:
    targets = []
    for d in SCRIPTS_DIRS:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith((".py", ".sh")) and not f.startswith("_"):
                targets.append(os.path.join(d, f))

    print("=" * 104)
    print("  DATA PROVENANCE AUDIT — where does every treasury number actually come from?")
    print("=" * 104)
    print("  CHAIN      = eth_call / event logs. definitive.")
    print("  AGGREGATOR = DefiLlama / CMC / exchanges. discovery only — must be reproduced on-chain.")
    print("  CONFIG     = cached JSON / constants / hand notes. a label, never a fact.")
    print()

    rows = []
    for t in targets:
        r = scan(t)
        if r is None:
            continue
        counts, cfg_files, nlines = r
        rows.append((os.path.basename(t), counts, cfg_files, nlines))

    rows.sort(key=lambda x: (-x[1]["CHAIN"], x[0]))

    print(f"  {'script':<34}{'CHAIN':>7}{'AGG':>6}{'CONF':>6}   verdict")
    print("  " + "-" * 100)
    pure_config, chain_led, agg_only = [], [], []
    for name, c, cfg, n in rows:
        if c["CHAIN"] == 0 and c["AGGREGATOR"] == 0 and c["CONFIG"] > 0:
            v = "⚠️  CONFIG ONLY — no chain read and no live fetch"
            pure_config.append(name)
        elif c["CHAIN"] > 0 and c["AGGREGATOR"] == 0:
            v = "✅ CHAIN-LED"
            chain_led.append(name)
        elif c["CHAIN"] > 0 and c["AGGREGATOR"] > 0:
            v = "🟡 chain + aggregator (check it cross-checks)"
            chain_led.append(name)
        elif c["AGGREGATOR"] > 0:
            v = "🔵 AGGREGATOR ONLY"
            agg_only.append(name)
        else:
            v = "— no external source"
        print(f"  {name[:32]:<34}{c['CHAIN']:>7}{c['AGGREGATOR']:>6}{c['CONFIG']:>6}   {v}")

    print("\n" + "=" * 104)
    print("  SUMMARY")
    print("=" * 104)
    print(f"  scripts scanned          : {len(rows)}")
    print(f"  ✅ chain-led              : {len(chain_led)}")
    print(f"  🔵 aggregator-only        : {len(agg_only)}")
    print(f"  ⚠️  config-only            : {len(pure_config)}")
    if agg_only:
        print("\n  AGGREGATOR-ONLY SCRIPTS — these report numbers we have NOT reproduced on-chain:")
        for n in agg_only:
            print(f"     • {n}")
        print("     Not a defect by itself (discovery is an aggregator's job). A defect only if a")
        print("     DECISION is taken on the number before it is confirmed against a contract.")
    if pure_config:
        print("\n  CONFIG-ONLY SCRIPTS — highest risk: the number cannot have updated itself:")
        for n in pure_config:
            print(f"     • {n}")

    # the specific constants that have historically drifted — scanned against CODE ONLY, never prose
    print("\n  " + "-" * 100)
    print("  STALE-CONSTANT SPOT CHECK (values we have personally watched go out of date)")
    print("  scanning executable code only — a comment describing a fixed bug is not a live bug")
    known = {
        "steward-buylist.py": ["216% APR", "27% fee core", "Coinbase 3.5%"],
        "steward-buylist-overrides.json": ["216% APR", "27% fee core"],
        "steward_progress.py": ["currentDailyFees", "0.072"],
    }
    # A stale value can survive in live code LEGITIMATELY — inside a warning that names it as stale.
    # "Coinbase 3.5% is custodial and UNVERIFIED by us" is a correct string that happens to contain a
    # known-stale token. Firing on it forever teaches everyone to ignore the flag, and a flag nobody
    # reads is worse than no flag. So: if the token sits near a negation, downgrade it to a reference.
    NEGATIONS = ("unverified", "no measured", "superseded", "do not count", "deprecated",
                 "stale", "not counted", "emissions", "confirmed dead", "replaces the old")
    WINDOW = 120

    for d in SCRIPTS_DIRS:
        for fname, needles in known.items():
            path = os.path.join(d, fname)
            if not os.path.isfile(path):
                continue
            raw = open(path, encoding="utf-8", errors="replace").read()
            code = strip_prose(raw) if fname.endswith(".py") else raw
            asserted, referenced = [], []
            for n in needles:
                if n not in code:
                    continue
                idx = code.find(n)
                ctx = code[max(0, idx - WINDOW): idx + len(n) + WINDOW].lower()
                (referenced if any(neg in ctx for neg in NEGATIONS) else asserted).append(n)
            if asserted:
                print(f"     ⚠️  {fname}: LIVE CODE ASSERTS {asserted}")
            elif referenced:
                print(f"     ✅ {fname}: {referenced} appear in live code only inside a WARNING "
                      f"that names them as stale")
            else:
                prose_only = [n for n in needles if n in raw]
                if prose_only:
                    print(f"     ✅ {fname}: {prose_only} appear in COMMENTS/docstrings only — not live")
                else:
                    print(f"     ✅ {fname}: none of the known-stale strings present")

    print("\n" + "=" * 104)
    print("  DOCTRINE: on-chain data is king. Name the source of any number that drives a decision.")
    print("=" * 104)
    return 0


if __name__ == "__main__":
    sys.exit(main())
