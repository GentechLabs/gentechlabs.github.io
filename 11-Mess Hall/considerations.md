# Mess Hall — Considerations

Decisions pending, opportunities to evaluate, things to circle back on.

---

## [ ] Agent Ranking — Register + Verify + List
- **Added:** 2026-06-16
- **Source:** Agent Ranking + xPay partnership announcement
- **Link:** https://app.agentranking.io
- **What:** Agent discovery platform with trust scoring, verified revenue badges, xPay integration, 30+ chain support, MCP server.
- **Why us:** Free visibility. Trust scoring complements ERC-8004. xPay = monetization path. MCP = data integration.
- **Action items:**
  - [ ] Register agents (Agent Kit, working agents)
  - [ ] Complete verification process
  - [ ] Connect xPay for payments
  - [ ] Monitor API for AAE integration
- **Status:** QUEUED — Jordan to execute tomorrow (Jun 17)
- **Effort:** Quick win — register, verify, list. No heavy lift.

---

## [ ] WhatsApp Business Cloud — Customer Service Channel
- **Added:** 2026-06-12
- **Source:** Nous Research dropped WhatsApp Business Cloud integration for Hermes Agent
- **Link:** https://hermes-agent.nousresearch.com/docs/user-guide/messaging/whatsapp-cloud
- **What:** Private WhatsApp bot via Meta's official Business Cloud API. No Node.js bridge, no QR codes, no account-ban risk. Full feature set: webhooks, media/voice, read receipts, typing indicators, interactive approval buttons.
- **Why us:** Customer service channel. People message a WhatsApp number, talk to GenTech directly — no middleman. Free as long as you have internet. "Little do they know, they're talking to the GenTech."
- **Setup:** `hermes gateway setup` → select WhatsApp Cloud. Needs Meta Business account + phone number.
- **Status:** Queued. No immediate business use case yet, but the applications are massive. Add to queue for when we have paying customers.
- **Risk:** Meta Business account requires verification. Phone number dedicated to bot.

---

## [ ] Quant AI Ambassador Program
- **Added:** 2026-06-11
- **Link:** https://x.com/tryquantio/status/2058940341429149712
- **Apply:** https://forms.gle/bEwkiaWLZW9ooL...
- **More:** https://t.me/tryquantai_bot
- **What:** $100K in $QUANT + USDT for creators/contributors. Earn points, referral rewards, ambassador rewards.
- **Why us:** Adjacent to AAE — AI + finance narrative. Low-effort visibility play. Positions us as picks-and-shovels layer for AI trading platforms.
- **Status:** Decided YES. Jordan working 12hr shifts Jun 12-14. Apply after that window.

---

## [ ] Coinbase for Agents — x402 Integration Signal
- **Added:** 2026-06-11
- **Link:** https://x.com/coinbase/status/2065117242036023607
- **What:** Coinbase launching agent accounts — execute trades, manage portfolios, run autonomously under guardrails, pay for data via x402 (coming next week).
- **Why us:** Validates our entire stack. ERC-8004 (agent identity) = Coinbase giving agents accounts. x402 payments = Coinbase integrating x402 for data/tools. Agent finance = their exact pitch. We're already building this.
- **Status:** Monitor. Watch x402 integration details when they drop. Consider integrating Coinbase agent accounts into AAE as a provider option.
- **Risk:** If Coinbase becomes the default agent account layer, we need to integrate with them, not compete.

---

## [ ] WURK.FUN — Agent-to-Human Microtask Marketplace
- **Added:** 2026-06-11
- **Link:** https://wurk.fun/developer
- **API:** https://wurkapi.fun
- **What:** Microtask marketplace where AI agents hire humans. Payment IS authentication — no API key, no signup. x402 on Solana & Base, MPP on Tempo & Solana, USDC pay-per-request.
- **Why us:** Missing piece for Agent Economy. Our agents can hire humans for feedback, content moderation, product testing, social proof. We already support x402 (Ampersend), Solana (AgentBridge), Base (AgentBridge), MCP (Hermes).
- **Pricing:** $0.025/response for feedback, $0.025/unit for X likes/reposts, from $0.03/unit for followers.
- **Status:** HIGH PRIORITY. Direct integration opportunity. They have MCP skill available.
- **Next:** Install their SKILL.md, test API, integrate into AAE as human-in-the-loop layer.

---

## [ ] OOBE PROTOCOL — Solana Agent Infrastructure Map
- **Added:** 2026-06-12
- **Link:** https://x.com/OOBEonSol/status/2065091944787706358
- **What:** OOBE building SAP (Solana Agent Protocol) integration layer. Listed partners: WURK.FUN, AgentRanking, x402, Metaplex, krexa, bento_guard, AutoIncentive.
- **Why us:** Validates our entire stack. We're building in the right ecosystem. WURK.FUN integration already done. x402 already supported. AgentRanking = ERC-8004 related.
- **Status:** Monitor. We're already building the pieces they're integrating.
- **Next:** Reach out to OOBE about integrating AgentBridge (ERC-8004) into their SAP stack.

---
