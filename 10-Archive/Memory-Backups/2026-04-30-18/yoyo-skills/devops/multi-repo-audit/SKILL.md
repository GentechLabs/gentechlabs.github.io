---
name: multi-repo-audit
description: Audit an entire GitHub org or personal account — clone all repos, install missing dev tools, deep-inspect each project (build, test, coverage, security), cross-reference with vault context, identify duplicates/stale repos, and produce a prioritized gap analysis report.
version: 1.0.0
author: YoYo (Strategies)
metadata:
  hermes:
    tags: [audit, github, repos, codebase, security, devtools, foundry, infrastructure]
    related_skills: [github-repo-management, codebase-inspection, github-auth]
---

# Multi-Repo Codebase Audit

Full-spectrum audit of all repos in a GitHub org or personal account. Designed for "get me familiar with everything we've built" situations.

## When to Use

- User says "look at all our repos", "audit the codebase", "get familiar with what we have"
- New agent onboarding to understand the full project landscape
- Pre-hackathon inventory to find what's reusable
- Post-sprint cleanup to identify stale/duplicate repos
- "Check the brain for context" — cross-reference code with vault specs/ideas

## Prerequisites

```bash
# Required tools (install if missing)
command -v gh || echo "Install gh CLI"
command -v git
command -v forge || echo "Install Foundry: curl -L https://foundry.paradigm.xyz | bash && foundryup"
command -v python3
command -v node
```

## Workflow

### Phase 1: Discovery (5 min)

```bash
# List all repos in org
gh repo list <ORG> --limit 50

# List all repos for personal account
gh repo list <USERNAME> --limit 50

# Check auth status
gh auth status
```

**Capture:** repo name, visibility (public/private), description, last updated, language.

### Phase 2: Install Missing Tools (10 min)

Detect what each project needs:

```bash
# Solidity projects
command -v forge || (curl -L https://foundry.paradigm.xyz | bash && foundryup)

# Solana/Anchor projects
command -v anchor || echo "Need anchor-cli"
command -v solana || echo "Need solana-cli"

# Rust projects
command -v cargo

# Node.js projects
command -v node && command -v npm

# Python projects
command -v python3 && command -v pip3
```

### Phase 3: Clone All Repos (10 min)

```bash
mkdir -p ~/repos && cd ~/repos
# Clone with --depth 1 for speed (we're auditing, not modifying)
gh repo clone <owner>/<repo> -- --depth 1
```

**Parallelize:** Clone in a single batch command, not one-by-one.

### Phase 4: Deep Audit Each Repo (parallel subagents)

Delegate to 2-3 parallel subagents. Each subagent audits a batch of repos:

**For Solidity repos:**
```bash
cd ~/repos/<repo>
forge build 2>&1          # Does it compile?
forge test 2>&1           # Do tests pass?
grep -rn "TODO\|FIXME\|HACK" src/ 2>/dev/null  # Technical debt
grep -rn "console.log\|emit" src/ 2>/dev/null  # Debug artifacts
```

**For all repos:**
```bash
# File inventory
find . -name "*.sol" -o -name "*.rs" -o -name "*.py" -o -name "*.ts" | grep -v node_modules | grep -v lib/

# README quality
cat README.md | wc -l     # Is there even a README?

# Git hygiene
git log --oneline -5      # How active?
ls .gitmodules 2>/dev/null  # Submodules present?
```

**Per-repo audit checklist:**
- [ ] Build: Does it compile/build?
- [ ] Tests: How many? Pass rate?
- [ ] Coverage: Real tests or placeholders?
- [ ] Security: TODO/FIXME/HACK comments? Known vuln patterns?
- [ ] Docs: README quality? Referenced files exist?
- [ ] Deployment: Deploy scripts present?
- [ ] CI/CD: GitHub Actions configured?
- [ ] Status: Active/stub/superseded/abandoned?

### Phase 5: Cross-Reference with Vault Context (5 min)

```bash
# Check vault for related specs, ideas, handoffs
# Look in: 03-Strategies/, 07-Ideas/, 09-Green Room/, 11-Mess Hall/
```

Match repos to:
- Active specs (what was planned vs what was built)
- Brainstormed ideas (what's been discussed but not started)
- Handoffs between agents (what's in flight)
- Hackathon requirements (what's needed for submissions)

### Phase 6: Identify Overlaps & Gaps (5 min)

Build a relationship map:
```
repo-A ──superseded──→ repo-B
repo-C ───folded────→ repo-D
repo-E ──never built→ (doesn't exist)
```

### Phase 7: Compile Report (10 min)

Save to vault with this structure:

```markdown
# Codebase Audit — [DATE]

## Dev Tools Status
| Tool | Status |

## Repo Inventory
| Repo | Status | Contracts/Files | Tests | Verdict |

## Deep Dive — Core Projects
### [Project Name]
- Tech stack
- Contracts/files count
- Test pass rate
- Security patterns
- Assessment

## Duplicate/Overlap Map
[Visual relationship diagram]

## Brain Context
[Cross-reference with vault specs/ideas]

## Critical Gaps
[Prioritized list: P0/P1/P2]

## Recommendations
[Immediate / Medium-term / Strategic]
```

## Pitfalls

1. **Always use `--depth 1` for cloning** — we're auditing, not forking. Saves time and disk.
2. **Check for placeholder tests** — `assert!(true)` or `assert(true)` counts as 0% coverage.
3. **Verify referenced files exist** — READMEs often reference `docs/`, `script/`, `frontend/` that don't exist in the repo.
4. **Distinguish "not built" from "built and deleted"** — GitHub repos may exist but have no local clone.
5. **Cross-reference before concluding** — the vault often has specs that show what was *planned* vs what was *built*. The gap is the actionable finding.
6. **Delegate parallel audits** — use subagents for 2-3 batches of repos to speed up the process significantly.
