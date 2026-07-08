# Integration Proposal: AI Companion Support for RPCS3

**Repository:** RPCS3/rpcs3  
**Date:** July 6, 2026  
**From:** GenTech Labs (https://gentech.dev)  
**Status:** Draft — Maintainer Review Requested

---

## Executive Summary

We propose adding optional AI Companion support to RPCS3, enabling external AI agents to play games as Player 2 (and beyond) via native integration. This contributes generic pad handler and RSX capture APIs to RPCS3, while the AI logic remains separate and proprietary.

---

## About GenTech

GenTech Labs is a research lab building AI agent infrastructure, including:
- Multi-agent orchestration platforms
- AI marketplace for agent services
- Automation tools for various domains

Our goal: Make AI agents accessible and useful for everyday tasks — including gaming companionship.

---

## AI Disclosure Statement

**Per RPCS3 AI Use Policy:**

This proposal was prepared with the assistance of AI tools. The following work involved AI:
- Code research and architecture analysis
- Technical proposal drafting
- API design recommendations

**Human Review & Testing:**
- All technical details were reviewed by human contributors
- All code contributed to RPCS3 will be thoroughly tested
- PRs will include detailed disclosure of AI involvement
- Human contributors take full ownership of submitted code

---

## What We Propose to Contribute

### Open Source Contributions (to RPCS3)

#### 1. Pad Handler for AI Input Injection
- Create `agent_pad_handler` inheriting from `PadHandlerBase`
- Register in pad handler system (opt-in via config)
- Expose shared memory interface for external input
- Implement PS3 button mapping (Cross, Circle, Square, Triangle, etc.)
- **Benefit:** Enables automation, testing, and accessibility tools

#### 2. RSX Capture API Extension
- Extend `rsx_capture` system for real-time frame extraction
- Add optional callback for external frame capture
- Document API for external integrations
- **Benefit:** Enables debugging tools, recording utilities, and automation

#### 3. Shared Memory Infrastructure
- Generic buffer pool for frame sharing
- IPC endpoints for communication
- Configuration flags for opt-in behavior
- **Benefit:** Reusable infrastructure for other third-party tools

### What We Keep Proprietary

- Vision models and game-specific training data
- AI decision-making logic
- Python bridge implementation
- Agent marketplace and payment integration
- Agent personality modules

**Rationale:** The AI logic is our proprietary IP. The emulator integration (pad handler, capture API, shared memory) is generic infrastructure useful to all RPCS3 users.

---

## How It Works

```
RPCS3 Core (C++, GPL)
├─ agent_pad_handler (GPL)
├─ rsx_capture extension (GPL)
└─ Shared memory pool (GPL)
     ↓ IPC (clean license boundary)
Agent Core (Python, proprietary)
├─ Vision analysis
├─ Game state understanding
├─ Decision making
└─ x402 payments
```

### Workflow

1. User enables AI Companion via RPCS3 configuration
2. RPCS3 renders frames to RSX
3. RSX capture hook copies frame to shared memory
4. External Python process reads shared memory
5. Vision model analyzes game state
6. AI makes decisions
7. Agent writes controller state to shared memory
8. RPCS3 reads controller state via `agent_pad_handler`
9. Pad input injected into game

---

## Benefits for RPCS3

### 1. Enhanced Tooling Ecosystem
- Developers get RSX capture API for debugging
- Automation tools can test games programmatically
- Recording utilities get native access to frames

### 2. Accessibility Use Cases
- Automated accessibility testing
- Controller remapping for users with disabilities
- Assistive technologies can hook into RPCS3

### 3. Research Value
- AI agents can test game logic edge cases
- Automated compatibility testing
- Stress testing of emulator behavior

### 4. Community Value
- Gamers get AI companions for co-op games
- Streamers get reliable teammates
- Solo gamers can play co-op games without friends

---

## License Considerations

**RPCS3 License:** GPL-2.0-only

**Our Strategy:**
- Contribute: Pad handler, RSX capture extension, Shared memory infrastructure → GPL
- Keep proprietary: AI models, decision logic, marketplace

**Why This Works:**
- IPC separation maintains clean license boundary
- GPL covers emulator interaction layer
- Proprietary covers AI logic (no GPL infection)
- Clean separation allows both layers to coexist

**Potential Concern:** GPL requires derivative works to be GPL
**Our Response:** The contributed code becomes GPL (as required). The proprietary AI layer communicates via IPC, so it doesn't become a derivative work. This is a well-established pattern (e.g., proprietary drivers communicating with GPL kernels).

---

## Technical Concerns & Questions

We want to ensure this aligns with RPCS3's goals and maintainers' expectations. Key questions:

1. **Is this aligned with RPCS3's goals?**
   - We understand RPCS3 is a research emulator
   - AI agents could help test compatibility and game behavior
   - We're not adding game-specific hacks or proprietary Sony code

2. **Should this be opt-in?**
   - We propose making AI Companion opt-in via configuration flag
   - Default behavior: Disabled
   - User must explicitly enable `enable_ai_companion = true`

3. **Performance concerns?**
   - RSX capture only when AI Companion is enabled
   - Shared memory is fast (mmap)
   - No impact on normal RPCS3 operation when disabled

4. **API design concerns?**
   - Should RSX capture be a callback or polling?
   - Should pad handler be event-based or state-based?
   - Any technical preferences from maintainers?

5. **Maintenance concerns?**
   - We're willing to maintain the integration code
   - We'll follow RPCS3's coding style and contribution guidelines
   - Clean git history, small PRs, thorough testing

6. **GPL license concerns?**
   - IPC separation ensures no GPL infection
   - We understand GPL requirements for contributed code
   - Open to alternative approaches if maintainers prefer

---

## Next Steps (If Approved)

1. **Phase 1: RSX Capture API Extension**
   - Extend `rsx_capture` for real-time frame extraction
   - Add configuration flag
   - Test with existing RPCS3 games
   - Submit PR with AI disclosure

2. **Phase 2: Pad Handler Implementation**
   - Implement `agent_pad_handler`
   - Register in pad handler system
   - Test controller injection
   - Submit PR with AI disclosure

3. **Phase 3: Shared Memory Infrastructure**
   - Implement buffer pool
   - Add IPC endpoints
   - Test with external Python process
   - Submit PR with AI disclosure

4. **Phase 4: Integration Testing**
   - End-to-end testing with AI agent
   - Performance benchmarking
   - Community feedback

---

## Risks & Mitigations

### Risk: Misuse by bad actors
**Mitigation:**
- Opt-in by default (disabled)
- Clear documentation of capabilities
- Community guidelines for AI Companion use

### Risk: Performance impact
**Mitigation:**
- Zero overhead when disabled
- Shared memory is fast
- Optional frame rate limiting

### Risk: Code maintenance burden
**Mitigation:**
- We maintain the integration code
- We contribute to RPCS3 long-term
- We follow contribution guidelines

### Risk: GPL license conflicts
**Mitigation:**
- IPC separation is standard practice
- We acknowledge GPL requirements
- We're open to alternative approaches

---

## Alternatives Considered

1. **External tool hooking via Windows API**
   - Cons: Slower, less reliable, platform-specific
   - Native integration is cleaner

2. **Separate fork of RPCS3**
   - Cons: Fragmentation, harder to maintain, less community benefit
   - Upstream contribution benefits everyone

3. **No contribution, only proprietary bridge**
   - Cons: Slower, less reliable, no community benefit
   - Upstream contribution is better for ecosystem

---

## Contact & Discussion

**Maintainer Discussion Points:**
- Is this aligned with RPCS3's goals?
- Any technical concerns with the proposed approach?
- Preferences for API design (callback vs polling, event vs state)?
- Any concerns about GPL license separation?
- Any conditions for approval?

**Next Action:**
- Open issue on GitHub requesting feedback
- Maintain PR draft for review
- Schedule Discord/forum discussion if needed

---

## Appendix: Technical Details

### Pad Handler Design

```cpp
// Proposed API
class agent_pad_handler final : public PadHandlerBase {
public:
    agent_pad_handler();
    ~agent_pad_handler() override;
    
    // PadHandlerBase implementation
    s32 open() override;
    s32 close() override;
    s32 enumerate() override;
    s32 add_player(const u8 player_id) override;
    
    // Shared memory interface
    void SetControllerState(u8 player_id, const AgentControllerState& state);
    bool HasNewState(u8 player_id) const;
};
```

### RSX Capture Design

```cpp
// Proposed API extension
namespace rsx {
  namespace capture {
    // Existing capture functions
    void capture_draw_memory(thread* rsx);
    void capture_image_in(thread* rsx, frame_capture_data::replay_command& replay_command);
    
    // New: Real-time frame capture callback
    void SetFrameCaptureCallback(std::function<void(const void* data, uint32_t width, uint32_t height)> callback);
    void EnableRealtimeCapture(bool enable);
  }
}
```

### Configuration Design

```ini
# AI Companion settings
# Enable AI Companion support
enable_ai_companion = false

# AI Companion settings
ai_companion_shm_path = "/tmp/rpcs3_ai_shm"
ai_companion_capture_fps = 30
ai_companion_input_latency_ms = 16

# Pad handler settings
Input/ai_pad_handler = false
```

---

## Conclusion

We believe AI Companion support would:
- Provide valuable infrastructure for RPCS3's tooling ecosystem
- Enable accessibility and automation use cases
- Benefit the community with new gaming possibilities
- Align with RPCS3's research goals (testing compatibility)

We're committed to:
- Following RPCS3's contribution guidelines
- Maintaining the integration code long-term
- Respecting the GPL license
- Working transparently with maintainers
- Disclosing AI involvement in all PRs

**Thank you for considering this proposal.**

---

**Last Updated:** July 6, 2026  
**Status:** Draft — Awaiting Maintainer Feedback