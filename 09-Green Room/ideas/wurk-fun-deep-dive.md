# WURK.fun Deep Dive — Agent-to-Human Microjob Marketplace

**Date:** June 1, 2026
**Source:** Tweet from @ElisaSumar38408
**URL:** https://wurk.fun
**Status:** Active, production-ready

## What It Is

Microjob marketplace for AI agents and humans on Solana. Agents hire humans for tasks, humans earn crypto.

## Integration Points (All Match Our Stack)

| Feature | WURK Support | Our Stack |
|---------|-------------|-----------|
| x402 payments | ✅ Solana + Base | ✅ Building with |
| MCP endpoint | ✅ https://wurkapi.fun/mcp | ✅ We use this |
| Solana wallets | ✅ Required | ✅ Have one |
| OpenAPI spec | ✅ Full spec available | ✅ Can integrate |
| USDC payments | ✅ Native | ✅ Have USDC |

## API Endpoints

### Agent-to-Human (Simple)
```
GET https://wurkapi.fun/solana/agenttohuman?description=TASK&winners=N&perUser=0.025
```
- Creates a paid task
- Humans complete it
- You fetch submissions later with secret

### Agent-to-Human (Advanced)
```
GET https://wurkapi.fun/solana/agenttohumanadvanced?description=TASK&selectionType=creator
```
- Manual winner selection
- Longer selection windows
- Optional requirement gating

### MCP Endpoint
```
https://wurkapi.fun/mcp
```
- Works with Claude Desktop, Cursor, any MCP client
- Can integrate with Hermes

### x402 Discovery
```
https://wurkapi.fun/.well-known/x402
```

### OpenAPI Specs
- x402: https://wurkapi.fun/openapi-x402.json
- MPP (Tempo): https://wurkapi.fun/openapi.json
- MPP (Solana): https://wurkapi.fun/openapi-mpp-solana.json

## How x402 Payment Works

1. Call endpoint WITHOUT payment → 402 Payment Required
2. Sign the payment (x402 SDK)
3. Retry WITH PAYMENT-SIGNATURE header → 200 OK

## Social Growth Services (25+)

Available across X/Twitter, Instagram, YouTube, Telegram, Discord, DexScreener, Base, Zora.

## Best Practices

- Use `agenttohuman` for simple, broad, fast input
- Use `agenttohumanadvanced` for manual winner selection
- Keep prompts easy to parse for real humans
- Number options for easy parsing (e.g., "1 - reason")
- Don't use unlimited entries for simple tasks

## Use Cases for Gentech

### 1. TradeRoast Feedback
- Post roast drafts to WURK
- Humans rate which roast is funniest
- Pay 0.025 USDC per response
- Get real human signal on comedy content

### 2. Pals Build Validation
- Post POE2 build screenshots
- Humans rate which build looks stronger
- Get community signal on meta alignment

### 3. Portfolio User Testing
- Post portfolio URL
- Humans test navigation and give feedback
- Pay for genuine UX feedback

### 4. AAE Agent Tasks
- Agents post tasks on WURK
- Humans complete them
- Agents pay with x402
- Full agent-to-human economy loop

## Integration Plan

1. Install WURK skill: `curl -s https://wurkapi.fun/skill.md > ~/.hermes/profiles/gentech/skills/wurk-integration/SKILL.md`
2. Configure x402 wallet for payments
3. Test with simple poll (logo preference)
4. Build AAE integration layer
5. Deploy agent-to-human task pipeline

## Revenue Angle

- WURK takes a fee on transactions
- We could white-label the agent-to-human layer
- Our agents could earn by completing tasks
- Humans could earn from our agent ecosystem
