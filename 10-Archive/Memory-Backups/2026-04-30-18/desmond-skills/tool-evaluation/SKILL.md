---
name: tool-evaluation
description: "Evaluate third-party Python CLI/SDK tools before adoption: install in isolated venv, functional-test all commands, find and fix bugs, run test suite, produce structured evaluation report. Use when testing a new dependency, library, or CLI tool for potential integration."
version: 1.0.0
category: software-development
tags: [evaluation, testing, python, cli, tooling, qa]
triggers:
  - "test this tool"
  - "evaluate this dependency"
  - "try this CLI"
  - "should we adopt this library"
  - "install and test"
---

# Tool Evaluation

Systematic workflow for evaluating third-party Python CLI/SDK tools before adoption.

## When to Activate

- User asks to "test", "try", "evaluate", or "check out" a tool/library/CLI
- Assessing whether to adopt a new dependency
- Comparing tools for a specific use case
- User shares a GitHub repo and asks "does this work?"

## Workflow

### Phase 1 — Reconnaissance
1. Read README, pyproject.toml/setup.py, and EXECUTION.md if present
2. Identify components (CLI, SDK, plugin, server) and what's testable standalone
3. Check: Python version requirements, dependencies, license, last update date
4. Determine if it needs external services (Obsidian, Docker, API keys) or works offline

### Phase 2 — Setup
1. Clone to `/tmp/<tool-name>` (temporary, disposable)
2. Create venv: `python3 -m venv /tmp/<tool-name>-env`
3. Install: `source /tmp/<tool-name>-env/bin/activate && pip install -e .`
4. If pyproject.toml is in subdirectory, install from root with `package-dir` config
5. Note: system Python is externally-managed (PEP 668) — always use venv

### Phase 3 — Functional Testing
1. Run `--help` to see available commands
2. Test each command with realistic inputs
3. Test edge cases: empty inputs, missing files, invalid arguments
4. Test integration points: file I/O, network calls, database operations
5. Capture output (both stdout and stderr) for each test

### Phase 4 — Bug Finding
1. Run the existing test suite: `python -m pytest tests/ -v --tb=short`
2. Note failures — read the test to understand expected vs actual behavior
3. For each failure: identify root cause in source, check if it's a real bug or test issue
4. Fix real bugs in-place (patch the source)
5. Re-run tests to confirm fix doesn't break other tests

### Phase 5 — Code Quality Check
1. Review core modules for: error handling, edge cases, security concerns
2. Check for hardcoded paths, missing input validation, resource leaks
3. Note architecture: is the code well-structured? Extensible? Testable?

### Phase 6 — Report
Produce structured report covering:
- **What it is**: One-line description + stars/language/license
- **Architecture**: How it works, key components
- **Test results**: X/Y tests pass, what was tested
- **Bugs found**: Description + fix applied
- **Limitations**: What it can't do, missing features
- **Verdict**: Adopt / Adopt with fixes / Skip

## Pitfalls

- **PEP 668**: Modern Debian/Ubuntu system Python is externally-managed. Always use venv.
- **pyproject.toml location**: May be in root or subdirectory. Check before `pip install -e .`
- **Interactive prompts**: Some commands (archive, delete) require confirmation. Pipe `echo "y"` or use `--yes`/`--force` flags.
- **Variable scoping bugs**: Python closures in loops can cause `UnboundLocalError`. Check if variables are assigned in conditional branches before use.
- **Hardcoded query filters**: SQL queries may have hardcoded exclusions (e.g., `WHERE status NOT IN ('archived')`) that prevent certain filter combinations from working. Check base queries when flags seem broken.

## Phase 7 — Adoption (after verdict = Adopt)

If the tool passes evaluation, these steps make it part of the workflow:

1. **Install to persistent venv**: `python3 -m venv /root/.venvs/<tool-name>` (not /tmp/)
2. **Create wrapper script** at `/usr/local/bin/<short-name>`:
   ```bash
   #!/bin/bash
   source /root/.venvs/<tool-name>/bin/activate
   export KANBAN_DB_PATH="/root/.hermes/<tool>.db"  # if tool uses default paths
   exec <tool-cli> "$@"
   ```
   This gives a clean command name and handles env vars/paths the tool expects.
3. **Initialize with real data** — seed the tool with actual projects/tasks from the vault
4. **Sync to vault** — if the tool outputs files (markdown, reports), sync to the vault
5. **Update memory** — save tool location, wrapper name, DB path, and any quirks

## Verification

After evaluation, confirm:
1. All tests pass (after fixes)
2. Core functionality works end-to-end
3. No critical security issues found
4. Report delivered with clear adopt/skip recommendation
