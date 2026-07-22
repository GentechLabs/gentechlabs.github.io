# Governance Agent — Build Plan

**Date:** 2026-05-23
**Status:** 🟢 In Progress
**Repo:** github.com/ProtoJay4789/genlayer-governance-agent (new)

## Problem
Governance participation in DeFi is fragmented across on-chain proposals (Snapshot, Tally, Governor contracts) and off-chain forums (Discourse, Commonwealth, GitHub). Token holders miss critical votes because they can't monitor everything. An Intelligent Contract that reads multi-source governance data and recommends votes showcases GenLayer's most complex agentic capabilities.

## Architecture
GenLayer Intelligent Contract that:
1. Fetches proposals from multiple governance sources (Snapshot API, Tally API, Governor contracts)
2. Analyzes proposal sentiment and impact using LLM reasoning
3. Scores proposals based on: alignment with strategy, quorum status, time remaining, historical patterns
4. Recommends vote direction (FOR/AGAINST/ABSTAIN) with confidence level
5. Stores governance history and voting record on-chain

## Data Sources
- **Snapshot API**: `https://hub.snapshot.org/graphql` — off-chain voting, sentiment
- **Tally API**: `https://api.tally.xyz/query` — on-chain governance (Governor contracts)
- **Boardroom API**: `https://api.boardroom.tv/v2/protocols` — aggregated governance data
- **Proposal text**: Can be fetched and interpreted by LLM (GenLayer's native capability)

## Scoring Model
Each proposal scored on 0-100:
- **Alignment Score (30%)**: How well does this proposal benefit the protocol/AAE ecosystem?
- **Participation Score (20%)**: Is quorum likely? How many voters are active?
- **Urgency Score (20%)**: Time remaining — urgent proposals score higher
- **Risk Score (15%)**: Does this proposal introduce technical/financial risk?
- **Sentiment Score (15%)**: Community sentiment from forum discussions

Vote recommendation:
- Score > 70 → FOR
- Score 40-70 → ABSTAIN (needs more analysis)
- Score < 40 → AGAINST

Confidence = based on data completeness (how many sources we could read)

## Tasks

### Task 1: Project Scaffold
- Directory structure, requirements.txt, README.md
- Files: `genlayer-governance-agent/`

### Task 2: Governance Agent Contract
- `@contract` decorated class `GovernanceAgent`
- `__init__` with Storage for proposals, votes, and history
- `analyze_proposal(proposal_id, source)` — fetch + score + recommend
- `analyze_all()` — scan all sources, return top proposals
- `cast_vote(proposal_id, direction, reason)` — record vote decision
- `get_history()` — past votes and recommendations
- Internal scoring methods for each dimension
- Files: `contracts/governance_agent.py`

### Task 3: Tests
- pytest tests for scoring dimensions
- Test vote recommendation logic
- Test proposal fetching and parsing
- Test edge cases (expired proposals, missing data)
- At least 15 test cases
- Files: `tests/test_agent.py`

### Task 4: Demo Script
- Standalone demo with simulated governance proposals
- Include: Snapshot proposal, Tally on-chain vote, urgent time-sensitive proposal
- Show analysis, scoring, and vote recommendation
- Pretty-print with emojis
- Files: `scripts/demo.py`

## Verification
- All tests pass
- Demo runs and produces formatted output
- Contract syntax valid
