# Integration Proposal: AI Companion Support for Xenia

**Repository:** xenia-project/xenia  
**Date:** July 6, 2026  
**From:** GenTech Labs (https://gentech.dev)  
**Status:** Draft — Maintainer Review Requested

---

## Executive Summary

We propose adding optional AI Companion support to Xenia, enabling external AI agents to play games as Player 2 (and beyond) via native integration. This contributes generic screen capture and input injection APIs to Xenia, while the AI logic remains separate and proprietary.

---

## About GenTech

GenTech Labs is a research lab building AI agent infrastructure, including:
- Multi-agent orchestration platforms
- AI marketplace for agent services
- Automation tools for various domains

Our goal: Make AI agents accessible and useful for everyday tasks — including gaming companionship.

---

## What We Propose to Contribute

### Open Source Contributions (to Xenia)

#### 1. Screen Capture API Hook
- Extend `GuestOutputRefreshContext` to expose frame buffer to external tools
- Add optional capture flag to presenter configuration
- Document API for external integrations
- **Benefit:** Enables debugging tools, recording utilities, and automation

#### 2. Input Injection API
- Create `AgentInputDriver` class inheriting from `InputDriver`
- Register `AgentInputDriver` in `InputSystem` (opt-in via config)
- Expose shared memory interface for external input
- **Benefit:** Enables automation, testing, and accessibility tools

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

**Rationale:** The AI logic is our proprietary IP. The emulator integration (capture API, input API, shared memory) is generic infrastructure useful to all Xenia users.

---

## How It Works

```
Xenia Core (C++)
├─ AgentInputDriver (open source)
├─ GuestOutputRefreshContext hook (open source)
└─ Shared memory pool (open source)
     ↓ IPC
Agent Core (Python, proprietary)
├─ Vision analysis
├─ Game state understanding
├─ Decision making
└─ x402 payments
```

### Workflow

1. User enables AI Companion via Xenia configuration
2. Xenia renders frames to `GuestOutputRefreshContext`
3. Hook copies frame to shared memory (mmap)
4. External Python process reads shared memory
5. Vision model analyzes game state
6. AI makes decisions
7. Agent writes controller state to shared memory
8. Xenia reads controller state via `AgentInputDriver`
9. Controller input injected into game

---

## Benefits for Xenia

### 1. Enhanced Tooling Ecosystem
- Developers get screen capture API for debugging
- Automation tools can test games programmatically
- Recording utilities get native access to frames

### 2. Accessibility Use Cases
- Automated accessibility testing
- Controller remapping for users with disabilities
- Assistive technologies can hook into Xenia

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

**Xenia License:** BSD 3-clause

**Our Strategy:**
- Contribute: Screen capture API, Input injection API, Shared memory infrastructure → BSD
- Keep proprietary: AI models, decision logic, marketplace

**Why This Works:**
- BSD allows proprietary usage of contributed code
- No license conflicts or GPL infection
- Clean separation between emulator integration and AI logic

---

## Technical Concerns & Questions

We want to ensure this aligns with Xenia's mission and maintainers' expectations. Key questions:

1. **Is this aligned with Xenia's research mission?**
   - We understand Xenia is a research emulator, not a gaming platform
   - AI agents could help test emulation accuracy and game compatibility
   - We're not adding game-specific hacks or XDK references

2. **Should this be opt-in?**
   - We propose making AI Companion opt-in via configuration flag
   - Default behavior: Disabled
   - User must explicitly enable `enable_ai_companion = true`

3. **Performance concerns?**
   - Screen capture only when AI Companion is enabled
   - Shared memory is fast (mmap)
   - No impact on normal Xenia operation when disabled

4. **API design concerns?**
   - Should screen capture be a callback or polling?
   - Should input injection be event-based or state-based?
   - Any technical preferences from maintainers?

5. **Maintenance concerns?**
   - We're willing to maintain the integration code
   - We'll follow Xenia's coding style and contribution guidelines
   - Clean git history, small PRs, thorough testing

---

## Next Steps (If Approved)

1. **Phase 1: Screen Capture API**
   - Implement `GuestOutputRefreshContext` hook
   - Add configuration flag
   - Test with existing Xenia games
   - Submit PR

2. **Phase 2: Input Injection API**
   - Implement `AgentInputDriver`
   - Register in `InputSystem`
   - Test controller injection
   - Submit PR

3. **Phase 3: Shared Memory Infrastructure**
   - Implement buffer pool
   - Add IPC endpoints
   - Test with external Python process
   - Submit PR

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
- We contribute to Xenia long-term
- We follow contribution guidelines

---

## Alternatives Considered

1. **External tool hooking via Windows API**
   - Cons: Slower, less reliable, platform-specific
   - Native integration is cleaner

2. **Separate fork of Xenia**
   - Cons: Fragmentation, harder to maintain, less community benefit
   - Upstream contribution benefits everyone

3. **No contribution, only proprietary bridge**
   - Cons: Slower, less reliable, no community benefit
   - Upstream contribution is better for ecosystem

---

## Contact & Discussion

**Maintainer Discussion Points:**
- Is this aligned with Xenia's mission?
- Any technical concerns with the proposed approach?
- Preferences for API design (callback vs polling, event vs state)?
- Any conditions for approval?

**Next Action:**
- Open issue on GitHub requesting feedback
- Maintain PR draft for review
- Schedule Discord/forum discussion if needed

---

## Appendix: Technical Details

### Screen Capture API Design

```cpp
// Proposed API
class AgentCaptureContext {
public:
    void SetFrameCallback(std::function<void(const void* data, uint32_t width, uint32_t height)> callback);
    void EnableCapture(bool enable);
    uint32_t GetFrameWidth() const;
    uint32_t GetFrameHeight() const;
    uint64_t GetTimestamp() const;
};
```

### Input Injection API Design

```cpp
// Proposed API
class AgentInputDriver : public InputDriver {
public:
    X_RESULT GetState(uint32_t user_index, X_INPUT_STATE* out_state) override;
    
    // Shared memory interface
    void SetControllerState(const AgentControllerState& state);
    bool HasNewState() const;
};
```

### Configuration Design

```ini
[xbox]
# Enable AI Companion support
enable_ai_companion = false

# AI Companion settings
ai_companion_shm_path = "/tmp/xenia_ai_shm"
ai_companion_capture_fps = 30
ai_companion_input_latency_ms = 16
```

---

## Conclusion

We believe AI Companion support would:
- Provide valuable infrastructure for Xenia's tooling ecosystem
- Enable accessibility and automation use cases
- Benefit the community with new gaming possibilities
- Align with Xenia's research mission (testing compatibility)

We're committed to:
- Following Xenia's contribution guidelines
- Maintaining the integration code long-term
- Respecting the research mission (no game-specific hacks)
- Working transparently with maintainers

**Thank you for considering this proposal.**

---

**Last Updated:** July 6, 2026  
**Status:** Draft — Awaiting Maintainer Feedback