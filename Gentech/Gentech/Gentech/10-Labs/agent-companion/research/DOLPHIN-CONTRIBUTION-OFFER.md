# Initial Contribution Offer: Controller Backend & Screen Capture Help

## About GenTech Labs

We're a research lab building AI agent infrastructure. We're developing an AI Companion system that lets external AI agents play games as Player 2 (and beyond) via emulator integration.

## What We Want to Do

We want to contribute to Dolphin in two ways:

### 1. Help with Existing Work (Short-Term)

We've reviewed the codebase and identified areas where we can help, particularly in controller backend and screen capture areas:

**Candidates we can help with:**
- Controller backend improvements (ControllerInterface)
- Screen capture infrastructure in VideoCommon
- Any input-related features you'd like help with
- Accessibility features for controller input

We're open to your guidance on what's most valuable for Dolphin.

### 2. AI Companion Integration (Long-Term)

We're building AI Companion — optional support for external AI agents to play games via native integration. This would contribute:
- Controller backend for external input injection
- Screen capture API for frame extraction
- Shared memory infrastructure

**License Strategy:**
- Contributed code (controller backend, capture API, shared memory) → GPL (as required)
- AI models, decision logic, marketplace → Proprietary (communicates via IPC)
- Clean IPC boundary = standard practice (like proprietary drivers + GPL kernels)

**We're not asking for immediate approval.** We want to:
1. First, prove we can contribute useful features
2. Build trust with maintainers
3. Then, if you're interested, share the full AI Companion proposal

## Why We're Doing This

We believe:
- AI Companion would provide valuable infrastructure for Dolphin's tooling ecosystem
- Contributing to open source is the right way to build this
- We should earn maintainer trust before proposing major features
- We respect Dolphin's GPLv2+ license

## Next Steps

**If you're interested:**
1. We'll start with a controller backend or screen capture feature you identify
2. Submit PR with thorough testing and documentation
3. Get your feedback on our contribution style
4. Discuss AI Companion proposal when you're ready

**If you're not interested:**
- We understand completely
- We can still contribute controller backend improvements if you want
- We'll respect your decision on AI Companion

## Questions for Maintainers

1. What's the most valuable contribution we could make right now?
2. Would you be open to discussing AI Companion after we've built trust via contributions?
3. Any concerns about our GPL license strategy (IPC separation)?
4. Any technical preferences for how we approach screen capture (VideoCommon vs Qt UI)?
5. Best channel for communication (GitHub Discussions, Discord, email)?

## Our Commitment

- Follow Dolphin's coding style and contribution guidelines
- Clean git history, small PRs, thorough testing
- Respect maintainers' time and decisions
- Long-term commitment to maintaining contributed code
- Transparent about our goals (no hidden agendas)

---

**Thank you for considering. We're excited to contribute to Dolphin.**

---

**Next Action:** Awaiting maintainer feedback before proceeding