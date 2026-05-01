---
name: codebase-assessment
description: "General-purpose repo assessment: clone, inspect codebase metrics, analyze architecture, assess project/hackathon fit, and write structured report to vault."
version: 1.0.0
author: DMOB
license: MIT
metadata:
  hermes:
    tags: [codebase, assessment, architecture, hackathon-fit, clone, audit]
    related_skills: [codebase-inspection, hackathon-prep-audit, github-repo-management]
prerequisites:
  commands: [git, pygount, grep, find]
---

# Codebase Assessment

End-to-end workflow for evaluating an arbitrary GitHub repo: clone, measure, analyze architecture, assess fit, and produce a structured assessment report in the vault. For blockchain-specific smart contract audits, see `hackathon-prep-audit`.

## When to Use

- Jordan says "check out this repo" or "look at X project"
- Evaluating a project for hackathon potential or integration
- Onboarding to an unfamiliar codebase
- Comparing multiple repos for a decision
- Any "clone and tell me what we've got" request

## Phase 1: Clone & Initial Survey

```bash
mkdir -p ~/repos && cd ~/repos
git clone https://github.com/ORG/repo-name.git
cd repo-name

# Quick structure survey
find . -maxdepth 2 -type f | head -60
find . -maxdepth 3 -type d | grep -v ".git" | sort
find . -name "*.py" | wc -l  # or .rs, .ts, etc.
```

Read the README immediately — it tells you what the project claims to be.

## Phase 2: Codebase Metrics

Use pygount for language breakdown:

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount

pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build" \
  .
```

Record: total files, language distribution, code lines, comment ratio.

## Phase 3: Architecture Analysis

Read key files to understand the architecture:

1. **Entry point** — `main.py`, `app.py`, `index.ts`, `lib.rs`, etc.
2. **Config** — `config.yml`, `.env.example`, `pyproject.toml`, `Cargo.toml`
3. **Core modules** — the main orchestration/logic files
4. **Dependencies** — `requirements.txt`, `package.json`, `Cargo.toml`
5. **Tests** — do they exist? What's the coverage like?

Build a mental model:
- What's the architecture pattern? (agent, pipeline, microservices, monolith)
- What are the key abstractions? (classes, traits, interfaces)
- How does data flow through the system?
- What external services/APIs does it depend on?

### Key Questions to Answer

| Question | Why It Matters |
|----------|---------------|
| What does this project actually do? | Core value proposition |
| What's the tech stack? | Compatibility with our setup |
| What are the dependencies? | heaviness, licensing, maintenance |
| Are there tests? | Quality signal |
| Is it actively maintained? | Commit frequency, issues |
| What API keys/services does it need? | Operational cost |
| What hardware does it require? | GPU, RAM, disk |
| What's the code quality? | Readability, patterns, docs |

## Phase 4: Functional Testing

Don't just read — **run it**. Verify the tool actually works before recommending it.

### Install & Smoke Test

```bash
# Python project
cd repo-name
pip install -e . --break-system-packages 2>/dev/null || pip install -e .

# Node project
npm install && npm run build

