---
name: hackathon-submission
description: Draft hackathon project submissions — research protocol traction, build technical narrative, identify ecosystem SDKs, coordinate with dev team on architecture.
category: strategies
tags: [hackathon, writing, pitch, web3, solana, coordination]
version: 1.0
---

# Hackathon Submission Drafting

Use this workflow when preparing a hackathon project submission. Covers research, narrative, technical architecture, and dev coordination.

## Trigger
- User asks to draft a hackathon submission, project description, or pitch
- Preparing for a specific hackathon deadline (Colosseum, ETHGlobal, etc.)

## Workflow

### Step 1: Gather Context
- Check vault for existing plans: `02-Labs/`, hackathon-specific docs
- Check `09-Green Room/` for dev handoffs related to this hackathon
- Review any existing contracts/code in repos

### Step 2: Research Protocol Traction
- Search for the core protocol's stats (transactions, volume, users)
- Check official docs for SDK/ecosystem tools devs can use
- Look for chain-specific integrations (x402 on Solana, etc.)
- Find facilitators, frameworks, and first-party support

Sources to check:
- Official protocol docs
- Chain ecosystem pages (solana.com, etc.)
- GitHub repos for SDKs
- Developer documentation (Coinbase CDP, etc.)

### Step 3: Draft Submission Narrative
Standard structure (adapt per hackathon requirements):

```
# [Project Name]: [One-liner pitch]

> Hackathon | Track | Prizes targeted

## The Problem
- What's broken in the current ecosystem?
- Why does this matter NOW (not in 5 years)?

## The Solution
- What are you building?
- How does it work? (ASCII flow diagram)

## Why [Chain]
- Specific chain advantages (finality, cost, volume)
- Traction data showing market is here

## Architecture
- Programs/contracts table
- Key integrations (SDKs, facilitators)
- How components connect

## Security Model
- What vulnerabilities are eliminated by chain choice
- New attack vectors you address
- Audit angle if targeting security tracks

## Traction & Market
- Protocol stats (transactions, volume, users)
- Why now (market timing, ecosystem readiness)

## Team
- Roles mapped to people
- Relevant background

## What We're Submitting
- Concrete deliverables list
```

### Step 4: Identify Dev Dependencies
- List SDKs/tools the dev team needs to evaluate
- Flag facilitator services and their pricing
- Note any "build vs integrate" decisions

### Step 5: Send to Dev Team
- Post in dev's Telegram group with:
  - Summary of what you drafted
  - Specific architecture questions (program split, SDK choice, tx flow)
  - Timeline question (can they scaffold alongside current work?)
- Create Green Room handoff with full context
- Update Mess Hall status

### Step 6: Iterate
- Wait for dev feedback on architecture
- Adjust narrative to match what's actually buildable
- Lock copy once architecture is confirmed

## Key Principles
- **Lead with traction**: Stats beat promises. "37M transactions" > "we will build"
- **Chain-native framing**: Don't port — build for the chain's strengths
- **Security as feature**: If targeting audit tracks, escrow/trust IS the security use case
- **One build, multiple pitches**: Same core contracts, different narrative angles per track
- **Taglines matter**: Test 2-3, pick the one that sticks
- **Ruthless shipping filter**: Pick ONE demo flow, build toward it. Everything else is Phase 2.
- **DMOB bottleneck**: He's the only dev — scaffold ASAP, don't wait for perfect specs

## Demo Flow Template (3 minutes)
Use this when Jordan asks for a video or live demo plan:
```
1. Show registration on devnet (30 sec)
2. Show payment → escrow creation (30 sec)
3. Show work submission → approval → payment release (30 sec)
4. Show "dogfood" angle — team agents paying each other (30 sec)
5. Show block explorer with transactions (30 sec)
6. Close with pitch + traction stats (30 sec)
```

## Pitfalls
- Don't wait for perfect — ship the submission, iterate on the build
- Scope creep: pick ONE demo flow, build toward it relentlessly
- Judges remember stories, not architecture diagrams
- Always check submission format requirements (some want videos, some want live demos)
- Planning docs are NOT code — minimize doc time, maximize build time
- Multiple workstreams need to be synced (DMOB builds, Desmond writes, YoYo researches — all on same thread)

## Output
- Draft saved to `06-Content/[Hackathon-Name]-Submission-DRAFT.md`
- Green Room handoff for dev team
- Mess Hall status update
- Telegram ping to dev group with specific questions
