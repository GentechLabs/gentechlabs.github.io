# Dolphin Research Notes

**Repository:** https://github.com/dolphin-emu/dolphin  
**Clone:** `/root/vaults/gentech/10-Labs/agent-companion/research/dolphin`

---

## License & Contribution Guidelines

**License:** GPLv2+ (compatible with GPLv3)
- Most source code: GPLv2+
- Some parts derived from other projects with different licenses
- Overall: GPLv3-compatible
- SPDX tags in each file specify exact license

**Contribution Requirements:**
- Contributing.md has detailed guidelines
- CODE_OF_CONDUCT.md applies
- CMake-based build system
- Multi-platform support

---

## Architecture Analysis

### Input System (InputCommon Layer)

**Location:** `Source/Core/InputCommon/`

**Key Directories:**
- `ControllerInterface/` — Controller interface implementations
  - `SDL/` — SDL gamepad support
  - `Win32/` — Windows input support
  - `Xlib/` — Linux input support
  - `evdev/` — Linux evdev support
  - `Wiimote/` — Wii Remote support
  - `SteamDeck/` — Steam Deck support
- `ControllerEmu/` — Emulated controller layer

**Key Files:**
- `ControllerInterface/ControllerInterface.h` — Base controller interface
- `ControllerInterface/Wiimote/WiimoteController.h` — Wii Remote support
- `ControllerEmu/ControllerEmu.h` — Emulated controller
- `Core/HW/SI/SI_DeviceGCController.h` — GameCube controller device

**AI Companion Strategy:**
Dolphin has a modular controller interface system:
1. Create new `AgentControllerBackend` in `ControllerInterface/`
2. Inherit from controller interface base class
3. Implement GameCube controller mapping (A, B, X, Y, D-Pad, sticks, triggers)
4. Support multiple controller instances

**Controller Interface Pattern:**
```cpp
// Multiple controller backends supported
// Can add new backend for AI input injection

class ControllerInterface {
    // Backends register here
    // Each backend provides input for emulated controllers
};
```

### Screen Capture (Video Layer)

**Location:** Not yet fully analyzed

**Preliminary Findings:**
- Dolphin has extensive capture systems for debugging
- Video capture likely in `Source/Core/VideoCommon/` or `Source/Core/Core/HW/`
- Need deeper investigation

**Files to Investigate:**
- `Source/Core/VideoCommon/` — Video rendering common code
- `Source/Core/Core/HW/` — Hardware emulation
- `Source/Core/DolphinQt/` — Qt UI (may have capture hooks)

---

## Key Questions Answered

| Question | Answer |
|----------|--------|
| **Does Dolphin have a plugin system?** | Modular controller interface, but no formal plugin system |
| **Can we hook into render pipeline?** | Not yet fully analyzed (screen capture needs more research) |
| **Can we inject controller input?** | Yes, by creating new controller backend |
| **What's the code style?** | C++, CMake-based, see Contributing.md |
| **Are there similar automation tools?** | Not yet identified |

---

## License Considerations

**Problem:** GPLv2+ is copyleft — derivative works must be GPL
**Impact:** Any code we contribute becomes GPL-licensed

**Same Strategy as RPCS3:**
- Contribute generic infrastructure (GPL)
- Keep AI engine, Python bridge, marketplace proprietary
- Use IPC separation to maintain clean license boundary

**Why This Works:**
- GPL covers emulator interaction layer
- Proprietary covers AI logic (no GPL infection)
- IPC separation maintains clean license boundary

---

## Integration Questions for Maintainers

1. Would you accept a PR adding a controller backend for AI input?
2. How should we handle GPL licensing for proprietary AI components?
3. What's the recommended approach for screen capture?
4. Are there concerns about AI agents playing games via Dolphin?

---

## Next Research Steps

- [ ] Analyze `Source/Core/VideoCommon/` for screen capture hooks
- [ ] Analyze `Source/Core/Core/HW/` for frame buffer access
- [ ] Identify frame buffer format and memory layout
- [ ] Document capture infrastructure

---

**Last Updated:** July 6, 2026