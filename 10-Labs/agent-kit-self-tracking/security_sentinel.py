#!/usr/bin/env python3
"""SECURITY SENTINEL — watches the space for attacks relevant to OUR treasury.

Jordan Sep 11 2026: "a cron job specifically supposed to look out for new
attacks out in the space... anytime it's relevant to us, it helps us find ways
of finding how it happened and upgrading our treasury. We need some type of
security layer that is also a part of self-healing."

Design principle: RELEVANCE, not news. A generic "hack feed" is noise. This
matches each incident against our ACTUAL exposure surface and only speaks when
something plausibly touches us.

Sources:
  - DefiLlama /hacks        (structured: chain, classification, technique, amount)
  - SlowMist Medium RSS      (deep technical post-mortems)

Silence doctrine: fingerprint the matched set; speak only when a NEW relevant
incident appears (or a known one escalates). Exit 0, empty stdout = silent.

Usage:  python3 security_sentinel.py [--json] [--all] [--days N]
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     ".security-sentinel-state.json")

# ── OUR EXPOSURE SURFACE ────────────────────────────────────────────────
# Everything here is derived from what the treasury ACTUALLY holds/uses.
# Update this when the treasury moves rails (it is the relevance filter).
OUR_CHAINS = {"avalanche", "avax", "bsc", "base", "ethereum", "solana", "arbitrum"}

# Primary chain: incidents here matter most.
PRIMARY_CHAIN = "avalanche"

# Protocols we actually depend on. An exploit here is an immediate alert.
OUR_PROTOCOLS = {
    "blackhole": "our live LP venue",
    "algebra": "the AMM math our CL position uses",
    "trader joe": "the rail we migrated OFF (still holds approvals)",
    "lfj": "the rail we migrated OFF (still holds approvals)",
    "aave": "lending rail in our config",
    "aerodrome": "Base rail in our roadmap",
    "meteora": "Solana rail in our roadmap",
    "veda": "the Sep 11 approval-exploit venue (approval class)",
    "ether.fi": "the Sep 11 approval-exploit venue (approval class)",
    "curve": "common LP venue",
    "pancakeswap": "common LP venue",
    "uniswap": "the AMM family our fee math is built on",
}

# Attack CLASSES we are structurally exposed to. This is the important part:
# even if the specific protocol is unknown to us, the TECHNIQUE may apply.
# Each maps to how it would bite US.
EXPOSED_TECHNIQUES = {
    "arbitrary external call": (
        "HIGH", "a contract we call can invoke arbitrary targets — audit every "
        "spender/router we approve"),
    "access control": (
        "HIGH", "permissioning bug — check we never grant control of our "
        "positions to a third party"),
    "improper access control": ("HIGH", "as above"),
    "approval": (
        "HIGH", "the ether.fi class — we hold live approvals; run the "
        "stale-approval audit check"),
    "private key compromised": (
        "HIGH", "key hygiene — our steward key signs autonomously; review "
        "key storage and blast radius"),
    "key compromise": ("HIGH", "as above"),
    "spot price manipulation": (
        "MED", "oracle/spot manipulation — affects our in-range fee "
        "assumptions and any price-gated logic"),
    "oracle manipulation": ("MED", "as above"),
    "flashloan": (
        "MED", "flash-loan-assisted — check any logic that trusts a "
        "spot balance within one tx"),
    "flash loan": ("MED", "as above"),
    "price manipulation": ("MED", "as above"),
    "reentrancy": (
        "MED", "reentrancy — relevant to any custom contract we deploy"),
    "rounding error": (
        "MED", "accounting precision — we compute liquidity/fee math; "
        "validate against chain (our collect()/decreaseLiquidity sims)"),
    "token & share accounting": ("MED", "as above"),
    "unbacked cross-chain mint": (
        "MED", "bridge class — relevant if we ever move capital across rails"),
    "bridge": ("MED", "as above"),
    "signature": (
        "MED", "signature validation — relevant if we adopt permit/sig-based "
        "approvals"),
    "logic": ("LOW", "generic logic bug — review for a similar pattern"),
}


def fetch(url, timeout=30, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return urllib.request.urlopen(req, timeout=timeout).read().decode(
                "utf-8", "replace")
        except Exception:
            if a == tries - 1:
                return None
            time.sleep(1.5)
    return None


def fetch_hacks(days=21):
    """DefiLlama hack feed — structured incidents."""
    raw = fetch("https://api.llama.fi/hacks")
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    cutoff = time.time() - days * 86400
    out = []
    for h in data:
        ts = h.get("date") or 0
        if ts < cutoff:
            continue
        chains = h.get("chain")
        if isinstance(chains, str):
            chains = [chains]
        out.append({
            "src": "defillama",
            "date": ts,
            "name": str(h.get("name") or "?"),
            "chains": [str(c).lower() for c in (chains or [])],
            "classification": str(h.get("classification") or ""),
            "technique": str(h.get("technique") or ""),
            "amount": h.get("amount") or 0,
            "target": str(h.get("targetType") or ""),
            "url": h.get("source") or "",
        })
    return out


def fetch_slowmist(limit=12):
    """SlowMist Medium RSS — deep post-mortems."""
    raw = fetch("https://slowmist.medium.com/feed")
    if not raw:
        return []
    out = []
    items = re.findall(r"<item>(.*?)</item>", raw, re.S)
    for it in items[:limit]:
        t = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", it, re.S)
        d = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S)
        l = re.search(r"<link>(.*?)</link>", it, re.S)
        desc = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>",
                         it, re.S)
        title = (t.group(1) if t else "").strip()
        ts = 0
        if d:
            try:
                ts = datetime.strptime(d.group(1).strip(),
                                       "%a, %d %b %Y %H:%M:%S %Z").replace(
                    tzinfo=timezone.utc).timestamp()
            except Exception:
                ts = 0
        body = (desc.group(1) if desc else "")[:2500]
        out.append({
            "src": "slowmist",
            "date": ts,
            "name": title[:150],
            "chains": [],
            "classification": "",
            "technique": "",
            "amount": 0,
            "target": "",
            "url": (l.group(1) if l else "").strip(),
            "body": body,
        })
    return out


def relevance(item):
    """Return (score, reasons). Score 0 = not relevant, silence."""
    reasons = []
    score = 0
    name = (item["name"] + " " + item.get("body", "")).lower()
    tech = (item["technique"] + " " + item["classification"] + " "
            + item.get("body", "")).lower()
    chains = [c.lower() for c in item["chains"]]

    # 0. RSS/deep-dive items carry no structured fields — mine the body for
    # chain names so a post-mortem on OUR chain still surfaces.
    if not chains:
        if "avalanche" in name or "avax" in name:
            chains.append("avalanche")
        for c in OUR_CHAINS:
            if c in name and c not in ("avax",):
                chains.append(c)

    # 1. our chain?
    if any(c in ("avalanche", "avax") for c in chains):
        score += 60
        reasons.append("on OUR chain (Avalanche)")
    elif chains and any(c in OUR_CHAINS for c in chains):
        score += 15
        reasons.append(f"on a chain we touch ({', '.join(chains[:3])})")

    # 2. a protocol we depend on?
    for proto, why in OUR_PROTOCOLS.items():
        if proto in name:
            score += 80 if proto in ("blackhole", "algebra", "trader joe", "lfj") else 45
            reasons.append(f"touches {proto} — {why}")
            break

    # 3. a technique we are exposed to?
    for tkey, (sev, why) in EXPOSED_TECHNIQUES.items():
        if tkey in tech or tkey in name:
            score += {"HIGH": 40, "MED": 20, "LOW": 8}[sev]
            reasons.append(f"[{sev}] technique applies to us: {why}")
            break

    # 4. a WALLET/KEY or APPROVAL incident is always ours to study: we run an
    # autonomous signing wallet holding live approvals.
    wallet_hit = any(k in name for k in (
        "wallet", "private key", "seed phrase", "approval", "allowance",
        "phishing", "signature", "permit", "drainer"))
    if wallet_hit:
        score += 35
        reasons.append("wallet/approval class — directly on our operating model")

    # 5. generic exploit write-ups from a threat-intel source: worth a look,
    # but only if it is a real incident analysis.
    if item["src"] == "slowmist" and any(
            k in name for k in ("hack", "exploit", "vulnerabilit", "theft",
                                "attack", "incident", "stolen", "drain")):
        score += 12
        reasons.append("threat-intel post-mortem (study the technique)")

    # 6. material size (big incidents get studied and copied)
    if item["amount"] >= 10_000_000:
        score += 12
        reasons.append("very large incident (>$10M) — patterns get copied")

    return score, reasons


def main():
    days = 21
    if "--days" in sys.argv:
        days = int(sys.argv[sys.argv.index("--days") + 1])
    show_all = "--all" in sys.argv

    items = fetch_hacks(days) + fetch_slowmist()

    scored = []
    for it in items:
        sc, rs = relevance(it)
        if sc > 0:
            it["score"], it["reasons"] = sc, rs
            scored.append(it)
    scored.sort(key=lambda x: (-x["score"], -x["date"]))

    # fingerprint: new/changed relevant incidents
    sig_map = {f"{i['src']}:{i['name'][:60]}": i["score"] for i in scored}
    prev = {}
    if os.path.exists(STATE):
        try:
            prev = json.load(open(STATE))
        except Exception:
            prev = {}
    new_items = [i for i in scored
                 if sig_map.get(f"{i['src']}:{i['name'][:60]}", 0) > 0
                 and f"{i['src']}:{i['name'][:60]}" not in (prev.get("seen") or {})]

    if "--json" in sys.argv:
        print(json.dumps({
            "scanned": len(items),
            "relevant": len(scored),
            "new": len(new_items),
            "items": [{k: v for k, v in i.items() if k != "body"} for i in scored[:15]],
        }, indent=2))
        json.dump({"seen": sig_map, "ts": time.time()}, open(STATE, "w"))
        return 0

    json.dump({"seen": sig_map, "ts": time.time()}, open(STATE, "w"))

    if not new_items and not show_all:
        return 0   # SILENT — silhouette doctrine

    print("🛡️  SECURITY SENTINEL — incidents relevant to OUR treasury\n")
    for i in new_items if not show_all else scored[:10]:
        dt = (datetime.fromtimestamp(i["date"], tz=timezone.utc).strftime("%Y-%m-%d")
              if i["date"] else "?")
        tag = "NEW " if i in new_items else "    "
        print(f"  {tag}[{dt}] {i['name'][:80]}")
        if i["amount"]:
            print(f"        ${i['amount']:,.0f} · {i['classification']}"
                  f" · {i['technique']}")
        for r in i["reasons"]:
            print(f"        → {r}")
        if i["url"]:
            print(f"        {i['url']}")
        print()
    if new_items:
        print(f"{len(new_items)} new relevant incident(s). "
              f"Review each against our exposure and add an audit check if it "
              f"maps to a bug class we could hit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
