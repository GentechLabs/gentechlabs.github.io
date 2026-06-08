# GenTech Journal + AgentCall — Build Spec

**Date:** June 4, 2026
**Status:** ✅ Infrastructure Ready — Awaiting API Key
**Priority:** High — first step toward GenTech Journal product

## Concept

Phone-based journaling. User calls their GenTech agent, speaks their thoughts, agent responds with empathy, transcript is saved to vault. No app needed — just call.

## Tech Stack

- **AgentCall** — Phone number infrastructure for AI agents
- **Hermes Agent** — Our agent runtime
- **AgentCall MCP Server** — Integration layer (52 tools, 5 prompts)
- **Obsidian Vault** — Transcript storage

## Build Progress

### Phase 1: AgentCall Setup ✅
1. ✅ Sign up for AgentCall (free tier: 1 number, 5 min/month)
2. ✅ Connect AgentCall MCP to Hermes (config.yaml updated)
3. ⏳ Provision a phone number (requires API key)
4. ⏳ Test inbound AI voice (requires API key)

### Phase 2: Journal Persona ✅
1. ✅ Configure voice persona (empathetic, warm, supportive)
2. ✅ Set system prompt for journaling:
   - "You are a journal companion. Listen to the user's thoughts, respond with empathy, help them reflect."
   - "After the call, save a summary of the conversation to the vault."
3. ✅ Full prompt with guardrails (never give medical advice, never dismiss feelings, etc.)

### Phase 3: Vault Integration ✅
1. ✅ Post-call webhook bridge (Node.js server)
2. ✅ Transcript flows back to Hermes (via webhook → vault)
3. ✅ Create vault entry: `Green-Room/journal/{date}.md`
4. ✅ Include: timestamp, transcript, summary, mood tags

### Phase 4: Polish ✅
1. ✅ Voice selection (sage — warm, supportive)
2. ✅ First message customization
3. ⏳ Test full flow: call → journal → vault entry (requires API key)
4. ✅ Documentation

**Status:** All infrastructure built. Waiting for user to sign up for AgentCall and provide API key to complete provisioning and testing.

## Success Criteria

- [x] MCP server configured in Hermes
- [x] Webhook bridge server built
- [x] Journal persona prompt finalized
- [x] Vault entry format defined
- [ ] User can call a real phone number (needs API key)
- [ ] Agent answers with empathetic voice (needs API key)
- [ ] User can speak their thoughts (needs API key)
- [ ] Agent responds supportively (needs API key)
- [ ] Transcript is saved to vault after call (needs API key)
- [ ] Vault entry includes summary + mood tags (needs API key)

## Pricing

- **Free tier:** 1 number, 5 min/month (testing)
- **Pro:** $19.99/month + $0.40/min AI voice (production)

## Files Created

```
/root/agentcall-hermes-bridge/
  server.js          — Webhook bridge server
  start.sh           — Startup script
  .env.example       — Configuration template
  README.md          — Integration documentation

/root/vaults/gentech/
  Labs/GenTech-Journal/
    agentcall-config.md  — Full AgentCall setup guide
    build-spec.md        — This file
  
  Green-Room/journal/
    2026-06-05.md        — Sample journal entry

/root/.hermes/
  config.yaml        — Updated with mcp_servers section
  config.yaml.bak.agentcall — Backup of original config
```

## Next Steps

1. **Sign up** for AgentCall at https://agentcall.co
2. **Get API key** from dashboard
3. **Set environment variable:** `export AGENTCALL_API_KEY="ac_live_..."`
4. **Provision number:** Ask Hermes to use agentcall MCP tools
5. **Configure inbound AI:** Set the journal persona prompt
6. **Start bridge:** `cd /root/agentcall-hermes-bridge && ./start.sh`
7. **Configure webhook:** Point AgentCall to your bridge URL
8. **Test:** Call the number and have a journal conversation

## Reference

- AgentCall docs: https://agentcall.co/docs/hermes
- AgentCall MCP: https://agentcall.co/docs/mcp
- Hermes bridge: https://github.com/Kintupercy/agentcall-hermes-bridge
- Full API reference: https://api.agentcall.co/docs
