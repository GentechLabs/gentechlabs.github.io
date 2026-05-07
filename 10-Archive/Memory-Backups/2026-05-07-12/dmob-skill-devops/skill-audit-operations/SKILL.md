---
name: skill-audit-operations
description: Systematic skill version auditing, health checks, and external resource scanning for Hermes Agent ecosystems. Covers multi-layer skill storage inspection, git-based update detection, vault coupling, and awesome-list resource discovery with domain filtering.
version: 1.0.0
author: DMOB (Labs)
license: MIT
metadata:
  hermes:
    tags: [skills, audit, maintenance, hermes-agent, version-check, health-monitor]
    related_skills: [hermes-operations, hackathon-prep]
---

# Skill Audit Operations

Auditing skill health, detecting available updates, and scanning external resource ecosystems (awesome lists, community hubs) for relevant new integrations. Designed for periodic cron execution or manual maintenance.

---

## When to Use

**Trigger:** Jordan asks to "check skill updates", "audit skill health", "scan for new resources", or scheduled weekly/monthly cron.

**Do NOT use** for installing/updating specific skills (use `hermes skills update`) or for one-off skill development (use skill authoring workflow).

---

## Multi-Layer Skill Architecture (Gentech Context)

Hermes Agent skill storage is multi-layered; audit ALL of them:

| Layer | Location | Source Type | Notes |
|-------|----------|-------------|-------|
| Built-in skills | `/usr/local/lib/hermes-agent/skills/` or package install | Bundled, read-only | Part of core install; updates via `hermes update` |
| Bundled skill repo | `/root/skills/` (79 modules across categories) | Git-tracked, shared | Contains `base/`, `solana/`, `github/`, `devops/`, etc. |
| Custom/local skills | Instance-specific (vault or derived) | Local | Often non-git; loaded by `hermes` automatically from discovered paths |
| Vault-stored skills | `/root/vaults/gentech/` (coupled via backup/sync) | Mirrored | Skill SKILL.md files appear in vault memory backups; use `ob sync` to reconcile |

**Key insight:** `hermes skills list` shows 98 installed skills but they come from multiple sources. Git-based tracking only exists for `/root/skills/` and the Hermes core repo itself.

---

## Audit Phases

### Phase 1: Core Hermes Agent Version Check

```bash
# Check installed version
hermes --version

# Dry-run update check
hermes update --dry-run

# If installed from git (common in dev installs)
git -C /usr/local/lib/hermes-agent status
git -C /usr/local/lib/hermes-agent fetch origin
git -C /usr/local/lib/hermes-agent log --oneline HEAD..origin/main -5
```

**Output:** Core agent version + available update commits if any.

---

### Phase 2: Git-Tracked Skill Repos Scan

Target: `/root/skills/*/` directories containing `SKILL.md` with `.git` folders.

```bash
# List all skill SKILL.md files
find /root/skills -name SKILL.md | while read f; do
  dir=$(dirname "$f")
  name=$(basename "$dir")
  if [ -d "$dir/.git" ]; then
    echo "Skill: $name"
    git -C "$dir" fetch origin --quiet
    current=$(git -C "$dir" rev-parse HEAD)
    latest=$(git -C "$dir" rev-parse origin/main 2>/dev/null || 
             git -C "$dir" rev-parse origin/master)
    if [ "$current" != "$latest" ]; then
      echo "  ⚠️ OUT OF DATE: $current → $latest"
      git -C "$dir" log --oneline "$current..$latest" -5 | sed 's/^/    /'
    else
      echo "  ✓ Up to date ($current)"
    fi
  else
    echo "Skill: $name (local, not git-tracked)"
  fi
done
```

**Output:** Per-skill status: `✓ Up to date`, `⚠️ OUT OF DATE` with commit diff, or `local` (no git history).

**Pitfall:** Some skill dirs have `.git` but the remote origin branch may be `master` not `main` — check both.

---

### Phase 3: Custom Skill Discovery & Mapping

Local skills (no git) are often installed from skill hubs or hand-crafted. Map them to known sources:

```bash
# Get installed skill list from Hermes
hermes skills list | tail -n +3 | awk '{print $1}' > /tmp/installed_skills.txt

# Cross-reference against known skill hub manifests
# Check /root/skills/.bundled_manifest for skill IDs + hashes
jq -r 'skills | keys[]' /root/skills/.bundled_manifest 2>/dev/null > /tmp/bundled_skills.txt

# Diff to identify unaccounted-for local skills
comm -23 /tmp/installed_skills.txt /tmp/bundled_skills.txt > /tmp/local_only_skills.txt
```

