#!/usr/bin/env python3
"""TinyFish Hackathon Scanner — Daily automated hackathon discovery."""

import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Load API key
from dotenv import load_dotenv
load_dotenv('/root/.hermes/profiles/gentech/.env')

API_KEY = os.getenv("TINYFISH_API_KEY")
VAULT_PATH = Path("/root/vaults/gentech")
SCANS_PATH = VAULT_PATH / "03-Strategies" / "hackathon-scans"
TRACKER_PATH = VAULT_PATH / "00-HQ" / "hackathon-tracker.md"

def scan_url(url: str, goal: str, timeout: int = 120) -> dict:
    """Run TinyFish Agent to scrape a URL."""
    print(f"[*] Scanning: {url}")
    print(f"[*] Goal: {goal}")
    
    response = requests.post(
        "https://agent.tinyfish.ai/v1/automation/run-sse",
        headers={
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "url": url,
            "goal": goal,
            "timeout_seconds": timeout
        },
        stream=True,
        timeout=timeout + 30
    )
    
    result = {}
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if data.get('type') == 'COMPLETE':
                        result = data.get('result', {})
                        print(f"[+] Scan complete")
                    elif data.get('type') == 'PROGRESS':
                        purpose = data.get('purpose', '')
                        if purpose:
                            print(f"    {purpose}")
                except json.JSONDecodeError:
                    pass
    
    return result

def scan_devpost() -> list:
    """Scan Devpost for active hackathons."""
    goal = (
        "List all active hackathons on this page. For each hackathon, extract: "
        "name, deadline, prize pool, tracks/themes, and any requirements. "
        "Return as a JSON array of objects with keys: name, deadline, prizes, tracks, requirements. "
        "Only include hackathons that are currently accepting submissions."
    )
    result = scan_url("https://devpost.com/hackathons", goal)
    hackathons = result.get('hackathons', [])
    for h in hackathons:
        h['platform'] = 'Devpost'
    return hackathons

def scan_dorahacks() -> list:
    """Scan DoraHacks for active hackathons."""
    goal = (
        "List all active hackathons on this page. For each hackathon, extract: "
        "name, deadline, prize pool, tracks/themes, and any requirements. "
        "Return as a JSON array of objects with keys: name, deadline, prizes, tracks, requirements. "
        "Only include hackathons that are currently accepting submissions."
    )
    result = scan_url("https://dorahacks.io/hackathons", goal)
    hackathons = result.get('hackathons', [])
    for h in hackathons:
        h['platform'] = 'DoraHacks'
    return hackathons

def load_existing_tracker() -> str:
    """Load existing hackathon tracker."""
    if TRACKER_PATH.exists():
        return TRACKER_PATH.read_text()
    return ""

def find_new_hackathons(all_hackathons: list, tracker_content: str) -> list:
    """Find hackathons not already in the tracker."""
    new_hackathons = []
    for h in all_hackathons:
        name = h.get('name', '').lower()
        if name and name not in tracker_content.lower():
            new_hackathons.append(h)
    return new_hackathons

def score_fit(hackathon: dict) -> int:
    """Score hackathon fit (1-5 stars) based on keywords."""
    text = json.dumps(hackathon).lower()
    
    high_fit = ['agent', 'ai', 'solana', 'evm', 'defi', 'yield', 'erc-8004', 'x402', 'privacy', 'prediction']
    medium_fit = ['web3', 'blockchain', 'crypto', 'smart contract', 'dapp']
    low_fit = ['enterprise', 'cloud', 'aws', 'google cloud']
    
    score = 3  # baseline
    
    for keyword in high_fit:
        if keyword in text:
            score += 1
    for keyword in low_fit:
        if keyword in text:
            score -= 1
    
    return max(1, min(5, score))

def generate_summary(all_hackathons: list, new_hackathons: list) -> str:
    """Generate markdown summary."""
    date = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        f"# Hackathon Scan — {date}",
        "",
        f"**Total found:** {len(all_hackathons)}",
        f"**New (not in tracker):** {len(new_hackathons)}",
        "",
        "## All Hackathons Found",
        "",
    ]
    
    for h in all_hackathons:
        fit = score_fit(h)
        stars = "⭐" * fit
        lines.append(f"### {h.get('name', 'Unknown')} {stars}")
        lines.append(f"- **Platform:** {h.get('platform', 'Unknown')}")
        lines.append(f"- **Deadline:** {h.get('deadline', 'Unknown')}")
        lines.append(f"- **Prizes:** {h.get('prizes', 'Unknown')}")
        if h.get('tracks'):
            lines.append(f"- **Tracks:** {', '.join(h['tracks']) if isinstance(h['tracks'], list) else h['tracks']}")
        if h.get('requirements'):
            lines.append(f"- **Requirements:** {', '.join(h['requirements']) if isinstance(h['requirements'], list) else h['requirements']}")
        lines.append("")
    
    if new_hackathons:
        lines.append("## 🆕 New Opportunities")
        lines.append("")
        for h in new_hackathons:
            fit = score_fit(h)
            stars = "⭐" * fit
            lines.append(f"- **{h.get('name', 'Unknown')}** {stars} — {h.get('deadline', 'Unknown')} — {h.get('prizes', 'Unknown')}")
        lines.append("")
    
    return "\n".join(lines)

def main():
    print("=" * 60)
    print("TinyFish Hackathon Scanner")
    print("=" * 60)
    
    # Scan platforms
    all_hackathons = []
    
    try:
        devpost = scan_devpost()
        all_hackathons.extend(devpost)
        print(f"[+] Devpost: {len(devpost)} hackathons found")
    except Exception as e:
        print(f"[-] Devpost scan failed: {e}")
    
    try:
        dorahacks = scan_dorahacks()
        all_hackathons.extend(dorahacks)
        print(f"[+] DoraHacks: {len(dorahacks)} hackathons found")
    except Exception as e:
        print(f"[-] DoraHacks scan failed: {e}")
    
    # Compare with tracker
    tracker_content = load_existing_tracker()
    new_hackathons = find_new_hackathons(all_hackathons, tracker_content)
    
    print(f"\n[+] Total: {len(all_hackathons)} hackathons")
    print(f"[+] New: {len(new_hackathons)} not in tracker")
    
    # Save results
    SCANS_PATH.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    
    json_path = SCANS_PATH / f"{date}.json"
    with open(json_path, 'w') as f:
        json.dump({
            'date': date,
            'total': len(all_hackathons),
            'new': len(new_hackathons),
            'hackathons': all_hackathons,
            'new_hackathons': new_hackathons
        }, f, indent=2)
    print(f"[+] Saved JSON: {json_path}")
    
    # Generate summary
    summary = generate_summary(all_hackathons, new_hackathons)
    summary_path = SCANS_PATH / f"{date}.md"
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"[+] Saved summary: {summary_path}")
    
    # Print new opportunities
    if new_hackathons:
        print("\n" + "=" * 60)
        print("🆕 NEW OPPORTUNITIES")
        print("=" * 60)
        for h in new_hackathons:
            fit = score_fit(h)
            print(f"  {'⭐' * fit} {h.get('name', 'Unknown')} — {h.get('deadline', 'Unknown')} — {h.get('prizes', 'Unknown')}")
    
    print("\n" + "=" * 60)
    print("Scan complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
