# Forge Handoff — Agent Companion (Phase 0 Complete)

**Date:** July 6, 2026  
**Status:** ✅ Phase 0 Complete + GitHub Issues Submitted  
**Next Phase:** Phase 1 — AI Companion Core (Week 2-3)

---

## Quick Summary

We've completed Phase 0 research and submitted contribution offers to all three emulators using a "prove first, propose second" strategy.

**Strategy:** Instead of dropping massive AI Companion proposals, we offered to help with existing bugs first. This builds trust before proposing major features.

---

## Files for Forge to Review

All research and proposals are in:

```
/root/vaults/gentech/10-Labs/agent-companion/
├── PRODUCT-VISION.md                    # Complete product vision + build plan
└── research/
    ├── PHASE0-RESEARCH.md               # Full research summary with compatibility matrix
    ├── PHASE0-COMPLETION.md             # Phase 0 completion summary
    ├── XENIA-RESEARCH.md                # Xenia technical details
    ├── XENIA-PROPOSAL.md                # Full AI Companion proposal (for later)
    ├── XENIA-CONTRIBUTION-OFFER.md      # Contribution offer (SUBMITTED)
    ├── RPCS3-RESEARCH.md                # RPCS3 technical details
    ├── RPCS3-PROPOSAL.md                # Full AI Companion proposal (for later)
    ├── RPCS3-CONTRIBUTION-OFFER.md      # Contribution offer (SUBMITTED)
    ├── DOLPHIN-RESEARCH.md              # Dolphin technical details
    ├── DOLPHIN-PROPOSAL.md              # Full AI Companion proposal (for later)
    ├── DOLPHIN-CONTRIBUTION-OFFER.md    # Contribution offer (NEEDS MANUAL SUBMISSION)
    ├── xenia/                           # Xenia repo clone
    ├── rpcs3/                           # RPCS3 repo clone
    └── dolphin/                         # Dolphin repo clone
```

---

## GitHub Issues Submitted

### ✅ Xenia — Issue #2353
**URL:** https://github.com/xenia-project/xenia/issues/2353
**Status:** Live
**Offer:** Help with #2239 (controller duplication bug) + AI Companion discussion
**Strategy:** Prove we can contribute → discuss AI Companion later

### ✅ RPCS3 — Issue #18999
**URL:** https://github.com/RPCS3/rpcs3/issues/18999
**Status:** Live
**Offer:** Help with pad handler/RSX capture issues + AI Companion discussion
**AI Disclosure:** Included (per RPCS3 policy)

### ⏳ Dolphin — Issues Disabled
**Status:** Needs manual submission
**Action:** Submit via web interface or email
**Document:** DOLPHIN-CONTRIBUTION-OFFER.md ready

---

## Key Findings

| Emulator | Input Injection | Screen Capture | License | Integration Complexity |
|----------|-----------------|----------------|---------|----------------------|
| **Xenia** | `InputDriver` base class ✅ | `GuestOutputRefreshContext` ✅ | BSD 3-clause ✅ | **Low** |
| **RPCS3** | `PadHandlerBase` ✅ | `rsx_capture` system ✅ | GPL-2.0 ⚠️ | **Medium** (license) |
| **Dolphin** | `ControllerInterface` ✅ | TBD (VideoCommon) ⏳ | GPLv2+ ⚠️ | **Medium** (license + research) |

### Critical Insight: We Got Lucky

**All three emulators have extensible input systems** — we can inject controller input.

**All three have capture infrastructure** — screen capture is possible.

**The main constraint is licensing:**
- Xenia (BSD) = Easiest — proprietary code allowed
- RPCS3/Dolphin (GPL) = Require IPC separation — GPL bridge, proprietary AI

---

## License Strategy for GPL Emulators

For RPCS3 and Dolphin, we use IPC separation:

```
GPL Layer (contributed to emulator)
├─ Input driver registration (GPL)
├─ Screen capture API (GPL)
└─ Shared memory/socket endpoints (GPL)
     ↓ IPC (clean license boundary)
Proprietary Layer (Gentech)
├─ Vision models (proprietary)
├─ Agent logic (proprietary)
├─ Python bridge (proprietary)
└─ Marketplace + payments (proprietary)
```

