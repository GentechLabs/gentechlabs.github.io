# Initial Contribution: Input System & Infrastructure Help

## About GenTech Labs

We're a research lab building AI agent infrastructure. We're developing an AI Companion system that lets external AI agents play games as Player 2 (and beyond) via emulator integration.

## What We Want to Do

We want to contribute to Xenia in two ways:

### 1. Help with Existing Issues (Short-Term)

We've reviewed open issues and identified several we can help with, particularly in input/capture areas:

**Immediate Candidate:** #2239 — Controller input duplication bug
- Issue: Wireless Xbox 360 controller detected as two separate controllers
- Relevant: Directly related to our understanding of `InputDriver` architecture
- We can: Investigate and fix the duplication logic

**Other candidates:**
- #2138 — SDL2 external controller mapping support
- Any other input-related bugs you'd like help with

### 2. AI Companion Integration (Long-Term)

We're building AI Companion — optional support for external AI agents to play games via native integration. This contributes:
- Screen capture API (expose frame buffer)
- Input injection API (allow external input)
- Shared memory infrastructure

The AI logic is our proprietary IP, but the emulator integration is generic infrastructure that benefits all Xenia users (debugging, automation, accessibility).

We're **not** asking for immediate approval of AI Companion. We want to:
1. First, prove we can contribute useful fixes (like #2239)
2. Build trust with maintainers
3. Then, if you're interested, we can share the full AI Companion proposal

## Why We're Doing This

We believe:
- AI Companion would provide valuable infrastructure for Xenia's tooling ecosystem
- Contributing to open source is the right way to build this
- We should earn maintainer trust before proposing major features

## Next Steps

**If you're interested:**
1. We'll start by addressing #2239 (controller duplication bug)
2. Submit PR with thorough testing and documentation
3. Get your feedback on our contribution style
4. Discuss AI Companion proposal when you're ready

**If you're not interested:**
- We understand completely
- We can still contribute input fixes if you want
- We'll respect your decision on AI Companion

## Questions for Maintainers

1. Are you interested in contributions for #2239 (controller duplication bug)?
2. Any other input/capture-related issues you'd like help with?
3. Would you be open to discussing AI Companion after we've built trust via contributions?
4. Any technical preferences for how we approach these fixes?

## Our Commitment

- Follow Xenia's coding style and contribution guidelines
- Clean git history, small PRs, thorough testing
- Respect maintainers' time and decisions
- Long-term commitment to maintaining contributed code
- Transparent about our goals (no hidden agendas)

---

**Thank you for considering. We're excited to contribute to Xenia.**

---

**Next Action:** Awaiting maintainer feedback before proceeding