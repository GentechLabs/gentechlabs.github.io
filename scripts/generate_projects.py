import os
import json
import re
from pathlib import Path
from datetime import datetime

VAULT_PATH = "/root/vaults/gentech/03-Projects"
OUTPUT_PATH = "/root/.hermes/profiles/gentech/home/portfolio/data/projects.json"

PROJECT_STATUS = {
    "agent-escrow-solana": {"status": "building", "deadline": "2026-05-11", "highlight": True, "timeline": "May 2026"},
    "kite-ai": {"status": "building", "deadline": "2026-05-17", "highlight": True, "timeline": "May 2026"},
    "lets-fg": {"status": "live", "deadline": None, "highlight": False, "timeline": "Apr 2026"},
    "hermes-kanban": {"status": "live", "deadline": None, "highlight": False, "timeline": "Mar 2026"},
    "tech-payment-router": {"status": "research", "deadline": None, "highlight": False, "timeline": "Feb 2026"},
    "lfj-avax-usdc-rebalance": {"status": "live", "deadline": None, "highlight": False, "timeline": "Apr 2026"},
    "birdeye-bip": {"status": "research", "deadline": None, "highlight": False, "timeline": "Feb 2026"},
}

def extract_readme_info(project_path):
    readme = Path(project_path) / "README.md"
    if not readme.exists():
        return {"description": "", "tech": []}
    
    text = readme.read_text(encoding="utf-8", errors="ignore")
    
    # First substantial paragraph after title
    lines = text.split('\n')
    description = ""
    in_desc = False
    for line in lines:
        if line.startswith('# '):
            in_desc = True
            continue
        if in_desc and line.strip() and not line.startswith('#'):
            description = line.strip()
            break
    
    tech = []
    tech_match = re.search(r'## Tech Stack\s*(.+?)\n\n', text, re.DOTALL)
    if tech_match:
        tech = re.findall(r'`([^`]+)`', tech_match.group(1))
    
    return {"description": description[:150], "tech": tech[:5]}

def discover_projects():
    projects = []
    for folder in sorted(os.listdir(VAULT_PATH)):
        folder_lower = folder.lower().replace("_", "-")
        meta = PROJECT_STATUS.get(folder_lower, {"status": "building", "deadline": None, "highlight": False, "timeline": None})
        
        project_path = os.path.join(VAULT_PATH, folder)
        if not os.path.isdir(project_path):
            continue
            
        info = extract_readme_info(project_path)
        title = folder.replace("-", " ").replace("_", " ").title()
        
        projects.append({
            "id": folder_lower,
            "title": title,
            "description": info["description"] or f"{title} — GenTech project",
            "tech": info["tech"],
            "status": meta["status"],
            "deadline": meta["deadline"],
            "timeline": meta.get("timeline"),
            "highlight": meta["highlight"],
            "vault_path": f"03-Projects/{folder}"
        })
    
    projects.sort(key=lambda p: (not p["highlight"], p["deadline"] or "9999"))
    return projects

if __name__ == "__main__":
    data = {
        "projects": discover_projects(),
        "generated": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "vault 03-Projects/"
    }
    Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    Path(OUTPUT_PATH).write_text(json.dumps(data, indent=2))
    print(f"✅ Generated {len(data['projects'])} projects")