**Output:** List of local-only skills (no bundled/manifest source). These require manual provenance tracking.

**Recommendation:** For DMOB/Labs critical skills, prefer git-tracking under `/root/skills/<category>/` or vault `02-Labs/Skills/` for version control.

---

### Phase 4: External Resource Scanning (Awesome-List + Community Hubs)

Scan curated awesome lists and skill hubs for new blockchain/DeFi/hackathon resources.

#### Pattern: Awesome-List Fetch + Domain Filter

```python
import requests
from typing import List, Dict

def scan_awesome_hermes(domain_keywords: List[str]) -> List[Dict]:
  """Fetch awesome-hermes-agent README and filter for domain-specific resources."""
  url = "https://raw.githubusercontent.com/0xNyk/awesome-hermes-agent/main/README.md"
  resp = requests.get(url, timeout=15)
  if resp.status_code != 200:
    return []
  
  lines = resp.text.split('\n')
  current_section = None
  matches = []
  
  for line in lines:
    if line.startswith('## ') or line.startswith('### '):
      current_section = line.strip('# ').strip()
    elif '[' in line and ']' in line and '(' in line:
      line_lower = line.lower()
      if any(kw in line_lower for kw in domain_keywords):
        matches.append({
          'section': current_section,
          'entry': line.strip(),
          'keywords': [kw for kw in domain_keywords if kw in line_lower]
        })
  return matches

# Domain keywords for Gentech focus
domains = {
  'blockchain': ['blockchain', 'smart contract', 'solidity', 'web3', 'evm', 'ethereum'],
  'defi': ['defi', 'decentralized finance', 'uniswap', 'aave', 'curve', 'lp', 'liquidity pool', 'yield'],
  'hackathon': ['hackathon', 'hack-together', 'bounty', 'competition', 'submission'],
  'audit': ['audit', 'security review', 'vulnerability', 'bug bounty', 'security contest'],
  'solana': ['solana', 'anchor', 'spl'],
  'base': ['base', 'base chain', 'coinbase'],
  'aae': ['aae', 'autonomous agent', 'autonomous', 'agent'],
}

# Example usage
new_resources = scan_awesome_hermes(
  domain_keywords=domains['blockchain'] + domains['defi'] + domains['solana']
)
```

**Output:** List of relevant resources with section context. Cross-reference against already-installed skills to identify new ones.

**Pitfall:** GitHub API rate limits (403) for raw content; fallback to direct raw.githubusercontent.com fetch as shown.

---

## Integrated Audit Report

Combine all phases into a single report (saved to `/tmp/skill-audit-report-<date>.json`):

```json
{
  "scan_date": "2026-05-03T11:47:00Z",
  "hermes_agent": {
    "installed_version": "v0.12.0",
    "latest_version": "v0.12.0",
    "update_available": false
  },
  "git_tracked_skills": [
    {
      "name": "base",
      "source": "/root/skills/blockchain/base",
      "current_commit": "abc1234",
      "latest_commit": "def5678",
      "out_of_date": true,
      "new_commits": ["feat: add L2 gas optimization hints", "fix: RPC fallback logic"]
    }
  ],
  "local_skills": ["agent-voice-content", "defi-milestone-cron-operations"],
  "external_resources": [
    {
      "name": "chainlink-agent-skills",
      "url": "https://github.com/smartcontractkit/chainlink-agent-skills",
      "matching_domains": ["blockchain", "defi"],
      "section": "agentskills.io Ecosystem",
      "status": "new"
    }
  ],
  "vault_coupled": true,
  "vault_status": "behind_origin/main_by_16_commits",
  "recommendations": [
    "Sync vault from remote before next agent run",
    "Consider git-tracking local-only skills under /root/skills/<category>/"
  ]
}
```

---

## Automation & Scheduling

### Cron Job (Weekly, Mondays 09:00 UTC)

```bash
0 9 * * 1 cd /root && /usr/local/lib/hermes-agent/venv/bin/hermes run \
  --skill skill-audit-operations \
  --prompt "Run full skill audit and save report to /tmp/ with summary to Gentech Labs" \
  2>&1 | tee /tmp/skill-audit-$(date +\%Y\%m\%d).log
```

### Telegram Summary Format (Gentech Labs)

