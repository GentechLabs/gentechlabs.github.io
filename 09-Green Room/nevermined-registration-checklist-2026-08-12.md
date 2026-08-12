# Nevermined Registration — Ready, Needs Your One-Pass Signup (Aug 12)

**Status:** Staged and run-ready. Blocked only on a human API key — nevermined.app requires a login to generate the `NVM_API_KEY` (we have no programmatic signup).

## What's already done
- Full flow researched: Nevermined = open-entry, sell-side, "your API, agent-payable". Register our x402 services as "agents", attach a payment plan, agents pay via x402/USDC on Base.
- SDK verified (`@nevermined-io/payments` v1.10.0), endpoint/plan type confirmed.
- Registration script written + syntax-checked + dry-run validated.

## Your one-pass checklist (~5 min)
1. Go to **https://nevermined.app** → sign in (email/GitHub/Google).
2. **Settings → Global NVM API Keys → + New API Key.** Copy it.
3. Paste the key here OR put it in the vault env: `NVM_API_KEY="live:<your-key>"` (use `sandbox:` prefix to test first).
4. Pick a **BUILDER_ADDRESS** — our settlement wallet for USDC payouts on Base (e.g. the x402 gateway revenue wallet `0x7ebf…96a` or the BlockRun CDP wallet).

## Then I run it
Once I have the key + builder address, I run the staged script at
`/tmp/nevermined-setup/register-gentech.js` (5 services staged: token security, market intel, DeFi LP analytics, wallet analysis, NFT search; $0.01–0.02/call).

**One caveat to decide:** our x402 gateway returns its OWN 402 challenge. Nevermined's middleware returns THEIR 402 with a Nevermined payment-required header. So for Nevermined to "gate" our endpoints, we either:
- **(A)** point Nevermined at our endpoint and let Nevermined's proxy settle (their infra handles metering + settlement), OR
- **(B)** keep our native x402 gateway as the gate and just list the service in Nevermined for discovery.

(A) = we get their metering/settlement for free but lose our own facilitator; (B) = keep our rail, Nevermined is a discovery listing. I'd recommend **B** (matches our "we ARE the rails" thesis), but worth your call.

## Notes
- The script registers 5 agents + plans in one run; IDs print on success; I save them to the registry.
- This is genuinely open-entry (no stake, no incorporation) and 1.2M req/day live — the strongest sell-side option we've found. Worth the 5 min.
