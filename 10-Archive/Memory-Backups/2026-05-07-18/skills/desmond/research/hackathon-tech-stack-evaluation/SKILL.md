---
name: hackathon-tech-stack-evaluation
description: "Evaluate a hackathon's required or featured tech stack for fit against current projects. Research platform docs, templates, and requirements, then produce a structured scope document with comparison and decision points."
tags:
  - hackathon
  - tech-stack
  - evaluation
  - scope
  - platform-assessment
  - gcp
  - solana
  - ai-agents
triggers:
  - Jordan shares a hackathon platform/toolkit link for scoping
  - Need to evaluate whether a hackathon's tech requirements fit current projects
  - Researching a hackathon's starter pack, SDK, or framework
  - Comparing hackathon tech stack against existing codebase
  - Writing a scope document for hackathon fit assessment
  - Assessing whether to pivot or run parallel for a hackathon
---

# Hackathon Tech Stack Evaluation

Evaluate a specific hackathon's required/recommended tech stack and assess fit against current projects. Produces a structured scope document for decision-making.

## When to Use

- Jordan shares a hackathon link and says "scope this"
- A hackathon requires specific frameworks, SDKs, or platforms
- Need to decide between pivoting current work vs. running parallel
- Assessing team readiness for a new tech stack

## Research Steps

### 1. Identify the Tech Stack
- What platform/framework does the hackathon require or recommend?
- Is there a GitHub repo? Docs site? Starter pack?
- What's the maturity level? (actively maintained, maintenance mode, new)

### 2. Deep-Dive Research
- **GitHub repo**: Stars, forks, recent commits, open issues, version
- **Docs site**: Templates available, setup requirements, deployment targets
- **PyPI/npm**: Package name, version, install command
- **Success stories**: Community showcase, past winners
- **Video walkthroughs**: YouTube tutorials, conference talks

### 3. Catalog Available Templates/Patterns
- List each template with framework, use case, and complexity
- Note which ones align with the hackathon's requirements
- Identify any MCP, A2A, or specific protocol requirements

### 4. Map Requirements vs. Current Stack
- What does the hackathon mandate? (e.g., "must integrate ≥1 MCP server")
- What does our current project use? (e.g., Solana, custom agent framework)
- Where are the gaps? (new language, new cloud provider, new paradigm)

### 5. Assess Team Fit
- Team expertise with the new stack
- Time to learn vs. time to build
- Deployment complexity (cloud-managed vs. self-hosted)

## Scope Document Template

```markdown
# 🔍 [Platform Name] — Hackathon Scope
**Date:** [date]
**Hackathon:** [name]
**Deadline:** [date] | **Prize:** [amount or TBD]

---

## What Is [Platform]?
[1-2 paragraph overview with repo stars, PyPI version, docs URL]

## Available [Templates/Components]
| Name | Framework | Use Case | Complexity |
|------|-----------|----------|------------|
| ... | ... | ... | Low/Med/High |

## Key Features (What You Get For Free)
1. [Feature] — [one-liner]
2. ...

## Setup Requirements
- [List prerequisites]

## 🚨 Critical Notes
[Active development vs. maintenance mode, migration paths, lock-in risks]

## Hackathon Fit Analysis
### ✅ Strengths for This Hackathon
- [List]

### ⚠️ Concerns
- [List]

### 🎯 Recommended Approach
1. [Step-by-step recommendation]

## vs. [Current Stack] (Current Focus)
| Factor | New Stack | Current Stack |
|--------|-----------|---------------|
| Prize | ... | ... |
| Deadline | ... | ... |
| Chain/Platform | ... | ... |
| Agent Framework | ... | ... |
| Our Expertise | Low/Med/High | Low/Med/High |
| Production Infra | Built-in / Self-managed | ... |

## Decision Points
1. [Key decision with options]
2. ...

## Next Steps
- [ ] [Actionable items]
```

## Research Workflows

### GitHub Repo Analysis
```bash
# Get repo stats
curl -s "https://api.github.com/repos/OWNER/REPO" | jq '{stars: .stargazers_count, forks: .forks_count, language: .language, updated: .updated_at}'

# Get recent commits
curl -s "https://api.github.com/repos/OWNER/REPO/commits?per_page=5" | jq '.[].commit.message'

# Check PyPI version
curl -s "https://pypi.org/pypi/PACKAGE/json" | jq '.info.version'
```

### Docs Site Scraping
- Navigate to docs site, extract sidebar navigation
- Find template/agent/component listing pages
- Get setup/installation instructions
- Look for video walkthroughs and community showcases

### Comparison Matrix
Always compare across these dimensions:
- **Prize**: Absolute value and our odds
- **Deadline**: Time until submission, conflicts with other deadlines
- **Tech fit**: How much new learning is required
- **Reuse**: What existing code/concepts can carry over
- **Deployment**: How hard is it to demo (built-in infra vs. self-managed)

## Known Pitfalls

- **Maintenance mode traps** — A "successor" tool may be announced mid-hackathon; check repo status
- **GCP lock-in** — Google Cloud templates assume GCP; evaluate portability
- **Rules not yet published** — Some hackathons announce platform early but rules later (e.g., May 5); don't commit before rules drop
- **Solana vs. EVM vs. GCP** — Different ecosystems, different mental models; team may struggle context-switching
- **Demo vs. production** — Starter packs optimize for demo speed, not production scale; judges may notice
- **Parallel = diluted** — Running two hackathons simultaneously splits focus; recommend clear priority

## Related Skills

- `crypto-hackathon-bounty-scout` — Finding hackathons (this skill evaluates specific ones)
- `defi-dashboard-digest` — Similar "scan multiple sources, produce structured report" pattern