```
[Skill Audit - 2026-05-03]
✓ Hermes Agent: v0.12.0 (up to date)
⚠️  Git-tracked skills: 2 outdated (base, solana)
• Local-only skills: 55 (consider version control)
🔗 New external resources: 8 matches found
⚠️  Vault: 16 commits behind origin/main (uncommitted changes present)
See /tmp/skill-audit-20260503.json for full details.
```

---

## Pitfalls

### Pitfall: Skills appear "local" even though they're from a repo
**Cause:** Hermes skill discovery copies or symlinks skills into profile-specific home directories (`~/.hermes/profiles/<profile>/skills/`) which lose `.git` metadata.
**Fix:** The canonical source is the original install location. Track custom skill sources in a manifest file at `/root/skills/.custom_sources.yaml`:
```yaml
agent-voice-content:
  source: "git@github.com:gentech/skills-voice-content.git"
  category: "creative"
```

### Pitfall: GitHub API rate limits block raw README fetch
**Cause:** Too many requests to raw.githubusercontent.com (60/hr unauthenticated).
**Fix:** Cache README locally at `/root/skills/.awesome_hermes_cache.md` and only refresh once per day. Use `If-Modified-Since` header if available.

### Pitfall: Vault sync conflicts during audit
**Cause:** Memory backups or vault sync processes hold lockfiles (`.tick.lock`, `.lock`) causing git operations to fail.
**Fix:** Audit read-only; never write during scan. Skip locked paths. Use `git fetch --quiet` only; avoid `git pull`.

### Pitfall: Skill with multiple git remotes (origin vs upstream)
**Cause:** Forked skill repos may have both `origin` (personal fork) and `upstream` (original).
**Fix:** Audit against `origin/main` by default; if `upstream` exists and is ahead, flag for manual review. Never auto-sync across forks.

---

## Community Skill Promotion Workflow

When the audit identifies community skills (GitHub repos with SKILL.md files) for potential adoption, use this workflow:

### 1. Review Pending Skills
The vault `12-Skills/Skills-Tracker.md` maintains a categorized pending list with priority ratings (HIGH/MEDIUM/LOW).

### 2. Promotion Criteria
- **HIGH priority**: Recent commits (<30 days), high star count, directly relevant to agent tasks → Approve
- **MEDIUM priority**: Relevant but not urgent → Defer to agent-specific install sessions
- **LOW priority**: Tangential relevance → Skip unless specifically requested
- **Stale (>6 months)**: No commits → Drop from pending list

### 3. Execute Promotion
Update `12-Skills/Skills-Tracker.md`:
- Move approved skills from `🔲 Pending Review` to `✅ Installed` or mark as `APPROVED`
- Strikethrough the skill name to indicate action taken
- Move dropped skills to `❌ Dropped` section with reason and date

### 4. Agent-Specific Routing
Skills often target specific agents. Route installs accordingly:
- Security skills (krait, trailofbits) → DMOB
- DeFi skills (defi-skills, almanak-sdk) → YoYo/Strategies
- Content skills (OpenMontage, VoxCPM) → Desmond/Entertainment
- General skills → All agents

### 5. Update Audit Doc
Mark the consolidation audit as `completed` with an execution log listing what was approved, dropped, and deferred.

### Pitfalls
- Don't install skills directly — the audit marks them APPROVED, then agent-specific sessions do the actual `hermes skills install`
- Stale skill detection: check last commit date, not just star count. A 500-star repo with no commits in 12 months is dead
- The `immunefi-team/Web3-Security-Library` drop (13+ months stale) is the canonical example of a stale skill

---

## Coupling with Vault Operations

`skill-audit-operations` should run AFTER `vault-intelligence-recon` and BEFORE any skill install/update. Sequence:

1. `vault-intelligence-recon` → identify vault-resident skill artifacts
2. `skill-audit-operations` → assess version drift across all layers
3. `hermes skills update` (if updates available) → apply patches
4. `ob sync` → propagate updated skills to vault

**Checkpoint:** If vault is BEHIND remote, do NOT update skills until vault sync completes. Otherwise, local edits diverge.

---

## References

- [Hermes skill storage architecture](references/hermes-skill-storage.md) — where skills live, how they're discovered
- [Git skill update patterns](references/git-skill-update-patterns.md) — common failure modes and recovery
- [Awesome-list scanning cookbook](references/awesome-list-scanning.md) — reusable fetch/filter/score pattern
- [Vault coupling checklist](references/vault-skill-coupling.md) — manual sync steps when vault is out of date

---

## Revision History

- v1.0 — created 2026-05-03 after multi-layer skill audit discovery session
