# Agent Kit v2 — Smart Skill Selection Architecture

**Philosophy:** "Eat the meat, spit out the bones."
**Inspired by:** Claude Design Skillstack marketplace pattern
**Adapted for:** Hermes Agent skill system

---

## The Problem

Installing 50+ skills bloats the context window. Most agents use 10-15 skills regularly. The rest sit idle, wasting tokens on every turn.

## The Solution: Lazy-Load + Auto-Activate

Instead of installing everything upfront, skills are **registered** but not **loaded** until triggered. The agent detects what's needed and pulls the right skill at the right time.

---

## Skill Structure (Borrowed from Claude Design Skillstack)

```
skill-name/
├── SKILL.md              # YAML frontmatter + instructions
├── triggers.yaml         # When to auto-activate (keywords, tasks, patterns)
├── references/           # API docs, guides
├── scripts/              # Automation utilities
└── assets/               # Templates, examples
```

### SKILL.md Frontmatter

```yaml
---
name: defi-lp-monitoring
description: Automated LP position tracking with Aleph Zero integration
category: defi
tags: [lp, monitoring, aleph-zero, yield]
triggers:
  keywords: [lp, liquidity, position, yield, apr, aleph]
  tasks: [check position, monitor lp, rebalance, harvest]
  files: [defi-data.json, lp-monitor.*]
  chains: [aleph-zero, base, avalanche]
priority: high  # high = always loaded, medium = loaded on trigger, low = manual only
---
```

### triggers.yaml (Detailed Activation Rules)

```yaml
# When should this skill auto-activate?
activation:
  # Keyword match in user message
  keywords:
    - lp
    - liquidity position
    - yield farming
    - rebalance
    
  # Task pattern match
  tasks:
    - pattern: "check.*position"
    - pattern: "monitor.*lp"
    - pattern: "harvest.*reward"
    
  # File presence in working directory
  files:
    - defi-data.json
    - lp-monitor.*
    
  # Chain context
  chains:
    - aleph-zero
    - base
    
  # Time-based (for cron jobs)
  schedule:
    - "*/10 11-23 * * *"  # During trading hours

# When should this skill NOT activate?
deactivation:
  keywords: [solidity, rust, marketing]
  tasks: [deploy contract, write content]
```

---

## Category Bundles (Install Once, Use Selectively)

Instead of installing individual skills, install bundles:

| Bundle | Skills | When to Load |
|--------|--------|-------------|
| **core** | identity, wake-up, memory, context, routing | ALWAYS loaded |
| **defi** | lp-monitoring, portfolio-sync, yield-farming, compound-extract | On DeFi tasks |
| **content** | social-drafts, media-gen, scheduling | On content tasks |
| **security** | agent-rug, contract-verify, drain-detect | On security tasks |
| **hackathon** | submission-prep, demo-recording, pitch-deck | On hackathon tasks |
| **career** | job-scan, resume-tailor, interview-prep | On career tasks |

### Bundle Manifest

```json
{
  "name": "defi",
  "description": "DeFi operations bundle — LP monitoring, portfolio sync, yield optimization",
  "skills": [
    "defi-lp-monitoring",
    "defi-portfolio-sync", 
    "defi-yield-farming",
    "defi-compound-extract"
  ],
  "auto_activate": {
    "when": "user mentions defi, lp, yield, portfolio, trading",
    "load": "all",
    "cache": "30m"
  },
  "context_budget": {
    "max_tokens": 4000,
    "priority": "high"
  }
}
```

---

## Smart Selection Engine

### How It Works

1. **User sends message** → Agent scans for triggers
2. **Trigger match** → Agent loads relevant skill(s) from bundle
3. **Skill loaded** → Agent follows SKILL.md instructions
4. **Task complete** → Skill stays cached for 30 min (configurable)
5. **No match** → Agent uses core skills only

### Selection Priority

```
1. Explicit skill request ("use the defi skill")
2. Keyword match from triggers.yaml
3. Task pattern match
4. File presence match
5. Chain context match
6. Time-based schedule match
```

### Context Budget Management

Each skill declares its token budget. The agent enforces:

```
Total context = core (always) + loaded skills (on-demand)
Max total = 8,000 tokens (configurable)
If over budget → unload lowest-priority cached skill
```

---

## Marketplace Structure

### Registry File

```json
{
  "marketplace": "gentech-agent-kit",
  "version": "2.0.0",
  "bundles": [
    {
      "name": "core",
      "version": "2.0.0",
      "skills": ["identity", "wake-up", "memory", "context", "routing"],
      "required": true
    },
    {
      "name": "defi",
      "version": "1.0.0",
      "skills": ["defi-lp-monitoring", "defi-portfolio-sync"],
      "required": false
    }
  ],
  "install_command": "agent-kit install <bundle>",
  "list_command": "agent-kit list",
  "search_command": "agent-kit search <query>"
}
```

### Install Flow

```bash
# Install core (always needed)
agent-kit install core

# Install DeFi bundle
agent-kit install defi

# Install specific skill
agent-kit install defi-lp-monitoring

# List installed
agent-kit list

# Search available
agent-kit search "liquidity"
```

---

## Key Differences from Claude Design Skillstack

| Claude Design Skillstack | Agent Kit v2 |
|--------------------------|-------------|
| All plugins loaded at start | Lazy-load on trigger |
| Manual slash commands | Auto-activation from triggers.yaml |
| Fixed plugin list | Dynamic bundle composition |
| No context budget | Token budget enforcement |
| Claude Code only | Hermes Agent (any provider) |
| No chain awareness | Chain-aware triggers |

---

## Migration Path

### Phase 1: Audit Current Skills
- List all installed Hermes skills
- Tag each with category + triggers
- Identify unused skills (remove or deprioritize)

### Phase 2: Bundle Creation
- Group skills into bundles (core, defi, content, security, etc.)
- Write triggers.yaml for each skill
- Set context budgets

### Phase 3: Smart Selection Engine
- Build trigger scanner
- Implement lazy loader
- Add context budget manager

### Phase 4: Marketplace
- Create registry file
- Build install/search/list CLI
- Publish to GitHub

---

## Example: Agent Kit in Action

**User says:** "Check my LP position on Aleph Zero"

**Agent does:**
1. Scans message → triggers: "lp", "position", "aleph-zero"
2. Matches bundle: `defi`
3. Loads skill: `defi-lp-monitoring`
4. Follows SKILL.md instructions
5. Returns position data
6. Caches skill for 30 min

**Context used:** ~1,200 tokens (not 8,000)

**User says:** "Write a tweet about it"

**Agent does:**
1. Scans message → triggers: "tweet", "content"
2. Matches bundle: `content`
3. Loads skill: `social-content`
4. Follows SKILL.md instructions
5. Returns draft tweet

**Context used:** ~800 tokens (LP skill already cached)

---

## Summary

**Old way:** Install 50 skills, load all 50 every turn, waste tokens.
**New way:** Install bundles, load on trigger, cache temporarily, enforce budget.

**Result:** Faster responses, lower costs, cleaner context.

This is the "eat the meat, spit out the bones" approach — only load what you need, when you need it.
