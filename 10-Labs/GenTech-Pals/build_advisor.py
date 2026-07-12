#!/usr/bin/env python3
"""
GenTech Pals — Build File Parser & Advisor
Reads POE2 build files from vault, analyzes them, gives personalized advice.
"""

import re
import sys
from pathlib import Path

VAULT_BASE = Path("/root/vaults/gentech/15-Gaming")
BUILD_FILE = VAULT_BASE / "POE-2" / "Jordan Monk build.md"


def parse_build_file(filepath: Path) -> dict:
    """Parse a build markdown file into structured data."""
    if not filepath.exists():
        return {"error": f"Build file not found: {filepath}"}
    
    content = filepath.read_text()
    build = {
        "filename": filepath.name,
        "game": filepath.parent.name,
        "sections": {},
        "skills": [],
        "synergy_loop": [],
        "goals": [],
        "patch_notes": []
    }
    
    current_section = None
    current_list = []
    
    for line in content.split("\n"):
        line = line.strip()
        
        # Detect section headers
        if line.startswith("## "):
            if current_section and current_list:
                build["sections"][current_section] = current_list
            current_section = line[3:].strip()
            current_list = []
            continue
        
        # Detect subsections
        if line.startswith("### "):
            if current_section and current_list:
                build["sections"][current_section] = current_list
            current_section = line[4:].strip()
            current_list = []
            continue
        
        # Collect list items
        if line.startswith("- **") or line.startswith("- "):
            current_list.append(line)
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            current_list.append(line)
        elif re.match(r"^\d+\.", line):
            current_list.append(line)
    
    if current_section and current_list:
        build["sections"][current_section] = current_list
    
    # Extract skills specifically
    for section_name, items in build["sections"].items():
        if "skill" in section_name.lower() or "active" in section_name.lower():
            for item in items:
                skill_match = re.search(r"\*\*(.+?)\*\*", item)
                if skill_match:
                    build["skills"].append({
                        "name": skill_match.group(1),
                        "description": item,
                        "section": section_name
                    })
        
        if "synergy" in section_name.lower() or "loop" in section_name.lower():
            build["synergy_loop"] = items
        
        if "goal" in section_name.lower():
            build["goals"] = items
        
        if "patch" in section_name.lower():
            build["patch_notes"] = items
    
    return build


def analyze_build(build: dict) -> list:
    """Analyze a build and return advice."""
    advice = []
    
    skills = [s["name"] for s in build.get("skills", [])]
    
    # Check for mana sustain
    mana_skills = [s for s in skills if "mana" in s.lower() or "drain" in s.lower()]
    if not mana_skills:
        advice.append({
            "type": "warning",
            "topic": "Mana Sustain",
            "message": "No mana sustain skill detected. You may run OOM in extended fights. Consider adding Mana Drain or a mana leech source."
        })
    else:
        advice.append({
            "type": "ok",
            "topic": "Mana Sustain",
            "message": f"Mana sustain covered by: {', '.join(mana_skills)}"
        })
    
    # Check for mobility
    mobility_skills = [s for s in skills if "strike" in s.lower() or "dash" in s.lower() or "leap" in s.lower() or "flurry" in s.lower()]
    if not mobility_skills:
        advice.append({
            "type": "warning",
            "topic": "Mobility",
            "message": "No mobility skill detected. Consider adding a movement skill for repositioning."
        })
    else:
        advice.append({
            "type": "ok",
            "topic": "Mobility",
            "message": f"Mobility covered by: {', '.join(mobility_skills)}"
        })
    
    # Check for AoE clear
    aoe_skills = [s for s in skills if "thunder" in s.lower() or "storm" in s.lower() or "nova" in s.lower() or "aoe" in s.lower()]
    if not aoe_skills:
        advice.append({
            "type": "info",
            "topic": "AoE Clear",
            "message": "No obvious AoE clear skill. May struggle with large packs."
        })
    
    # Check for execute/finisher
    execute_skills = [s for s in skills if "kill" in s.lower() or "palm" in s.lower() or "execute" in s.lower() or "cull" in s.lower()]
    if not execute_skills:
        advice.append({
            "type": "info",
            "topic": "Execute/Finisher",
            "message": "No execute skill detected. Consider adding a culling or finishing move for bosses."
        })
    
    # Check synergy loop exists
    if not build.get("synergy_loop"):
        advice.append({
            "type": "warning",
            "topic": "Synergy Loop",
            "message": "No synergy loop defined. Map out your skill rotation for optimal damage."
        })
    
    # General advice based on skill count
    skill_count = len(skills)
    if skill_count > 8:
        advice.append({
            "type": "info",
            "topic": "Skill Count",
            "message": f"You have {skill_count} active skills. Consider trimming to focus on core rotation."
        })
    elif skill_count < 4:
        advice.append({
            "type": "info",
            "topic": "Skill Count",
            "message": f"Only {skill_count} active skills. You may want more utility or situational options."
        })
    
    return advice


def format_build_report(build: dict, advice: list) -> str:
    """Format build analysis into a readable report."""
    lines = []
    lines.append(f"🎮 **GenTech Pals — Build Report**")
    lines.append(f"Game: {build.get('game', 'Unknown')}")
    lines.append(f"File: {build.get('filename', 'Unknown')}")
    lines.append("")
    
    # Skills
    if build.get("skills"):
        lines.append("**Active Skills:**")
        for s in build["skills"]:
            lines.append(f"  • {s['name']}")
        lines.append("")
    
    # Synergy Loop
    if build.get("synergy_loop"):
        lines.append("**Synergy Loop:**")
        for item in build["synergy_loop"]:
            lines.append(f"  {item}")
        lines.append("")
    
    # Goals
    if build.get("goals"):
        lines.append("**Goals:**")
        for item in build["goals"]:
            lines.append(f"  {item}")
        lines.append("")
    
    # Advice
    lines.append("**📋 Advisor Assessment:**")
    for a in advice:
        icon = "⚠️" if a["type"] == "warning" else "✅" if a["type"] == "ok" else "ℹ️"
        lines.append(f"  {icon} **{a['topic']}**: {a['message']}")
    
    return "\n".join(lines)


def main():
    """Main entry point."""
    build = parse_build_file(BUILD_FILE)
    
    if "error" in build:
        print(f"❌ {build['error']}")
        sys.exit(1)
    
    advice = analyze_build(build)
    report = format_build_report(build, advice)
    print(report)


if __name__ == "__main__":
    main()
