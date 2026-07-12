#!/usr/bin/env python3
"""
GenTech Pals — Telegram Bot Interface
Wraps the build advisor and patch scanner for Telegram delivery.
"""

import sys
from pathlib import Path

# Add the project directory to path
sys.path.insert(0, str(Path(__file__).parent))

from build_advisor import parse_build_file, analyze_build, format_build_report
from patch_scanner import extract_skills_from_build, check_relevance

# Build file paths
BUILD_FILES = {
    "poe2": Path("/root/vaults/gentech/15-Gaming/POE-2/Jordan Monk build.md"),
    "vanito": Path("/root/vaults/gentech/15-Gaming/POE-2/Vanito.md"),
}


def handle_build_check(game: str = "poe2") -> str:
    """Handle a build check request."""
    filepath = BUILD_FILES.get(game)
    if not filepath:
        return f"❌ No build file found for game: {game}\nAvailable: {', '.join(BUILD_FILES.keys())}"
    
    build = parse_build_file(filepath)
    if "error" in build:
        return f"❌ {build['error']}"
    
    advice = analyze_build(build)
    return format_build_report(build, advice)


def handle_build_advice(game: str, question: str) -> str:
    """Handle a specific build advice question."""
    filepath = BUILD_FILES.get(game)
    if not filepath:
        return f"❌ No build file found for game: {game}"
    
    build = parse_build_file(filepath)
    if "error" in build:
        return f"❌ {build['error']}"
    
    # Simple keyword-based advice (MVP)
    question_lower = question.lower()
    skills = [s["name"] for s in build.get("skills", [])]
    
    # Mana questions
    if "mana" in question_lower or "oom" in question_lower:
        mana_skills = [s for s in build.get("skills", []) if "mana" in s["name"].lower() or "drain" in s["name"].lower()]
        if mana_skills:
            return f"💧 **Mana Sustain:** Your build uses {mana_skills[0]['name']} for mana recovery. Make sure it's leveled appropriately and linked with mana regeneration supports."
        else:
            return "⚠️ **Mana Issue:** Your build has no dedicated mana sustain skill. Consider adding Mana Drain or a mana leech source to prevent OOM in extended fights."
    
    # Damage questions
    if "damage" in question_lower or "dps" in question_lower or "burst" in question_lower:
        damage_skills = [s for s in build.get("skills", []) if any(w in s["name"].lower() for w in ["thunder", "storm", "frenzy", "flurry"])]
        if damage_skills:
            return f"⚡ **Damage Sources:** Your primary damage comes from: {', '.join([s['name'] for s in damage_skills])}. Focus on lightning penetration and elemental damage nodes in your passive tree."
    
    # Survivability questions
    if "survive" in question_lower or "tank" in question_lower or "defense" in question_lower or "hp" in question_lower:
        return "🛡️ **Survivability:** As a lightning Invoker, your defenses rely on evasion and energy shield. Make sure you're picking up ES/evasion nodes in the passive tree. Consider a granite flask for physical damage reduction."
    
    # Passive tree questions
    if "passive" in question_lower or "tree" in question_lower or "refund" in question_lower or "respec" in question_lower:
        return "🌳 **Passive Tree:** For your lightning Invoker, focus on the center-top area for lightning damage, AoE, and mana nodes. Avoid the bottom-left (Strength/physical area). Prioritize: Mana > Lightning Damage > AoE > ES/Evasion."
    
    # Gear questions
    if "gear" in question_lower or "equipment" in question_lower or "weapon" in question_lower:
        return "🔧 **Gear Priority:**\n1. Quarterstaff with +lightning damage and spell damage\n2. Armor with high evasion + energy shield\n3. Rings/amulets with mana regeneration\n4. Boots with movement speed\n5. Belt with flask effectiveness"
    
    # Fallback — generic advice based on build
    return f"🎮 **Build Overview:** You're running a {build.get('sections', {}).get('Strategy', [''])[0] if build.get('sections', {}).get('Strategy') else 'lightning Invoker'} build. Your core skills are: {', '.join(skills[:5])}. Ask me about mana, damage, survivability, passives, or gear for specific advice."


def main():
    """CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: python bot_wrapper.py check [game] | advice [game] [question]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "check":
        game = sys.argv[2] if len(sys.argv) > 2 else "poe2"
        print(handle_build_check(game))
    
    elif command == "advice":
        game = sys.argv[2] if len(sys.argv) > 2 else "poe2"
        question = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else "general"
        print(handle_build_advice(game, question))
    
    else:
        print(f"Unknown command: {command}")
        print("Usage: python bot_wrapper.py check [game] | advice [game] [question]")


if __name__ == "__main__":
    main()
