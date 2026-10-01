#!/usr/bin/env python3
"""
Agent Network / Rails Scanner — maps the network of agent rails.

Jordan's lens (Aug 6): instead of watching one vendor (MetaMask), scan the whole
network of agents as they launch, to understand what the network of rails looks
like and what's changing between them.

Sources:
  - 8004scan.io  (ERC-8004 agent registry) — /api/v1/agents
  - agentscan.info (agent registry)        — /api/agents

Upgrades (Aug 6, Jordan-approved):
  1. TREND TRACKING — persists a history of {date, total, x402, by_chain} snapshots
     each run; the weekly report shows the DELTA (what's changing between rails).
  2. DATA QUALITY — dedups the same agent across both sources, normalizes chain
     names (BNB Smart Chain / BNB / chain-5042002 → canonical).
  3. LEADS TAGGING — flags x402 + on-our-chains agents as 🔗 integration/partner leads.

Usage:
  python3 agent_network_scan.py            # scan, emit new agents
  python3 agent_network_scan.py --prime    # baseline (silent)
  python3 agent_network_scan.py --report    # full current-state report (always emits)
  python3 agent_network_scan.py --weekly    # top 20 + rails + trend + leads
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

STATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "watcher-state")
os.makedirs(STATE_DIR, exist_ok=True)
STATE_FILE = os.path.join(STATE_DIR, "agent-network-scan.json")

# Canonical chain names (normalize the mess of aliases across sources)
CHAIN_ALIASES = {
    "ethereum": "Ethereum", "eth": "Ethereum", "mainnet": "Ethereum",
    "bnb": "BNB", "bnb smart chain": "BNB", "bsc": "BNB", "bsc-1": "BNB",
    "base": "Base", "base-1": "Base",
    "avalanche": "Avalanche", "avax": "Avalanche",
    "solana": "Solana",
    "polygon": "Polygon", "matic": "Polygon",
    "arbitrum": "Arbitrum", "arb": "Arbitrum",
    "optimism": "Optimism", "op": "Optimism",
    "x layer": "X Layer", "xlayer": "X Layer", "x-layer": "X Layer",
    "scroll": "Scroll", "mantle": "Mantle", "celo": "Celo",
    "injective": "Injective", "monad": "Monad",
    "arc": "Arc", "arc-1": "Arc",
}
CHAIN_IDS = {
    1: "Ethereum", 56: "BNB", 8453: "Base", 43114: "Avalanche",
    137: "Polygon", 42161: "Arbitrum", 10: "Optimism", 196: "X Layer",
    534352: "Scroll", 5000: "Mantle", 1284: "Moonbeam", 42220: "Celo",
    5042002: "Arc", 2741: "Abstract", 1776: "Injective",
}
# Chains we operate on / care about for leads
OUR_CHAINS = {"Base", "Ethereum", "Avalanche", "Solana", "BNB", "Arc"}
# Known noise families (duplicate spam agents) + our own fleet
NOISE_NAMES = {"Ave.ai Trading Agent"}
# Our own deployed agents (Hermes fleet on Arc) — not external leads
OUR_FLEET_PREFIXES = ("hermes-", "gentech-", "gta-", "steward-")


def _now():
    return datetime.now(timezone.utc).strftime("%b %d · %H:%M UTC")


def _fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; GenTechLabs/1.0; +https://gentechlabs.net)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


def _load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"seen": [], "last_scan": None, "history": []}


def _save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def _canon_chain(raw):
    """Normalize a chain name/id to a canonical label."""
    if isinstance(raw, int):
        return CHAIN_IDS.get(raw, f"chain-{raw}")
    key = str(raw).strip().lower()
    return CHAIN_ALIASES.get(key, str(raw).strip() or "?")


def scan_8004scan():
    out = []
    try:
        data = _fetch("https://8004scan.io/api/v1/agents?limit=100")
        for a in data.get("items", []):
            out.append({
                "source": "8004scan",
                "id": a.get("agent_id") or a.get("id"),
                "name": a.get("name", "?"),
                "chain": _canon_chain(a.get("chain_id")),
                "x402": bool(a.get("x402_supported")),
                "protocols": a.get("supported_protocols") or [],
                "desc": (a.get("description") or "")[:80],
                "created": a.get("created_at", ""),
            })
    except Exception as e:
        print(f"⚠️ 8004scan: {e}", file=sys.stderr)
    return out


def scan_agentscan():
    out = []
    try:
        data = _fetch("https://agentscan.info/api/agents?page=1&page_size=100")
        for a in data.get("items", []):
            out.append({
                "source": "agentscan",
                "id": a.get("id") or a.get("address"),
                "name": a.get("name", "?"),
                "chain": _canon_chain(a.get("network_name")),
                "x402": False,  # agentscan doesn't expose x402 directly
                "protocols": (a.get("skills") or []) + (a.get("domains") or []),
                "desc": (a.get("description") or "")[:80],
                "created": a.get("created_at", ""),
            })
    except Exception as e:
        print(f"⚠️ agentscan: {e}", file=sys.stderr)
    return out


def _dedup(agents):
    """Dedup the same agent across both sources by (name, chain)."""
    seen = {}
    for a in agents:
        key = (a["name"].lower(), a["chain"])
        if key in seen:
            # merge: prefer the record with more info (x402, protocols)
            cur = seen[key]
            if a["x402"] and not cur["x402"]:
                cur["x402"] = True
            if a["protocols"] and not cur["protocols"]:
                cur["protocols"] = a["protocols"]
            if not cur["desc"] and a["desc"]:
                cur["desc"] = a["desc"]
        else:
            seen[key] = a
    return list(seen.values())


def _is_lead(a):
    """A lead = x402-supported AND on a chain we operate on."""
    return a["x402"] and a["chain"] in OUR_CHAINS


def _score(a):
    s = 0
    if a["x402"]: s += 3
    if a["protocols"]: s += 2
    if a["name"] and not a["name"].startswith(("Agent #", "smoke-")): s += 1
    if a["chain"] in OUR_CHAINS: s += 1
    return s


def main():
    prime = "--prime" in sys.argv
    full_report = "--report" in sys.argv
    weekly = "--weekly" in sys.argv

    state = _load_state()
    seen = set(state.get("seen", []))

    all_agents = _dedup(scan_8004scan() + scan_agentscan())

    # Aggregate current-state stats
    by_chain = {}
    x402_count = 0
    leads = []
    for a in all_agents:
        by_chain[a["chain"]] = by_chain.get(a["chain"], 0) + 1
        if a["x402"]:
            x402_count += 1
        if _is_lead(a):
            leads.append(a)

    # New agents since last run
    new = [a for a in all_agents if _dedup_key(a) not in seen]
    for a in new:
        seen.add(_dedup_key(a))
    state["seen"] = list(seen)[-2000:]

    # TREND: persist a snapshot each run (bounded history, keep last 12)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    history = state.get("history", [])
    if not history or history[-1].get("date") != today:
        history.append({
            "date": today,
            "total": len(all_agents),
            "x402": x402_count,
            "by_chain": by_chain,
        })
        history = history[-12:]
    state["history"] = history
    state["last_scan"] = _now()
    _save_state(state)

    if prime:
        return  # baseline, silent

    if weekly:
        lines = ["🏆 AGENT NETWORK — TOP 20 + RAILS + TREND", f"   {_now()}", ""]
        lines.append(f"Total agents: {len(all_agents)} | x402: {x402_count} "
                     f"({x402_count/len(all_agents)*100:.0f}%) | chains: {len(by_chain)}")
        lines.append("")

        # TREND: delta vs previous snapshot
        if len(history) >= 2:
            prev = history[-2]
            d_total = len(all_agents) - prev.get("total", len(all_agents))
            d_x402 = x402_count - prev.get("x402", x402_count)
            lines.append("📈 Trend vs last scan:")
            lines.append(f"  Agents: {d_total:+d} | x402: {d_x402:+d}")
            # chain deltas
            prev_chains = prev.get("by_chain", {})
            chain_deltas = []
            for c, n in by_chain.items():
                d = n - prev_chains.get(c, 0)
                if d != 0:
                    chain_deltas.append(f"{c}{d:+d}")
            if chain_deltas:
                lines.append("  Chain deltas: " + ", ".join(chain_deltas[:8]))
            lines.append("")

        # TOP 20 — drop noise + our own fleet
        clean = [a for a in all_agents
                 if a["name"] not in NOISE_NAMES
                 and not a["name"].lower().startswith(OUR_FLEET_PREFIXES)]
        ranked = sorted(clean, key=_score, reverse=True)[:20]
        for i, a in enumerate(ranked, 1):
            x = "🔑" if a["x402"] else " "
            protos = ", ".join(a["protocols"][:4]) if a["protocols"] else "—"
            lines.append(f"{i}. {a['name']} · {a['chain']} {x} · {protos}")
        lines.append("")

        # LEADS — external only (drop our own fleet)
        ext_leads = [a for a in leads
                     if not a["name"].lower().startswith(OUR_FLEET_PREFIXES)]
        if ext_leads:
            lines.append(f"🔗 LEADS ({len(ext_leads)} x402 + on our chains):")
            for a in sorted(ext_leads, key=_score, reverse=True)[:8]:
                lines.append(f"  • {a['name']} · {a['chain']}")
            lines.append("")

        lines.append("Lens: x402 = our payment standard. Watch chain + protocol")
        lines.append("distribution + x402 adoption to see the network shift.")
        print("\n".join(lines))
        return

    if full_report:
        lines = ["🌐 AGENT NETWORK / RAILS — CURRENT STATE", f"   {_now()}", ""]
        lines.append(f"Total agents tracked: {len(all_agents)}")
        lines.append(f"x402-supported: {x402_count}")
        lines.append("")
        lines.append("Agents by chain:")
        for chain, cnt in sorted(by_chain.items(), key=lambda x: -x[1]):
            lines.append(f"  {chain:15s} {cnt}")
        lines.append("")
        lines.append("New since last scan:")
        if new:
            for a in new[:15]:
                x = "🔑x402" if a["x402"] else "     "
                lines.append(f"  {x} {a['name'][:30]:30s} {a['chain']}")
        else:
            lines.append("  (none)")
        print("\n".join(lines))
        return

    # Default: emit only new agents
    if not new:
        return  # silent

    lines = ["🌐 AGENT NETWORK / RAILS — NEW AGENTS", f"   {_now()}", ""]
    lines.append(f"{len(new)} new agent(s) since last scan:")
    lines.append("")
    for a in new[:20]:
        x = "🔑x402" if a["x402"] else "     "
        lines.append(f"  {x} {a['name'][:35]:35s} | {a['chain']}")
        if a["desc"]:
            lines.append(f"        {a['desc']}")
    lines.append("")
    lines.append("Lens: which rails are agents adopting? x402 = our payment standard.")
    lines.append("Track chain distribution + x402 adoption to see the network shift.")
    print("\n".join(lines))


def _dedup_key(rec):
    return f"{rec['source']}:{rec['id']}"


if __name__ == "__main__":
    main()
