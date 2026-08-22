# CopilotKit Channels SDK — x402 Approval-Gate Spike (2026-08-21)

**Status:** Spike complete — verdict **WAIT** (vendor-gated; not self-hostable today)

## What I tested
Cloned `CopilotKit/channels-sdk` (MIT), read the repo-owned `build-channels-agent` skill (the API authority), inspected the `minimal-channel` example, and installed all 437 packages on Node 22.14.

## The core finding: it is NOT self-hostable
The SDK routes every turn through **CopilotKit Intelligence**, their managed cloud. The `minimal-channel` example's `runtime.ts` does `required("INTELLIGENCE_API_URL")`, `required("INTELLIGENCE_GATEWAY_WS_URL")`, `required("INTELLIGENCE_API_KEY")` — all hard-required at startup. The repo-owned skill states it plainly:

> **"A CopilotKit Intelligence API key is required (free tier available). There is no standalone or DIY way to run a Channel."**

The open-source SDK is the **client engine** (agent wiring, JSX UI, approval gates, adapters). The **server that owns platform credentials, ingress, and delivery is their cloud**. A direct-adapter path exists (you hold Slack/Telegram tokens) but it still needs Intelligence for the lifecycle — the skill explicitly warns "swapping to a direct adapter to 'make it work' is a known failure mode."

## What WOULD it do for us (if adopted)
- Native approval gates (the exact thing we hack via Telegram bot buttons) — `awaitChoice`/`onInterrupt` renders a Button in the channel and blocks until the human approves.
- One AG-UI agent, native UI on Slack/Teams/Discord/Telegram/WhatsApp.
- `thread.runAgent` with Intelligence Memory.

## Why I'm recommending WAIT, not adopt
1. **Vendor lock-in on the trust layer.** Our whole GTA/agentic-treasury moat is *self-custody + we own the trust substrate* (per `gta-product-thesis.md`). Routing payment approvals through CopilotKit's cloud contradicts that.
2. **We're Telegram-native.** We already run the approval-gate UX in Telegram bot buttons today. Channels adds Slack/Teams — not our current surface.
3. **x402 approval seam would still be ours to wire** — Channels gives the *UI gate* but not the payment challenge/`Payment-Request` fulfilment; that's still our gateway code either way.
4. **Node 22 long-running process** required — another always-on service on the VPS.

## What would make it a "yes" later
- If Jordan wants a **Slack/Teams-native** agent surface (e.g. selling GenTech as a Slack app where enterprises already work), Channels is the fastest path — at the cost of Intelligence being the managed connector. That's a *product-channel* decision, not an infra one.
- If CopilotKit ships a truly self-hosted Intelligence (their docs mention "self-hosted for enterprise" — not on the open-source path), the lock-in objection disappears.

## Verdict
**WAIT.** Don't wire the treasury payment approvals through CopilotKit cloud. Keep Telegram bot-buttons as our approval rail. Revisit only if (a) we need Slack/Teams as a paid product surface, or (b) Intelligence becomes self-hostable on our own infra. Sandbox-only, no funds moved, no code committed to the treasury path.

---
*Spike source: `CopilotKit/channels-sdk` @ main, README + `.agents/skills/build-channels-agent/SKILL.md` + `examples/minimal-channel/`.*