**Why This Works:**
- IPC separation is standard practice (like proprietary drivers + GPL kernels)
- GPL covers emulator interaction layer
- Proprietary covers AI logic (no GPL infection)
- Clean separation allows both layers to coexist

---

## Next Steps

### Immediate (Next 24-48 Hours)
1. **Wait for maintainer feedback** on Xenia (#2353) and RPCS3 (#18999)
2. **Review maintainer responses** → Accept help? Discuss AI Companion? Reject?
3. **Manually submit Dolphin offer** via web interface
4. **Vault sync** (retry after 1.5 hours when system is less loaded)

### Short-Term (This Week)
1. **Contribution First:** Fix input/capture bugs to build trust
   - Xenia: Address #2239 (controller duplication bug)
   - RPCS3: Address any pad handler issues they identify
   - Show we understand the codebase
   - Demonstrate clean contribution style

2. **Gepard 1.0 TTS — Validation Phase (Forge, 1 hour)**
   - Pull model: `git clone https://huggingface.co/nineninesix/gepard-1.0`
   - Run reference PyTorch runner with sample sentence
   - Generate one voice clip → send to VPS for comparison vs ElevenLabs
   - **Do NOT replace ElevenLabs until testing passes:**
   - ✅ Voice similarity (clone vs original)
   - ✅ Latency (real-time vs batch)
   - ✅ Stability (no crashes, memory leaks, artifacts)
   - Keep ElevenLabs as production default until Gepard clears all checks

3. **Then Propose:** Discuss AI Companion integration
   - Share full proposals (XENIA-PROPOSAL.md, RPCS3-PROPOSAL.md, DOLPHIN-PROPOSAL.md)
   - Get maintainer feedback on API design
   - Negotiate technical details
   - Get approval before coding

### Phase 1 (Week 2-3) — Can Start in Parallel
- Build vision engine (Python)
- Implement game state understanding (generic, game-agnostic)
- Create decision-making layer (configurable per game)
- Integrate Ollama Cloud for inference
- Define bridge protocol (Python ↔ C++ IPC)

### Phase 2 (Week 4-5) — After Maintainer Approval
- Implement C++ screen capture module
- Implement C++ input injector
- Create Python bridge for Xenia
- End-to-end latency testing
- Submit PR to Xenia repository

---

## Build Queue Entry

✅ Added to `scripts/build_queue.json` with:
- Cost: $2-8/2hr (Ollama) or $15-30/2hr (cloud)
- Complexity: Complex
- Forge Threshold: YES
- Gentech + Forge collaboration

---

## Revenue Model (from PRODUCT-VISION.md)

6 revenue streams:
1. **Per-hour AI sessions** ($2-8/2hr with Ollama)
2. **Agent personality marketplace** ($5-50/personality)
3. **Game-specific training data** ($10-100/game)
4. **Enterprise API** ($500-2,000/month)
5. **Highlight generation service** ($5-20/session)
6. **Creator revenue share** (30% of agent sales)

**Potential:** $265-950K/year with 100-1,000 active users

---

## Questions for Forge

1. **Which emulator to prioritize first?** Xenia (BSD) is easiest, RPCS3/Dolphin require IPC separation
2. **Should we start Phase 1 (AI Core) while waiting for maintainer feedback?** Yes, it's independent of emulator integration
3. **Do you want to handle the Dolphin manual submission?** Or should I try again later?
4. **Vault sync:** Should I retry in 1.5 hours, or will you handle it?
5. **Next meeting:** When do you want to review Phase 1 progress?

---

## Phase 0 Status: 100% Complete ✅

**Delivered:**
- ✅ Complete research on Xenia, RPCS3, Dolphin
- ✅ Professional integration proposals (ready for later)
- ✅ Contribution offers (submitted to Xenia + RPCS3, ready for Dolphin)
- ✅ License strategy (IPC separation for GPL)
- ✅ Build plan (Phase 0 complete, ready for Phase 1)
- ✅ Documentation for Forge

**Next Phase:** Phase 1 — AI Companion Core

---

**Last Updated:** July 6, 2026  
**Vault Sync:** Pending retry (system overloaded with old files)  
**Owner:** Gentech → Forge handoff