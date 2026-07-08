# Initial Contribution: Pad Handler & RSX Capture Help

## About GenTech Labs

We're a research lab building AI agent infrastructure. We're developing an AI Companion system that lets external AI agents play games as Player 2 (and beyond) via emulator integration.

## AI Disclosure

Per RPCS3 AI Use Policy: This issue was prepared with AI assistance for research and technical drafting. All code we contribute will be thoroughly tested and reviewed by human contributors. We take full ownership of submitted code.

## What We Want to Do

We want to contribute to RPCS3 in two ways:

### 1. Help with Existing Issues (Short-Term)

We've reviewed open issues and identified areas where we can help, particularly in pad handler and RSX capture areas:

**Candidates we can help with:**
- General pad handler improvements
- RSX capture/replay enhancements
- Any input-related bugs you'd like help with
- Accessibility features for controller input

We're open to your guidance on what's most valuable for RPCS3.

### 2. AI Companion Integration (Long-Term)

We're building AI Companion — optional support for external AI agents to play games via native integration. This would contribute:
- Pad handler for external input injection
- RSX capture API extension for real-time frame extraction
- Shared memory infrastructure

**License Strategy:**
- Contributed code (pad handler, capture API, shared memory) → GPL (as required)
- AI models, decision logic, marketplace → Proprietary (communicates via IPC)
- Clean IPC boundary = standard practice (like proprietary drivers + GPL kernels)

**We're not asking for immediate approval.** We want to:
1. First, prove we can contribute useful fixes
2. Build trust with maintainers
3. Then, if you're interested, share the full AI Companion proposal

## Why We're Doing This

We believe:
- AI Companion would provide valuable infrastructure for RPCS3's tooling ecosystem
- Contributing to open source is the right way to build this
- We should earn maintainer trust before proposing major features
- We respect RPCS3's AI use policy and GPL license

## Next Steps

**If you're interested:**
1. We'll start by addressing a pad handler or RSX capture issue you identify
2. Submit PR with AI disclosure, thorough testing, and documentation
3. Get your feedback on our contribution style
4. Discuss AI Companion proposal when you're ready

**If you're not interested:**
- We understand completely
- We can still contribute pad handler fixes if you want
- We'll respect your decision on AI Companion

## Questions for Maintainers

1. Are there any pad handler or RSX capture issues you'd like help with?
2. What's the most valuable contribution we could make right now?
3. Would you be open to discussing AI Companion after we've built trust via contributions?
4. Any concerns about our GPL license strategy (IPC separation)?
5. Any technical preferences for how we approach these fixes?

## Our Commitment

- Follow RPCS3's coding style and contribution guidelines
- Clean git history, small PRs, thorough testing
- Include AI disclosure in all PRs
- Respect maintainers' time and decisions
- Long-term commitment to maintaining contributed code
- Transparent about our goals (no hidden agendas)

---

**Thank you for considering. We're excited to contribute to RPCS3.**

---

**Next Action:** Awaiting maintainer feedback before proceeding