---
name: multi-repo-audit
description: "Full multi-repo codebase audit: verify tools, discover repos, analyze structure, run tests, produce structured report."
version: 1.0.0
author: Gentech
license: MIT
metadata:
  hermes:
    tags: [GitHub, Audit, Codebase, Testing, Sprint-Onboarding, Hackathon]
    related_skills: [codebase-inspection, github-repo-management, github-auth]
---

# Multi-Repo Codebase Audit

Comprehensive audit across multiple GitHub repositories. Use when onboarding after system issues, starting a new sprint/hackathon cycle, or doing pre-submission review.

## When to Use

- Starting a new development sprint or hackathon cycle
- Onboarding after system reinstall or major config change
- Pre-submission codebase review before hackathon deadline
- User says "audit the repos" or "get familiar with the codebase"
- User wants to know the state of all project code

## Prerequisites

- GitHub auth configured (see `github-auth` skill)
- `gh` CLI available and authenticated
- `jq` for JSON parsing

## Workflow

### Phase 1: Verify Dev Tools (2 min)

Check all critical tools are installed and working:

```bash
# Check core tools
echo "git: $(git --version 2>/dev/null || echo 'NOT INSTALLED')"
echo "gh: $(gh --version 2>/dev/null | head -1 || echo 'NOT INSTALLED')"
echo "node: $(node --version 2>/dev/null || echo 'NOT INSTALLED')"
echo "python3: $(python3 --version 2>/dev/null || echo 'NOT INSTALLED')"
echo "forge: $(forge --version 2>/dev/null | head -1 || echo 'NOT INSTALLED')"
echo "cargo: $(cargo --version 2>/dev/null || echo 'NOT INSTALLED')"
echo "docker: $(docker --version 2>/dev/null || echo 'NOT INSTALLED')"
echo "jq: $(jq --version 2>/dev/null || echo 'NOT INSTALLED')"

# Check GitHub auth
gh auth status 2>&1

# Set up git config if missing
git config --global user.name || echo "NEEDS SETUP"
git config --global user.email || echo "NEEDS SETUP"
```

Install any missing tools immediately:

```bash
# Foundry (Solidity/Anchor projects)
curl -L https://foundry.paradigm.xyz | bash && source ~/.bashrc && foundryup

# Set git config if missing (required for commits)
git config --global user.name "<username>"
git config --global user.email "<email>"
git config --global credential.helper store
```

### Phase 2: Discover Repos (3 min)

List all repos across personal and org accounts:

```bash
# Personal repos
gh repo list <username> --limit 50 --json name,description,updatedAt,isPrivate,primaryLanguage,url

# Org repos
gh repo list <org> --limit 50 --json name,description,updatedAt,isPrivate,primaryLanguage,url
```

Filter for active repos (updated in last 30 days) and note:
- Which are hackathon-specific vs infrastructure
- Which are private vs public
- Primary language for each

### Phase 3: Clone & Analyze (10-15 min)

Create workspace and clone all active repos:

```bash
mkdir -p /root/workspace && cd /root/workspace
```

For each repo, analyze:

```bash
# File structure (excluding .git, node_modules, lib)
find <repo> -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/lib/*' | sort

# Language breakdown
cd <repo> && find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10

# Check key files
test -f <repo>/README.md && echo "README: ✅" || echo "README: ❌"
test -f <repo>/foundry.toml && echo "Foundry: ✅" || echo "Foundry: ❌"
test -f <repo>/package.json && echo "Package: ✅" || echo "Package: ❌"

# Count test files
find <repo> -type f -name '*.t.sol' -o -name '*.test.*' -o -name '*_test.*' -o -name 'test_*' | grep -v .git | wc -l

# LOC by language
find . -type f -not -path '*/.git/*' -not -path '*/lib/*' -name '*.sol' -exec cat {} + 2>/dev/null | wc -l
find . -type f -not -path '*/.git/*' -not -path '*/lib/*' -name '*.py' -exec cat {} + 2>/dev/null | wc -l
```

### Phase 4: Run Tests (5-10 min)

Execute test suites for all repos:

```bash
# Foundry repos
cd <repo> && forge test -vvv 2>&1 | tail -20

# Python repos
cd <repo> && python -m pytest -v 2>&1 | tail -20

# Node repos
cd <repo> && npm test 2>&1 | tail -20
```

Record: pass/fail count, any warnings, gas usage for Solidity.

### Phase 5: Gather Context (5 min)

Check vault/project docs for:
- Sprint goals and deadlines
- Architecture decisions
- Pending approvals
- Related strategies or specs

### Phase 6: Produce Report (5 min)

Write structured audit report to vault:

```markdown
# Codebase Audit — [Date]

## Dev Tools Status
| Tool | Status | Version |

## Repository Summary
| Repo | Tests | LOC | Status |

## Test Results
| Repo | Tests | Status |

## Gaps & Recommendations
### Critical (Before Deadline)
### High Priority
### Medium Priority

## What's Working Well
```

Update any stale project documents (e.g., HACKATHON-TODO.md).

## Pitfalls

1. **Private repos need `gh` auth** — plain `git clone` will fail on private repos. Use `gh repo clone` instead.
2. **Exclude `lib/` and `node_modules/`** from file counts — they inflate LOC and file numbers.
3. **Foundry repos share deps** — `lib/` contains OpenZeppelin etc. Don't count those lines as project code.
4. **Solidity LOC can be misleading** — a 74K LOC repo might only have 500 lines of actual project code (rest is deps).
5. **Set git config before cloning** — commits will fail without user.name/user.email.
6. **Check for empty repos** — some repos may have been created but never populated.
7. **Batch analysis with execute_code** — Use `execute_code` with `terminal` from `hermes_tools` for iterating across repos programmatically (e.g., running tests on all repos in a loop).
8. **Stale HACKATHON-TODO.md** — After audit, always reconcile HACKATHON-TODO.md with current roster. Dead hackathons (withdrawn, skipped) should be removed from the active list.

## Output Format

The audit produces a vault document at `00-HQ/Summaries/YYYY-MM-DD-Codebase-Audit.md` and updates the todo list for the next sprint.

## Example Triggers

- "Audit all our repos"
- "Get familiar with the codebase"
- "What's the state of our code?"
- "We just reinstalled — what do we have?"
- "Sprint starts today — what needs work?"
