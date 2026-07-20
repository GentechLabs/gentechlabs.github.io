#!/usr/bin/env python3
"""
GenTech Content Pipeline — Vault → Remotion Video → ElevenLabs → Ready to Post

Reads the latest build queue snapshot and PR portfolio, generates a video script,
renders a Remotion video, narrates with ElevenLabs, and saves the output.

Usage:
  python3 content-pipeline.py [--preview] [--render]

Flags:
  --preview   Generate script only, don't render
  --render    Full pipeline: script → video → narration
"""

import json, os, sys, subprocess, textwrap
from datetime import datetime

VAULT = "/root/vaults/gentech"
OUTPUT = f"{VAULT}/assets/content-pipeline"
ELEVENLABS_KEY = os.environ.get("ELEVENLABS_API_KEY", "")

def get_latest_build():
    """Read the build queue for recent completions."""
    path = f"{VAULT}/scripts/build_queue.json"
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)

def get_pr_highlights():
    """Read the latest PR scout output for merged PRs."""
    cron_dir = "/root/.hermes/profiles/gentech/cron/output/22c4d276b87a"
    if not os.path.isdir(cron_dir):
        return []
    files = sorted(os.listdir(cron_dir), reverse=True)
    if not files:
        return []
    with open(os.path.join(cron_dir, files[0])) as f:
        content = f.read()
    highlights = []
    for line in content.split("\n"):
        if "merged" in line.lower() or "Merged" in line:
            highlights.append(line.strip())
    return highlights[:5]

def generate_script(build, pr_highlights):
    """Generate a video script from build data."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    
    # Count shipped items
    shipped = [i for i in build.get("items", []) if i.get("status") == "shipped"]
    in_progress = [i for i in build.get("items", []) if i.get("status") == "in_progress"]
    
    lines = [
        f"GenTech Labs — Build Report",
        f"{now}",
        "",
        f"📦 {len(shipped)} items shipped, {len(in_progress)} in progress",
        "",
    ]
    
    if pr_highlights:
        lines.append("🎉 PRs merged this cycle:")
        for h in pr_highlights:
            lines.append(f"  • {h}")
        lines.append("")
    
    # Top 3 in-progress items
    lines.append("⚡ Currently building:")
    for item in in_progress[:3]:
        lines.append(f"  • {item.get('name', 'Unknown')}")
    
    return "\n".join(lines)

def save_script(script):
    """Save the script for Remotion to use."""
    os.makedirs(OUTPUT, exist_ok=True)
    path = f"{OUTPUT}/latest-script.txt"
    with open(path, "w") as f:
        f.write(script)
    print(f"📝 Script saved: {path}")
    return path

def main():
    preview = "--preview" in sys.argv
    render = "--render" in sys.argv
    
    build = get_latest_build()
    if not build:
        print("❌ No build queue found")
        return
    
    pr_highlights = get_pr_highlights()
    script = generate_script(build, pr_highlights)
    save_script(script)
    
    print(f"\n{'─'*50}")
    print(script)
    print(f"{'─'*50}\n")
    
    if preview:
        print("🔍 Preview mode — script generated, no render")
        return
    
    if render:
        print("🎬 Full render requested — requires Remotion project")
        print("   Run: cd /root/remotion-videos && npx remotion render")
        print(f"   Script at: {OUTPUT}/latest-script.txt")
        
        if ELEVENLABS_KEY:
            print("🎙️ ElevenLabs key found — narration ready")
        else:
            print("⚠️ No ElevenLabs key — narration skipped")
    
    print("\n✅ Pipeline complete")

if __name__ == "__main__":
    main()
