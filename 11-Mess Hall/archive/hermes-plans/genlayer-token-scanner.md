# GenLayer Token Scanner — Build Plan

**Date:** 2026-05-23
**Status:** 🟢 In Progress
**Repo:** github.com/ProtoJay4789/genlayer-token-scanner (new)

## Problem
GenLayer needs real-world Intelligent Contract examples. We have rugcheck code that scans tokens for risk factors — repackaging it as a GenLayer contract demonstrates off-chain data reading + on-chain risk assessment.

## Architecture
Single GenLayer Intelligent Contract that:
1. Accepts a token contract address
2. Fetches security data from GoPlus API (web access — no oracle needed)
3. Calculates risk score using weighted factor analysis
4. Returns structured risk assessment

## Tasks

### Task 1: Project Scaffold
- Create project directory structure
- Write `requirements.txt` (genlayer deps)
- Write `README.md` with setup + usage
- Files: `genlayer-token-scanner/`

### Task 2: Token Scanner Contract
- Python class-based GenLayer Intelligent Contract
- `@contract` decorator, `__init__` with state
- `scan_token(address)` method — fetches GoPlus data, calculates score
- Risk weights ported from rugcheck (11 factors)
- Risk thresholds: LOW/MEDIUM/HIGH/CRITICAL
- Return structured result dict
- Files: `contracts/token_scanner.py`

### Task 3: Tests
- pytest tests for risk scoring engine
- Test all 4 risk scenarios (safe/suspicious/dangerous/mixed)
- Test edge cases (missing data, invalid address)
- Files: `tests/test_scanner.py`

### Task 4: Deploy Script + Demo
- GenLayer testnet deployment script
- Demo showing scan of known tokens
- Files: `scripts/deploy.py`, `scripts/demo.py`

## Verification
- All tests pass (`pytest tests/`)
- Contract runs in GenLayer Studio (local dev)
- Demo produces correct risk assessments for simulated data
