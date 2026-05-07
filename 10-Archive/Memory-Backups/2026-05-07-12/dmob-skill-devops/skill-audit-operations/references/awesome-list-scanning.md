# Awesome-List Scanning Cookbook

## Goal

Scan curated "awesome" lists (like `awesome-hermes-agent`) for new resources matching your domain keywords, and produce a structured, actionable report.

## General Pattern

1. **Fetch** — Grab the raw markdown (use raw.githubusercontent.com, not HTML)
2. **Parse** — Line-by-line with section tracking (`##` / `###` headers)
3. **Filter** — Match entry lines against domain keyword list
4. **Dedupe** — Cross-reference against already-installed resources
5. **Report** — JSON with section, entry, matching keywords, and novelty status

---

## Code Template (Python)

```python
import requests
from datetime import datetime
from typing import List, Dict, Set

def scan_awesome_list(
  repo: str,
  branch: str,
  readme_path: str,
  domain_keywords: Dict[str, List[str]],
  already_installed: Set[str] = None
) -> Dict:
  """
  Scan an awesome-list README and filter by domain keywords.

  Args:
    repo: "owner/repo" (e.g., "0xNyk/awesome-hermes-agent")
    branch: default branch (usually "main")
    readme_path: path to README in repo (usually "/README.md")
    domain_keywords: {"blockchain": ["solidity", "evm"], "hackathon": ["hackathon", "bounty"]}
    already_installed: set of skill names you already have installed

  Returns:
    {
      "scan_date": "...",
      "repo": "...",
      "total_entries": N,
      "matches": [
        {
          "section": "Integrations & Bridges",
          "entry": "[chainlink-agent-skills](https://github.com/smartcontractkit/chainlink-agent-skills) — Official Chainlink...",
          "matched_keywords": ["blockchain", "defi"],
          "resource_name": "chainlink-agent-skills",
          "url": "https://github.com/smartcontractkit/chainlink-agent-skills",
          "already_installed": false
        }
      ]
    }
  """
  raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}{readme_path}"
  resp = requests.get(raw_url, timeout=15)
  resp.raise_for_status()
  
  lines = resp.text.split('\n')
  current_section = None
  matches = []
  
  for line in lines:
    line_stripped = line.strip()
    if line_stripped.startswith('## ') or line_stripped.startswith('### '):
      current_section = line_stripped.lstrip('#').strip()
      continue
    
    # Quick filter: must contain '[' and '](' to be a markdown link entry
    if '[' not in line or '](' not in line:
      continue
    
    line_lower = line.lower()
    matched_keywords = []
    for domain, keywords in domain_keywords.items():
      if any(kw in line_lower for kw in keywords):
        matched_keywords.extend(kw for kw in keywords if kw in line_lower)
    
    if matched_keywords:
      # Extract resource name from markdown link: [name](url) → name
      import re
      m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
      if m:
        resource_name = m.group(1)
        resource_url = m.group(2)
      else:
        resource_name = line_stripped[:60]
        resource_url = ""
      
      matches.append({
        "section": current_section,
        "entry": line_stripped,
        "matched_keywords": list(set(matched_keywords)),
        "resource_name": resource_name,
        "url": resource_url,
        "already_installed": (resource_name.lower() in (already_installed or set()))
      })
  
  return {
    "scan_date": datetime.utcnow().isoformat() + "Z",
    "repo": repo,
    "total_entries": len(matches),
    "matches": matches
  }
```

---

## Usage Example (Gentech Labs)

```python
# Define Gentech's interest domains
DOMAIN_KEYWORDS = {
  "blockchain": ["blockchain", "smart contract", "solidity", "web3", "evm", "ethereum", "audit"],
  "defi": ["defi", "decentralized finance", "uniswap", "aave", "curve", "lp", "liquidity", "yield", "protocol"],
  "hackathon": ["hackathon", "bounty", "competition", "submission", "sponsor"],
  "solana": ["solana", "anchor", "spl", "colosseum"],
  "base": ["base", "base chain", "coinbase"],
  "aae": ["aae", "autonomous agent", "agent", "multi-agent"],
}

# Already installed skill names (from `hermes skills list`)
installed = {"hermes-agent", "blockchain-operations", "hackathon-prep", "security-contest-monitoring"}

# Scan
result = scan_awesome_list(
  repo="0xNyk/awesome-hermes-agent",
  branch="main",
  readme_path="/README.md",
  domain_keywords=DOMAIN_KEYWORDS,
  already_installed=installed
)

# Filter to only novel resources
novel = [m for m in result["matches"] if not m["already_installed"]]
print(f"Found {len(novel)} new relevant resources:")
for item in novel:
  print(f"  [{item['section']}] {item['resource_name']}")
  print(f"    Keywords: {', '.join(item['matched_keywords'])}")
  print(f"    URL: {item['url']}")
```

---

## Rate Limiting & Caching

GitHub raw endpoints are rate-limited to 60 requests/hour unauthenticated.

**Cache strategy:**
```bash
# Store README cache with timestamp
CACHE_DIR="/root/skills/.cache"
CACHE_FILE="$CACHE_DIR/awesome_hermes_agent.md"
CACHE_META="$CACHE_FILE.meta"

if [ -f "$CACHE_FILE" ]; then
  cache_age=$(( ( $(date +%s) - $(stat -c %Y "$CACHE_FILE") ) / 60 ))
  if [ $cache_age -lt 1440 ]; then  # < 24 hours
    echo "Using cached README (age: ${cache_age}m)"
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# Fetch fresh
curl -s -o "$CACHE_FILE" "https://raw.githubusercontent.com/0xNyk/awesome-hermes-agent/main/README.md"
date +%s > "$CACHE_META"
cat "$CACHE_FILE"
```

