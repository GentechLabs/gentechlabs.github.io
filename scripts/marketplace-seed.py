#!/usr/bin/env python3
"""GenTech — Marketplace Seed / Registry Parser.

Parses `11-Mess Hall/marketplace-listings-registry.md` into machine-readable
JSON so the Agent Marketplace Income Scanner (cron 38eda06b0a11) can:

  1. DEDUPE — never re-report a marketplace where GenTech is already listed.
  2. SCOPED HUNT — only pursue NEW platforms not already in the registry.
  3. ANCHOR — for each candidate, output the "why be here" + known gaps.

Output: JSON to stdout (no_agent-friendly). Exit 0 always.
"""
import json, re, sys
from pathlib import Path

VAULT = Path("/root/vaults/gentech")
REGISTRY = VAULT / "11-Mess Hall" / "marketplace-listings-registry.md"


def _extract_names_from_table(text: str) -> list[str]:
    """Pull platform names out of markdown table rows (the 'Platform' column)."""
    names = []
    for line in text.splitlines():
        # table row: | N | Platform | URL | ... |
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        name = cells[1]
        # skip header / separator rows
        if not name or name.startswith("---") or name.lower() in ("platform", "#"):
            continue
        # strip links / markdown
        name = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", name)
        name = re.sub(r"\*\*", "", name)
        name = name.split("(")[0].strip()
        if name and name not in names:
            names.append(name)
    return names


def _extract_known_platforms(text: str) -> list[str]:
    """Broader scan: URLs, domains, and named platforms across the whole file."""
    found = []
    # URLs
    for m in re.finditer(r"https?://([a-zA-Z0-9.-]+)", text):
        host = m.group(1).lower()
        root = host.split(".")[0] if host.count(".") >= 2 else host
        if root not in found and len(root) > 2:
            found.append(root)
    # bracketed platform names like [name](url) and **name**
    for m in re.finditer(r"\*\*([A-Za-z0-9 .&'-]{2,40})\*\*", text):
        n = m.group(1).strip()
        if n.lower() not in ("live", "pending", "watchlist", "known"):
            if n not in found:
                found.append(n)
    return found


def main():
    if not REGISTRY.exists():
        json.dump({
            "error": f"registry not found: {REGISTRY}",
            "already_listed": [],
            "watchlist": [],
            "known_not_pursued": [],
            "all_keywords": [],
        }, sys.stdout, indent=1)
        return 0

    text = REGISTRY.read_text(encoding="utf-8")

    # Split sections for granular classification
    live_section = text.split("## 🟢 LIVE LISTINGS")[-1].split("##")[0] if "## 🟢 LIVE LISTINGS" in text else text
    pending_section = text.split("## 🟡 PENDING / WATCHLIST")[-1].split("##")[0] if "## 🟡 PENDING / WATCHLIST" in text else ""
    known_section = text.split("## ⚪ KNOWN BUT NOT PURSUED")[-1].split("##")[0] if "## ⚪ KNOWN BUT NOT PURSUED" in text else ""

    already_listed = _extract_names_from_table(live_section)
    watchlist = _extract_names_from_table(pending_section)
    known_not_pursued = _extract_names_from_table(known_section)

    # Add the URL roots + bold names as extra keywords so dedupe is robust
    all_keywords = _extract_known_platforms(text)

    result = {
        "registry_path": str(REGISTRY.relative_to(VAULT)),
        "already_listed": already_listed,          # EXCLUDE these — we're live here
        "watchlist": watchlist,                     # EXCLUDE — pending/being worked
        "known_not_pursued": known_not_pursued,     # context, not new
        "all_keywords": all_keywords,               # any host/name to match against
        "rule": (
            "A marketplace is 'NEW' only if its name AND domain do NOT appear in "
            "already_listed, watchlist, known_not_pursued, or all_keywords. "
            "If matched, SKIP it — we already have a presence there."
        ),
    }
    json.dump(result, sys.stdout, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
