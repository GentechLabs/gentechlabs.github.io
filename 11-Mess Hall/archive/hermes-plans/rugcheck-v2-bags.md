# Rugcheck v2 — Bags.fm Build Plan

**Created:** 2026-05-23
**Repo:** github.com/ProtoJay4789/rugcheck
**Workdir:** /tmp/rugcheck-bags

## Task 1: Repo Rebrand + Structure
- Update README for Bags v2
- Remove Sui-specific code (Move contracts, sui_client.py)
- Create new directory structure: `agent/`, `agent/scanners/`, `agent/dashboard/`
- Keep: scoring engine, alerts, tests (adapt as needed)
- Files: `README.md`, `.gitignore`, directory cleanup
- Verify: `ls -la` shows clean structure

## Task 2: Bags API Client
- Create `agent/scanners/bags_client.py`
- REST client for Bags API (scout mode, token info, launch feed)
- Simulate mode with realistic mock data (like v1's simulate_goplus)
- Methods: `get_new_launches()`, `get_token_info(mint)`, `get_token_fees(mint)`
- Files: `agent/scanners/bags_client.py`, `agent/scanners/__init__.py`
- Verify: unit tests pass with mock data

## Task 3: Risk Scoring Engine (Solana Port)
- Adapt `agent/monitor.py` → `agent/scorer.py`
- Replace GoPlus factors with Solana-specific factors (mint_authority, freeze_authority, lp_locked, concentration)
- Keep weighted scoring logic (it's chain-agnostic)
- Add Bags-specific metadata (launch time, creator, fee structure)
- Files: `agent/scorer.py`, `agent/risk_factors.py`
- Verify: unit tests for all scoring paths

## Task 4: Agent Loop
- Create `agent/agent.py` — main autonomous loop
- Cycle: scout new launches → fetch metadata → score → store → alert if risky
- Configurable interval (default: 60s between scans)
- Graceful shutdown, logging
- Files: `agent/agent.py`, `agent/config.py`
- Verify: dry-run with simulated data completes one full cycle

## Task 5: Dashboard
- Single HTML file: `agent/dashboard/index.html`
- Live feed of scanned tokens (polls from JSON file)
- Risk score color coding (green/yellow/orange/red)
- Token details on click
- Dark theme, mobile responsive (match AAE style)
- Files: `agent/dashboard/index.html`
- Verify: opens in browser, shows mock data

## Task 6: Tests
- Unit tests for scorer, bags_client, agent loop
- Integration test: full pipeline with mock Bags API
- Target: 40+ tests passing
- Files: `agent/tests/test_scorer.py`, `agent/tests/test_bags_client.py`, `agent/tests/test_agent.py`
- Verify: `pytest` all green

## Task 7: README + Submission Docs
- README: what it does, how to run, architecture diagram
- Demo script (step-by-step for recording)
- Submission writeup for DoraHacks
- Files: `README.md`, `docs/demo-script.md`, `docs/submission.md`
- Verify: README renders clean on GitHub

## Parallelization

- Tasks 1-2 sequential (structure → client)
- Tasks 3-4 sequential (scorer → agent loop uses scorer)
- Task 5 parallel with 3-4 (dashboard is independent)
- Task 6 after 3+4 (tests need scorer + agent)
- Task 7 after all (docs reflect final state)

## Estimated Time
- Subagent build: ~10-15 minutes
- Review + fix: ~5 minutes
- Total: ~20 minutes
