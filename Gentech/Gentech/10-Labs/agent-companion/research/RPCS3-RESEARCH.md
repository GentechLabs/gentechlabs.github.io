# RPCS3 Research Notes

**Repository:** https://github.com/RPCS3/rpcs3  
**Clone:** `/root/vaults/gentech/10-Labs/agent-companion/research/rpcs3`

---

## License & Contribution Guidelines

**License:** GNU GPL-2.0-only (mostly), some files differently licensed
- GPL license is more restrictive than Xenia's BSD
- Some files may have different licensing (check file headers)
- GPL means derivative works must also be GPL

**AI Use Policy (from README.md):**
- AI tools permitted for research and reverse engineering
- Contributors must fully own and understand submitted code
- All communication must come from humans, not AI agents
- **Pull requests opened by AI agents must include disclosure** stating scope of AI involvement
- Omitted disclosure = PR may be closed without review
- Repeated violations = ban from repository

**Contributor Requirements:**
- Coding Style: https://github.com/RPCS3/rpcs3/wiki/Coding-Style
- Developer Information: https://github.com/RPCS3/rpcs3/wiki/Developer-Information
- Contact developers via forums or Discord before contributing

---

## Architecture Analysis

### Input System (Input Layer)

**Location:** `Input/` directory

**Key Files:**
- `Emu/Io/PadHandler.h` — Base class for pad handlers
- `ds3_pad_handler.h` / `ds3_pad_handler.cpp` — DualShock 3 support
- `ds4_pad_handler.h` / `ds4_pad_handler.cpp` — DualShock 4 support
- `dualsense_pad_handler.h` / `dualsense_pad_handler.cpp` — DualSense support
- `keyboard_pad_handler.h` / `keyboard_pad_handler.cpp` — Keyboard/mouse input
- `xinput_pad_handler.h` / `xinput_pad_handler.cpp` — Xbox controller support
- `hid_pad_handler.h` — Base for HID devices

**Base Class Structure:**
```cpp
class PadHandlerBase : public PadDevice
{
    // Handlers inherit from this
    virtual ~PadHandlerBase() = default;
    
    // Each handler manages pad state for a player
};
```

**AI Companion Strategy:**
Create a new `agent_pad_handler` that:
- Inherits from `PadHandlerBase`
- Exposes API to inject controller state from Python
- Supports multiple pad instances (P1, P2, P3, P4)
- Implements PS3 button mapping (Cross, Circle, Square, Triangle, etc.)

### Screen Capture (RSX Layer)

**Location:** `Emu/RSX/Capture/`

**Key Files:**
- `rsx_capture.h` / `rsx_capture.cpp` — RSX capture functionality
- `rsx_replay.h` / `rsx_replay.cpp` — RSX replay functionality
- `rsx_trace.h` — RSX tracing

**Capture System:**
```cpp
namespace rsx {
  namespace capture {
    void capture_draw_memory(thread* rsx);
    void capture_image_in(thread* rsx, frame_capture_data::replay_command& replay_command);
    void capture_buffer_notify(thread* rsx, frame_capture_data::replay_command& replay_command);
    void capture_display_tile_state(thread* rsx, frame_capture_data::replay_command& replay_command);
  }
}
```

**AI Companion Strategy:**
1. Hook into `rsx_capture` for frame capture
2. Extract display tiles for each frame
3. Convert to RGB format for Python processing
4. Use RSX command stream for game state understanding

---

## Key Questions Answered

| Question | Answer |
|----------|--------|
| **Does RPCS3 have a plugin system?** | No formal plugin system, but pad handlers are extensible |
| **Can we hook into render pipeline?** | Yes, via `rsx_capture` system |
| **Can we inject controller input?** | Yes, by creating new `PadHandlerBase` implementation |
| **What's the code style?** | C++, clang-format, see Coding Style wiki |
| **Are there similar automation tools?** | RSX capture/replay system exists for debugging |

---

## License Considerations

**Problem:** GPL-2.0 is copyleft — derivative works must be GPL
**Impact:** Any code we contribute becomes GPL-licensed

**Options:**
1. **Contribute generic infrastructure** — becomes GPL, but that's okay
2. **Build separate bridge layer** — proprietary, communicates via IPC
3. **Dual-license approach** — GPL for emulator integration, proprietary for AI

**Recommended Strategy:**
- Contribute capture API hook and input driver registration (GPL)
- Keep AI engine, Python bridge, marketplace proprietary
- Use shared memory or sockets for communication between GPL and proprietary parts

**Why This Works:**
- GPL covers emulator interaction layer
- Proprietary covers AI logic (no GPL infection)
- IPC separation maintains clean license boundary

---

## Integration Questions for Maintainers

1. Would you accept a PR adding a pad handler for AI input injection?
2. How should we handle GPL licensing for proprietary AI components?
3. Is the RSX capture system extensible for real-time frame extraction?
4. Are there concerns about AI agents playing games via RPCS3?

---

**Last Updated:** July 6, 2026