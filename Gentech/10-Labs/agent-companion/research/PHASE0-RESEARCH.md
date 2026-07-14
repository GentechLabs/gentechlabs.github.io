# Phase 0 Research: Emulator Integration

**Status:** In Progress (Xenia researched, RPCS3/Dolphin pending)  
**Date:** July 6, 2026  
**Owner:** Gentech

---

## 📋 Research Objectives

1. Identify plugin/extension architecture in each emulator
2. Find screen capture integration points
3. Find input injection integration points
4. Review contribution guidelines and coding standards
5. Submit proposals to maintainers for approval

---

## 🎮 Xenia Research (Complete)

**Repository:** https://github.com/xenia-project/xenia  
**Clone:** `/root/vaults/gentech/10-Labs/agent-companion/research/xenia`

### **License & Contribution Guidelines**

**License:** 3-clause BSD
- Xenia code is BSD licensed
- `third_party/` code must respect original licenses
- GPL code forbidden (except development tooling)
- LGPL code strongly discouraged
- Once code enters codebase, copyright belongs to project

**Contribution Requirements (from CONTRIBUTING.md):**
- Follow [style_guide.md](../docs/style_guide.md)
- Run `xb format` before committing
- Clean git history (no "Whoops" commits)
- Each commit must compile and run independently
- Small PRs with single commit preferred
- Reference sources with reproduction steps
- No game-specific hacks (violates research mission)
- Clean git history required for `git bisect`

**Legal/Content Guidelines:**
- No references to XDKs (Xbox Development Kits)
- All information from reverse engineering legally-owned games
- Comments must describe how information was obtained
- Avoid game trademarks in code (use hex title IDs instead)
- Discussing illegal activity = permanent ban

### **Architecture Analysis**

#### **Input System (HID Layer)**

**Location:** `src/xenia/hid/`

**Key Files:**
- `input_system.h` / `input_system.cc` — Main input manager
- `input_driver.h` — Base class for input drivers
- `xinput/xinput_input_driver.h` / `xinput_input_driver.cc` — Xbox controller support
- `sdl/sdl_input_driver.h` / `sdl_input_driver.cc` — SDL gamepad support
- `winkey/winkey_input_driver.h` / `winkey_input_driver.cc` — Keyboard/mouse input

**Integration Opportunity:**
```cpp
// InputDriver is the base class we can extend
class InputDriver {
  virtual X_RESULT GetState(uint32_t user_index, X_INPUT_STATE* out_state) = 0;
  virtual X_RESULT SetState(uint32_t user_index, X_INPUT_VIBRATION* vibration) = 0;
};
```

**AI Companion Strategy:**
Create a new `AgentInputDriver` that implements `InputDriver`:
- Expose API to inject controller state from Python
- Respond to `GetState()` calls with agent-provided input
- Support multiple user indices (P1, P2, P3, P4)

**Input System Registration:**
```cpp
class InputSystem {
  void AddDriver(std::unique_ptr<InputDriver> driver);
  X_RESULT GetState(uint32_t user_index, X_INPUT_STATE* out_state);
};
```

We register `AgentInputDriver` with `AddDriver()` alongside existing drivers (XInput, SDL, WinKey).

#### **Screen Capture (GPU Layer)**

**Location:** `src/xenia/ui/` and `src/xenia/gpu/`

**Key Findings:**
- Guest output is rendered to internal buffers in `GuestOutputRefreshContext`
- Output passes through presenter layer (`vulkan_presenter.cc`, `d3d12_presenter.cc`)
- Buffers are in GPU memory (Vulkan: `VkImage`, D3D12: `ID3D12Resource`)
- Guest output format: `VK_FORMAT_A2B10G10R10_UNORM_PACK32` (10-bit RGBA)

**Integration Opportunity:**

Xenia already has capture buffer infrastructure:
```cpp
// From vulkan_presenter.cc
XELOGE("VulkanPresenter: Failed to create the guest output capture buffer");
XELOGE("VulkanPresenter: Failed to map the guest output capture memory");
```