**Authenticated fetch (higher limits):**
```bash
export GITHUB_TOKEN="ghp_xxx"  # from ~/.hermes/.env or vault
curl -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3.raw" \
     -s -o "$CACHE_FILE" "$RAW_URL"
```

---

## Multi-List Scanning

When you need coverage beyond a single list, scan multiple awesome-lists in parallel:

```python
AWESOME_LISTS = [
  {"repo": "0xNyk/awesome-hermes-agent", "name": "Hermes Agent"},
  {"repo": "bokub/awesome-canbus", "name": "CAN bus (if doing vehicle/embedded)"},
  {"repo": "blockchain-ethereum/awesome-ethereum", "name": "Ethereum"},
  {"repo": "solana-labs/awesome-solana", "name": "Solana"},
]

# Aggregate matches across lists
all_matches = []
for lst in AWESOME_LISTS:
  result = scan_awesome_list(lst["repo"], "main", "/README.md", DOMAIN_KEYWORDS, installed)
  for m in result["matches"]:
    m["source_list"] = lst["name"]
  all_matches.extend(result["matches"])
```

---

## Output for DMOB/Labs

Save to `/tmp/awesome-scan-<date>.json` with structure:

```json
{
  "scan_date": "2026-05-03T11:47:00Z",
  "sources_checked": [
    {"name": "awesome-hermes-agent", "repo": "0xNyk/awesome-hermes-agent", "status": "ok"}
  ],
  "total_matches": 8,
  "novel_resources": 8,
  "matches": [
    {
      "resource_name": "chainlink-agent-skills",
      "url": "https://github.com/smartcontractkit/chainlink-agent-skills",
      "section": "agentskills.io Ecosystem",
      "matched_domains": ["blockchain", "defi"],
      "already_installed": false,
      "action": "review for integration"
    }
  ]
}
```

---

## Pitfalls

### Pitfall: README structure changes (different heading levels or no `##`)
**Fix:** Accept both `##` and `###` as section headers; if none found, track section as `None` and rely on full-text match context.

### Pitfall: Keyword matches false positives (e.g., "audit" in "audit trail" not "security audit")
**Fix:** Use word-boundary-aware matching or phrase-level keywords (prefer "security audit" over just "audit").

### Pitfall: Resource already installed under different name
**Fix:** Cross-check not just by name substring but also by URL (if present). Maintain `also_known_as` mapping in config for DMOB skill aliases (e.g., `solana-hackathon-build` → `colosseum-resources`).

### Pitfall: Awesome-list itself is out of date
**Fix:** Note the list's last commit date in the report. If list hasn't been updated in 6+ months, treat matches with lower confidence.

---

## Reusable Script

Save as `/usr/local/bin/scan-awesome-hermes`:

```bash
#!/bin/bash
# Scan awesome-hermes-agent for new domain resources
# Dependencies: python3, requests

OUTPUT="/tmp/awesome-scan-$(date +%Y%m%d).json"
python3 - <<PY
import requests, json, sys, re
from datetime import datetime

repo = "0xNyk/awesome-hermes-agent"
branch = "main"
path = "/README.md"
url = f"https://raw.githubusercontent.com/{repo}/{branch}{path}"

# Load installed skill list
installed = set()
try:
  with open('/tmp/installed_skills.txt') as f:
    installed = {line.strip() for line in f}
except: pass

# Domain keywords (extend as needed)
domains = {
  "blockchain": ["blockchain", "smart contract", "solidity", "web3", "evm"],
  "defi": ["defi", "uniswap", "aave", "curve", "lp", "liquidity"],
  "hackathon": ["hackathon", "bounty", "competition"],
  "solana": ["solana", "anchor", "spl"],
  "base": ["base", "coinbase"],
  "aae": ["aae", "autonomous agent", "agent"],
}
keywords = [kw for kws in domains.values() for kw in kws]

resp = requests.get(url, timeout=15)
resp.raise_for_status()
lines = resp.text.split('\n')

current_section = None
matches = []

for line in lines:
  s = line.strip()
  if s.startswith('## ') or s.startswith('### '):
    current_section = s.lstrip('#').strip()
    continue
  if '[' in line and '](' in line:
    line_lower = line.lower()
    matched = [kw for kw in keywords if kw in line_lower]
    if matched:
      m = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
      name = m.group(1) if m else line[:60]
      url = m.group(2) if m else ""
      already = any(name.lower() in inst or (url and url in inst) for inst in installed)
      matches.append({
        "section": current_section,
        "resource_name": name,
        "url": url,
        "matched_keywords": matched,
        "already_installed": already
      })

result = {
  "scan_date": datetime.utcnow().isoformat()+"Z",
  "repo": repo,
  "total_matches": len(matches),
  "novel": [m for m in matches if not m["already_installed"]],
  "matches": matches
}

print(json.dumps(result, indent=2))
PY
```

---

## Trigger Words (When to Run)

- "Check for new blockchain/DeFi skills"
- "Scan awesome-hermes-agent for Solana resources"
- "What new hackathon tools are available"
- "External resource audit"
- Periodic (weekly/biweekly)
