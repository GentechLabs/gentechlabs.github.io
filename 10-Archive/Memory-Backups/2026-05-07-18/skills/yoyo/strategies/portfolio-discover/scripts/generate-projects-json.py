#!/usr/bin/env python3
"""
Portfolio Project Discovery — generates projects.json from vault 03-Projects/ scan.

Reality-based labeling: uses hackathon deadlines, WIP/TBA flags; no aspirational dates.
Run: python3 generate-projects-json.py
Output: ~/portfolio/data/projects.json
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

VAULT_ROOT = Path("/root/vaults/gentech")
PROJECTS_DIR = VAULT_ROOT / "03-Projects"
OUTPUT_PATH = Path.home() / "portfolio" / "data" / "projects.json"

# Patterns for status detection
HACKATHON_PATTERNS = [
    r"(Solana Frontier|Kite AI|Retro9000).*?(?:May|Jun|Jul)\s+(\d{1,2})",
    r"deadline\s*[:\-]\s*(?:May|Jun|Jul)\s+(\d{1,2})",
    r"Hackathon\s*[:\-]\s*(?:May|Jun|Jul)\s+(\d{1,2})",
]
WIP_PATTERNS = [r"Phase\s+\d+", r"WIP", r"In Progress", r"Ready to start", r"Sprint"]
LIVE_PATTERNS = [r"\bLive\b", r"\bProduction\b", r"\bDeployed\b"]
RESEARCH_PATTERNS = [r"research", r"recon", r"SDK", r"comparison", r"exploratory"]

TECH_KEYWORDS = {
    "Solana": ["Solana", "Anchor", "Rust", "Solana "],
    "Avalanche": ["Avalanche", "AVAX", "Subnet"],
    "Python": ["Python", "FastAPI", "Pipecat"],
    "Maps": ["Google Maps", "Map", "Geocoding", "Street View"],
    "Voice": ["ElevenLabs", "TTS", "voice", "audio"],
    "DeFi": ["LP", "yield", "trading", "DeFi", "Aave", "LFJ"],
    "Foundry": ["Foundry", "Forge", "Cast"],
    "Hardhat": ["Hardhat", "Ethers", "ethers"],
    "x402": ["x402", "402", "pay-per-request"],
}

# Excluded meta-folders
EXCLUDE_DIRS = {".git", "hermes-kanban", "HACKATHON-ROSTER-2026.md", "defi-milestones.md", ".github", ".pytest_cache", "plugin", "docs", "scripts", "tests", "cli", "out", "cache", "lib", "node_modules"}

def extract_status_label(project_path: Path, files: list) -> tuple[str, str, list[str], str | None]:
    """Return (status_label, description, tech_stack, deadline_iso)."""
    text = ""
    # Read prioritized files
    for fname in ["Implementation-Plan.md", "README.md", "SPRINT1-STATUS.md", "index.md"]:
        if fname in files:
            fpath = project_path / fname
            try:
                text += fpath.read_text()[:3000] + "\n"
            except:
                pass

    # 1. Check hackathon deadline from HACKATHON-ROSTER
    roster = PROJECTS_DIR / "HACKATHON-ROSTER-2026.md"
    if roster.exists():
        roster_text = roster.read_text()
        deadline_match = re.search(r"\|\s*Solana Frontier\s*\|\s*May (\d{1,2})", roster_text)
        if deadline_match:
            pass  # will apply later if project matches

    # 2. Detect patterns
    has_wip = any(re.search(p, text, re.I) for p in WIP_PATTERNS)
    has_live = any(re.search(p, text, re.I) for p in LIVE_PATTERNS)
    has_research = any(re.search(p, text, re.I) for p in RESEARCH_PATTERNS)

    # 3. Extract tech stack
    tech_stack = []
    for tech, patterns in TECH_KEYWORDS.items():
        if any(re.search(p, text, re.I) for p in patterns):
            tech_stack.append(tech)
    # Dedupe, keep order
    tech_stack = list(dict.fromkeys(tech_stack))

    # 4. Build status label
    if has_live:
        status = f"Live — {', '.join(tech_stack[:2]) if tech_stack else 'APIs'} — WIP"
    elif has_wip:
        # Check for hackathon mention
        hack_match = re.search(r"(Solana Frontier).*?May (\d{1,2})", text, re.I)
        if hack_match:
            date_str = f"May {hack_match.group(2)}"
            status = f"Building — {', '.join(tech_stack[:2]) if tech_stack else 'TBD'} — Hackathon: {date_str}"
        else:
            status = f"Building — {', '.join(tech_stack[:2]) if tech_stack else 'TBD'} — WIP"
    elif has_research:
        status = f"Research — {tech_stack[0] if tech_stack else 'TBD'} — TBA"
    else:
        status = "Planning — TBA"

    # 5. Extract deadline (if any)
    deadline = None
    dl_match = re.search(r"May (\d{1,2})", text)
    if dl_match:
        try:
            deadline = f"2026-05-{int(dl_match.group(1)):02d}"
        except:
            pass

    # 6. Description: first meaningful line after title or first paragraph
    desc = ""
    for line in text.split("\n"):
        line = line.strip()
        if line and not line.startswith("#") and len(line) > 20:
            desc = line[:200]
            break
    if not desc:
        desc = f"{project_path.name} project"

    return status, desc, tech_stack, deadline

def scan_projects() -> list[dict]:
    projects = []
    if not PROJECTS_DIR.exists():
        return projects

    for item in sorted(PROJECTS_DIR.iterdir()):
        if not item.is_dir() or item.name in EXCLUDE_DIRS:
            continue
        files = [f.name for f in item.iterdir() if f.is_file()]
        # Skip if no docs
        if not any(f.lower().endswith((".md", ".txt")) for f in files):
            continue

        name = item.name
        status, desc, tech, deadline = extract_status_label(item, files)

        projects.append({
            "name": name,
            "status": status,
            "desc": desc,
            "tech": tech,
            "deadline": deadline
        })

    # Sort: deadline ascending first, then keep original order within groups
    projects.sort(key=lambda p: (p["deadline"] is None, p["deadline"] or "9999"))
    return projects

def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    projects = scan_projects()
    OUTPUT_PATH.write_text(json.dumps(projects, indent=2))
    print(f"✓ Wrote {len(projects)} projects to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