This suggests there's existing capture functionality we can extend.

**AI Companion Strategy:**
1. Hook into `GuestOutputRefreshContext` callback
2. Copy guest output buffer to shared memory (mmap)
3. Expose buffer pointer to Python via IPC
4. Use timestamp for frame synchronization

**Presenter Flow:**
```
GPU Render → Guest Output Buffer → Presenter → Window
                                       ↓
                                 AI Companion Hook
                                       ↓
                                 Copy to Shared Memory
                                       ↓
                                 Python Process Reads
```

#### **Codebase Structure**

```
src/xenia/
├── hid/              # Input drivers (we extend here)
├── gpu/              # GPU rendering pipeline
├── ui/               # Windowing and presenter (we hook here)
├── cpu/              # PPC CPU emulation
├── kernel/           # Xbox kernel emulation
├── debug/            # Debugging tools
├── app/              # Application entry point
└── tools/            # Development tools
```

### **Key Questions Answered**

| Question | Answer |
|----------|--------|
| **Does Xenia have a plugin system?** | No formal plugin system, but input drivers are extensible via `InputDriver` base class |
| **Can we hook into render pipeline?** | Yes, via `GuestOutputRefreshContext` in presenter layer |
| **Can we inject controller input?** | Yes, by creating new `InputDriver` implementation |
| **What's the code style?** | C++17, clang-format via `xb format` command |
| **Are there similar automation tools?** | Found capture buffer infrastructure, but no existing AI automation |

### **Integration Strategy for Xenia**

#### **Screen Capture Implementation**

1. **Create `AgentCaptureDriver` in `src/xenia/hid/agent/`**
   - Hook into `GuestOutputRefreshContext` callback
   - Copy frame to shared memory region (mmap)
   - Use `kMaxActiveGuestOutputImageVersions` for triple buffering

2. **Expose capture API:**
   ```cpp
   // src/xenia/hid/agent/agent_capture.h
   class AgentCaptureDriver {
     void* GetSharedMemoryAddress();  // Python reads from here
     uint32_t GetFrameWidth();
     uint32_t GetFrameHeight();
     uint64_t GetTimestamp();
   };
   ```

3. **Python bridge:**
   - Use `mmap` module to access shared memory
   - Read RGBA10 format (convert to numpy array)
   - Pass to vision model

#### **Input Injection Implementation**

1. **Create `AgentInputDriver` in `src/xenia/hid/agent/`**
   - Inherit from `InputDriver`
   - Implement `GetState()` to return agent-provided input
   - Accept commands via shared memory or socket

2. **Agent state structure:**
   ```cpp
   // src/xenia/hid/agent/agent_input.h
   struct AgentControllerState {
     bool thumb_l_x, thumb_l_y, thumb_r_x, thumb_r_y;
     uint8_t left_trigger, right_trigger;
     bool a, b, x, y;
     bool start, back;
     bool left_shoulder, right_shoulder;
     bool left_stick, right_stick;
     bool dpad_up, dpad_down, dpad_left, dpad_right;
   };
   ```

3. **Python bridge:**
   - Write agent decisions to shared memory
   - Use protobuf or flatbuffer for serialization
   - Xenia reads on each `GetState()` call

#### **Contribution Approach**

**Open-Source Contribution to Xenia:**
- Screen capture API (expose `GuestOutputRefreshContext` hook)
- Input injection API (expose `InputDriver` registration)
- Shared memory infrastructure (generic buffer pool)
- Documentation (integration guide)

**Closed-Source (Gentech Proprietary):**
- Vision models and training data
- Agent logic and decision making
- Python bridge implementation
- Marketplace and payment integration

**Why This Split Works:**
- Xenia gets useful tooling (screen capture, input APIs)
- We get native integration (faster, more reliable)
- No license conflicts (BSD allows proprietary usage)
- We only contribute generic infrastructure

---

## 🎮 RPCS3 Research (Pending)

**Repository:** https://github.com/RPCS3/rpcs3  
**Next Action:** Clone and explore

---

## 🎮 Dolphin Research (Pending)