# Rust project
cargo build --release
```

Run the primary command / entry point. If it needs a service (Obsidian, Docker, etc.) that's unavailable, note it and test what you CAN test (CLI layer, library imports, unit tests).

### Test Suite

```bash
# Find and run tests
python -m pytest tests/ -v --tb=short 2>/dev/null || \
npm test 2>/dev/null || \
cargo test 2>/dev/null
```

Record: pass/fail count, any test failures (are they real bugs or environment issues?).

### Manual Exercise

Run the core operations yourself:

1. **Init/bootstrap** — does setup work cleanly?
2. **Primary CRUD** — create, read, update, delete the main entities
3. **Edge cases** — duplicates, missing inputs, empty states
4. **Integration** — does it talk to its dependencies? (API calls, file I/O, sync)
5. **Output quality** — is generated output correct and well-formatted?

Document any bugs found with severity:
- 🔴 **Critical** — crashes, data loss, security issues
- 🟡 **Medium** — broken features that have workarounds
- 🟢 **Low** — cosmetic, dead code, minor annoyances

### What If You Can't Run It?

Some tools need specific environments (desktop Obsidian, GPU, hardware). In that case:
1. Review the code for correctness instead (read the implementation, not just the API)
2. Check test coverage — are the untestable paths covered by tests?
3. Note what you CAN'T verify and why
4. Score confidence: how sure are you it works based on code review alone?

## Phase 5: Fit Assessment

Rate the project for the intended use case:

| Rating | Criteria |
|--------|----------|
| ⭐⭐⭐ | Directly aligns with our goals, fits our stack, low friction |
| ⭐⭐ | Partially fits, requires adaptation or has blockers |
| ⭐ | Tangential — only if spare bandwidth |

### Integration Analysis (Do This First)

Before rating, explicitly map integration with systems we've already built:

1. **Overlap scan** — Does any component duplicate what we have? (e.g., their TraderJoe connector vs. our `lp-position-reader.py`)
2. **Integration points** — APIs, data formats, protocols that connect to our stack (e.g., gRPC gateway, intent vocabulary, state management)
3. **Partial adoption** — Can we extract just one module instead of the whole framework? (Connector library, backtesting engine, etc.)
4. **Replacement candidates** — Does their code do what our scripts do, but better? Note specific files/classes.
5. **Overkill assessment** — What parts are designed for scale we don't need? (Multi-chain when we're single-chain, etc.)

Document this as a separate subsection under Fit Assessment. The best outcome is usually "use their connector, skip their framework."

### Blockers to Identify Early

- **Hardware gaps** — GPU required but we're CPU-only
- **Dependency bloat** — massive requirement chains
- **API cost** — multiple paid APIs needed
- **Language barriers** — non-English codebase/comments
- **No tests** — risky to build on
- **License issues** — GPL in a commercial context

## Phase 6: Report to Vault

Write assessment to `02-Labs/Assessment-[ProjectName]-[Date].md`:

```markdown
---
title: "Codebase Assessment — [Org] [Project]"
date: YYYY-MM-DD
type: assessment
tags: [relevant, tags]
status: ready
---

# Codebase Assessment: [Project] ([Org])
**Repo:** https://github.com/ORG/repo
**License:** X | **Stars:** N | **Language:** Y

## Overview
[One paragraph — what it is and what it does]

## Codebase Metrics
| Metric | Value |
|--------|-------|
| Files | N |
| Lines of code | N |
| Comment ratio | N% |

## Architecture
[Directory tree + description of key components]

## How It Works
[Numbered flow — what happens when you run it]

## Dependencies
[Key dependencies and their purposes]

## API Keys Required
| Provider | Purpose |
|----------|---------|
| ... | ... |

## Setup Requirements
[Exact commands to get it running]

## Functional Testing ✅/❌
[What you tested, what worked, what didn't. Include test suite results.]

| Test | Result |
|------|--------|
| Installation | ✅/❌ |
| Test suite (N/N pass) | ✅/❌ |
| Core operations | ✅/❌ |
| Integration/sync | ✅/❌ |

### Bugs Found
[Severity + description of any bugs discovered during testing]

## Strengths ✅
[What's good about it]

## Concerns / Questions ⚠️
[What's risky, missing, or unclear]

## Fit Assessment
**Rating: ⭐⭐⭐ (N/5)**
[Why it does/doesn't fit the intended use case]

## Potential Use Cases
[How we could actually use this]

## Next Steps
[Concrete action items]
```

## Phase 7: Sync & Report

```bash
cd /root/vaults/gentech && ob sync
```

Report summary back to Jordan with the key findings and recommendation.

## Pitfalls

1. **Don't skip the README** — it often contains setup gotchas and architecture diagrams that save you hours.
2. **Check actual file sizes** — `find . -name "*.py" | wc -l` can be misleading if there are vendored dependencies. Look at the top-level structure first.
3. **Read config.yml/.env.example early** — reveals API dependencies and required services before you waste installing.
4. **Don't install everything blindly** — some repos have massive dependency trees. Survey first, install only what's needed for assessment.
5. **Check for tests directory** — `find . -name "test*" -o -name "*_test*" | head -20`. No tests = higher risk.
6. **License matters** — always check LICENSE file. MIT/Apache = safe. GPL = complications.
7. **Comment language** — non-English comments aren't a blocker but note it in assessment.
8. **Separate assessment from audit** — this skill is for understanding what a repo IS and whether it WORKS. Security audits (reentrancy, vulnerabilities) belong in `hackathon-prep-audit` for blockchain or a dedicated security audit skill.
9. **Don't skip functional testing** — reading code is not the same as running it. A repo can look perfect and fail on `pip install`. Always try to install and exercise the core path, even if you can't test everything.
10. **Note what you CAN'T test** — if the tool needs a desktop app, GPU, or specific hardware, say so explicitly. Don't leave the reader wondering if you tested the integration or just the CLI.
11. **Pester the `demo` command** — demo/seed commands often have bugs because they're less exercised. Test them first.
