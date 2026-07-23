# Integration Proposal: AI Companion Support for Dolphin

**Repository:** dolphin-emu/dolphin  
**Date:** July 6, 2026  
**From:** GenTech Labs (https://gentech.dev)  
**Status:** Draft — Maintainer Review Requested

---

## Executive Summary

We propose adding optional AI Companion support to Dolphin, enabling external AI agents to play games as Player 2 (and beyond) via native integration. This contributes generic controller backend and screen capture APIs to Dolphin, while the AI logic remains separate and proprietary.

---

## About GenTech

GenTech Labs is a research lab building AI agent infrastructure, including:
- Multi-agent orchestration platforms
- AI marketplace for agent services
- Automation tools for various domains

Our goal: Make AI agents accessible and useful for everyday tasks — including gaming companionship.

---

## What We Propose to Contribute

### Open Source Contributions (to Dolphin)

#### 1. Controller Backend for AI Input Injection
- Create `AgentControllerBackend` inheriting from controller interface
- Register in `ControllerInterface` system (opt-in via config)
- Expose shared memory interface for external input
- Implement GameCube/Wii controller mapping (A, B, X, Y, D-Pad, sticks, triggers)
- **Benefit:** Enables automation, testing, and accessibility tools

#### 2. Screen Capture API
- Add frame buffer capture hook in `VideoCommon` or `Core/HW`
- Expose captured frames via shared memory
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

**Rationale:** The AI logic is our proprietary IP. The emulator integration (controller backend, capture API, shared memory) is generic infrastructure useful to all Dolphin users.

---

## How It Works

```
Dolphin Core (C++, GPL)
├─ AgentControllerBackend (GPL)
├─ Screen capture API (GPL)
└─ Shared memory pool (GPL)
     ↓ IPC (clean license boundary)
Agent Core (Python, proprietary)
├─ Vision analysis
├─ Game state understanding
├─ Decision making
└─ x402 payments
```

### Workflow

1. User enables AI Companion via Dolphin configuration
2. Dolphin renders frames to video backend
3. Capture hook copies frame to shared memory
4. External Python process reads shared memory
5. Vision model analyzes game state
6. AI makes decisions
7. Agent writes controller state to shared memory
8. Dolphin reads controller state via `AgentControllerBackend`
9. Controller input injected into game

---

## Benefits for Dolphin

### 1. Enhanced Tooling Ecosystem
- Developers get screen capture API for debugging
- Automation tools can test games programmatically
- Recording utilities get native access to frames

### 2. Accessibility Use Cases
- Automated accessibility testing
- Controller remapping for users with disabilities
- Assistive technologies can hook into Dolphin

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

**Dolphin License:** GPLv2+ (compatible with GPLv3)

**Our Strategy:**
- Contribute: Controller backend, Screen capture API, Shared memory infrastructure → GPL
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

We want to ensure this aligns with Dolphin's goals and maintainers' expectations. Key questions:

1. **Is this aligned with Dolphin's goals?**
   - We understand Dolphin is a research emulator focused on accuracy
   - AI agents could help test compatibility and game behavior
   - We're not adding game-specific hacks or proprietary Nintendo code

2. **Should this be opt-in?**
   - We propose making AI Companion opt-in via configuration flag
   - Default behavior: Disabled
   - User must explicitly enable `enable_ai_companion = true`

3. **Performance concerns?**
   - Screen capture only when AI Companion is enabled
   - Shared memory is fast (mmap)
   - No impact on normal Dolphin operation when disabled

4. **API design concerns?**
   - Should screen capture be a callback or polling?
   - Should controller backend be event-based or state-based?
   - Any technical preferences from maintainers?

5. **Maintenance concerns?**
   - We're willing to maintain the integration code
   - We'll follow Dolphin's coding style and contribution guidelines
   - Clean git history, small PRs, thorough testing

6. **GPL license concerns?**
   - IPC separation ensures no GPL infection
   - We understand GPL requirements for contributed code
   - Open to alternative approaches if maintainers prefer

7. **Screen capture location?**
   - Where should capture hook be? (`VideoCommon`, `Core/HW`, Qt UI?)
   - Any existing capture infrastructure we should use?
   - Frame format preferences (RGBA, RGB, YUV?)

---

## Next Steps (If Approved)

1. **Phase 1: Screen Capture API**
   - Identify capture location in `VideoCommon` or `Core/HW`
   - Implement capture hook
   - Add configuration flag
   - Test with existing Dolphin games
   - Submit PR

2. **Phase 2: Controller Backend Implementation**
   - Implement `AgentControllerBackend`
   - Register in `ControllerInterface` system
   - Test controller injection (GameCube + Wii)
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
- We contribute to Dolphin long-term
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

2. **Separate fork of Dolphin**
   - Cons: Fragmentation, harder to maintain, less community benefit
   - Upstream contribution benefits everyone

3. **No contribution, only proprietary bridge**
   - Cons: Slower, less reliable, no community benefit
   - Upstream contribution is better for ecosystem

---

## Contact & Discussion

**Maintainer Discussion Points:**
- Is this aligned with Dolphin's goals?
- Any technical concerns with the proposed approach?
- Preferences for API design (callback vs polling, event vs state)?
- Any concerns about GPL license separation?
- Where should screen capture hook be? (`VideoCommon`, `Core/HW`, Qt UI?)
- Any conditions for approval?

**Next Action:**
- Open issue on GitHub requesting feedback
- Maintain PR draft for review
- Schedule discussion if needed

---

## Appendix: Technical Details

### Controller Backend Design

```cpp
// Proposed API
class AgentControllerBackend : public ControllerInterface {
public:
    AgentControllerBackend();
    ~AgentControllerBackend() override;
    
    // ControllerInterface implementation
    bool Init() override;
    void DeInit() override;
    void UpdateInput() override;
    
    // Shared memory interface
    void SetControllerState(u8 controller_id, const AgentControllerState& state);
    bool HasNewState(u8 controller_id) const;
    
private:
    // GameCube controller mapping
    void SetGCButtonState(u8 controller_id, GCPadStatus* status);
    // Wii controller mapping
    void SetWiimoteState(u8 controller_id, WiimoteEmu::Wiimote* wiimote);
};
```

### Screen Capture Design

```cpp
// Proposed API
namespace VideoCommon {
    class CaptureManager {
    public:
        static CaptureManager& GetInstance();
        
        void SetFrameCallback(std::function<void(const void* data, uint32_t width, uint32_t height)> callback);
        void EnableCapture(bool enable);
        uint32_t GetFrameWidth() const;
        uint32_t GetFrameHeight() const;
        uint64_t GetTimestamp() const;
    };
}
```

### Configuration Design

```ini
[AI Companion]
# Enable AI Companion support
Enable = false

# AI Companion settings
SharedMemoryPath = /tmp/dolphin_ai_shm
CaptureFPS = 30
InputLatencyMS = 16

[Controls]
# Enable AI controller backend
AIControllerBackend = false
```

---

## Conclusion

We believe AI Companion support would:
- Provide valuable infrastructure for Dolphin's tooling ecosystem
- Enable accessibility and automation use cases
- Benefit the community with new gaming possibilities
- Align with Dolphin's accuracy goals (testing compatibility)

We're committed to:
- Following Dolphin's contribution guidelines
- Maintaining the integration code long-term
- Respecting the GPL license
- Working transparently with maintainers

**Thank you for considering this proposal.**

---

**Last Updated:** July 6, 2026  
**Status:** Draft — Awaiting Maintainer Feedback