**Repository:** https://github.com/dolphin-emu/dolphin  
**Next Action:** Clone and explore

---

## 📊 Integration Comparison

| Emulator | Input System | Screen Capture | Plugin Architecture | Status |
|----------|--------------|----------------|---------------------|--------|
| **Xenia** | `InputDriver` base class | `GuestOutputRefreshContext` | No formal plugin, extensible via inheritance | ✅ Analyzed |
| **RPCS3** | (pending research) | (pending research) | (pending research) | ⏳ To Do |
| **Dolphin** | (pending research) | (pending research) | (pending research) | ⏳ To Do |

---

## 🚀 Next Steps for Phase 0

### **Week 1 Tasks**

- [x] Clone Xenia repository
- [x] Analyze codebase structure
- [x] Identify input integration points
- [x] Identify screen capture integration points
- [x] Review contribution guidelines
- [x] Clone RPCS3 repository
- [x] Clone Dolphin repository
- [x] Analyze RPCS3 architecture
- [x] Analyze Dolphin architecture
- [x] Document license considerations for all three emulators
- [ ] Write integration proposal for Xenia maintainers
- [ ] Write integration proposal for RPCS3 maintainers
- [ ] Write integration proposal for Dolphin maintainers
- [ ] Submit issue to Xenia repository
- [ ] Submit issues to RPCS3 and Dolphin repositories
- [ ] Get maintainer approval before coding

### **Questions for Maintainers**

**For Xenia:**
1. Would you accept a PR adding a screen capture API hook for external tools?
2. Would you accept a PR adding an input injection API for automation?
3. Are there concerns about AI agents playing games via Xenia?
4. Should this be opt-in via configuration flag?
5. Any technical guidance on shared memory implementation?

**For RPCS3:**
1. Would you accept a PR adding a pad handler for AI input injection?
2. How should we handle GPL licensing for proprietary AI components?
3. Is the RSX capture system extensible for real-time frame extraction?
4. Are there concerns about AI agents playing games via RPCS3?

**For Dolphin:**
1. Would you accept a PR adding a controller backend for AI input?
2. How should we handle GPL licensing for proprietary AI components?
3. What's the recommended approach for screen capture?
4. Are there concerns about AI agents playing games via Dolphin?

---

## 📊 Integration Compatibility Summary

| Emulator | Input System | Screen Capture | Plugin Architecture | License | Integration Complexity |
|----------|--------------|----------------|---------------------|---------|----------------------|
| **Xenia** | `InputDriver` base class | `GuestOutputRefreshContext` | Extensible via inheritance | BSD 3-clause | ✅ Low |
| **RPCS3** | `PadHandlerBase` | `rsx_capture` system | Extensible pad handlers | GPL-2.0 | ⚠️ Medium (license) |
| **Dolphin** | `ControllerInterface` | TBD (VideoCommon) | Modular controller backends | GPLv2+ | ⚠️ Medium (license, research) |

### **Key Findings**

1. **All three emulators have extensible input systems** — we can inject controller input
2. **All three have capture infrastructure** — screen capture is possible
3. **License compatibility is the main constraint** — Xenia (BSD) is easiest, RPCS3/Dolphin (GPL) require IPC separation
4. **No formal plugin systems** — we contribute infrastructure, build proprietary bridge
5. **AI-friendly maintainers** — RPCS3 explicitly allows AI use (with disclosure)

---

## 📝 Notes

- Xenia has strong anti-XDK and anti-game-specific-hack stance — must respect research mission
- RPCS3 requires AI disclosure in PRs — must be transparent about AI-generated code
- All three emulators use clang-format and have strict style guides — follow coding standards
- Clean git history is critical for all three — maintainers use `git bisect` regularly
- GPL licenses require careful separation — contribute generic infrastructure, keep AI proprietary
- Guest output formats vary — Xenia (RGBA10), RPCS3 (RSX tiles), Dolphin (unknown)

---

**Last Updated:** July 6, 2026  
**Next Research Session:** RPCS3 and Dolphin analysis