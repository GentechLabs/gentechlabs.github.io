---
name: swarms-acm-hackathon
description: Swarms ACM Hackathon project - Tokenized DeFi Signal Agent with Voice Alerts
status: setup
deadline: May 27, 2026
---

# Swarms ACM Hackathon - DeFi Signal Agent

## Hackathon Details
- **Name:** Agent Capital Markets (ACM) Hackathon
- **Deadline:** May 27, 2026
- **Prize Pool:** $30,000 (Solana, $SWARMS, USDC)
- **Requirements:** Tokenized agent/prompt, Frenzy Mode, publish on Swarms Marketplace

## Project: DeFi Signal Agent with Voice Alerts

### Concept
A tokenized AI agent that:
1. Monitors on-chain DeFi signals (LP positions, whale movements, yield opportunities)
2. Generates real-time voice alerts via ElevenLabs TTS
3. Gets tokenized on Swarms as a paid agent

### Architecture
```
[On-Chain Data] → [Signal Detection Script] → [Swarms Agent API] → [Voice Alerts via ElevenLabs]
```

### Components
1. **Signal Engine** (Python) - Monitors on-chain events
2. **Swarms Agent** - Wraps signal engine as tokenized marketplace agent
3. **Voice Layer** - ElevenLabs TTS for alert delivery
4. **Token Contract** - Agent tokenization via Swarms Frenzy Mode

### Cyfrin Alignment
- Token contract security (ERC-20 patterns)
- Access control for agent operators
- Fee distribution mechanisms
- Reentrancy protection in fee claims

## Status
- [x] Swarms API key obtained
- [x] Project scaffolding created (swarms-defi-agent/)
- [x] Signal engine implemented (7 tools: prices, pool state, IL calc, recommendations, reports, whale watch, yield scanner)
- [ ] Agent published to Swarms Marketplace
- [ ] Voice alerts integrated (ElevenLabs)
- [ ] Tokenization via Frenzy Mode
- [ ] Demo video recorded
- [ ] Marketplace listing published
- [ ] Submission completed

## Notes
- User will create API key for testing
- Combine with existing LP monitor script
- Use Steve Harvey voice clone from ElevenLabs work
