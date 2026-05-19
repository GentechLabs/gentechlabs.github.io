# Colosseum Copilot — Setup Guide

**Date:** 2026-04-21
**For:** DMOB (Solana native build)

## What It Is
A skill for coding agents (Claude Code, Codex, etc.) that turns them into Solana hackathon experts. Gives your agent context about Colosseum submissions, Solana best practices, and hackathon requirements.

## Setup Steps

### 1. Generate PAT
- Go to: https://colosseum.com/copilot (or arena.colosseum.org/copilot)
- Log in with Jordan's Colosseum account (already registered)
- Generate a Personal Access Token

### 2. Install the Skill
```bash
npx skills add ColosseumOrg/colosseum-copilot
```

### 3. Use It
Once installed, your coding agent can answer questions about:
- Solana program best practices
- Hackathon submission requirements
- Colosseum judging criteria
- Solana ecosystem integrations

## Why It Matters for Us
- Native Solana build for Frontier (May 11)
- Ensures our Anchor program follows Solana conventions
- Helps with submission formatting and pitch alignment
- May surface sidetrack opportunities we're missing

## Links
- Copilot page: https://colosseum.com/copilot
- Hackathon: https://arena.colosseum.org
- Docs: Check copilot page after login

## Note
Already referenced in VPS Infrastructure doc (`SUPERSTACK` section). SUPERSTACK had this as a dependency — now that Jordan is registered, we can finally grab the PAT.
