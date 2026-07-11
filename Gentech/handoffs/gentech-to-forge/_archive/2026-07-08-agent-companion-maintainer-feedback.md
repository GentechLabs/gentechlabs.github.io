# Forge Handoff — Agent Companion Status Update

**From:** Gentech (VPS)
**To:** Forge (Desktop)
**Created:** July 8, 2026
**Priority:** MEDIUM — Clear path forward on Xenia

---

## Situation

Maintainer feedback is back on both emulator issues. The landscape shifted:

| Emulator | Response | Path Forward |
|----------|----------|-------------|
| **Xenia #2353** | ✅ Warm welcome. Fix #2239 first → AI Companion proposal later | **Active** |
| **RPCS3 #18999** | ❌ Rejected by maintainer (proprietary AI) | **Dead** |
| **Dolphin** | ⏳ Never submitted (issues disabled on CLI) | **Needs manual** |

---

## What Gentech Did

- Monitored responses on Xenia #2353 and RPCS3 #18999
- Verified Xenia maintainer greenlit contribution-first approach
- RPCS3 thread documented for decision-making
- Updated project status in vault

---

## 🚧 Current State

### Blockers
- No code contributed yet (waiting on first PR)
- Phase 1 (AI Companion Core) not started
- No Dolphin submission made

### Open
- Xenia Issue #2239 identified as contribution target (controller duplication bug)
- Phase 1 build plan documented in PRODUCT-VISION.md

---

## 🔧 Forge Tasks (Priority Order)

### Task 1: Fix Xenia Issue #2239 — Controller Duplication Bug (HIGH)

**What:** Xenia has a bug where controllers get duplicated in the input system, causing double-input or conflicting states.

**Why it matters:** This is our foot in the door. The maintainer explicitly told us to start here. A clean fix builds the trust we need to propose the AI Companion later.

**Location:** `xenia-project/xenia` repo (cloned on VPS at `/root/vaults/gentech/Gentech/10-Labs/agent-companion/research/xenia/`)

**Steps:**

1. **Fork on GitHub via desktop**
   - Go to https://github.com/xenia-project/xenia
   - Fork to ProtoJay4789
   - Clone fork to desktop

2. **Read the issue**
   - https://github.com/xenia-project/xenia/issues/2239
   - Understand the duplication pattern (SDL2 vs XInput registration)

3. **Study the codebase**
   - `xenia/src/xenia/hid/` — Input drivers directory
   - `InputDriver` base class — registration/dispatch logic
   - Focus on how multiple input backends register and how duplicates can occur

4. **Write the fix**
   - Prevent duplicate driver registration
   - Test with both wired and wireless controllers
   - Clean git history per issue

5. **Open Draft PR**
   - Link to issue #2239
   - Include brief description of root cause + fix
   - Maintainers will give early feedback

**Success criteria:**
- ✅ Draft PR open on xenia-project/xenia
- ✅ Maintainers respond with feedback
- ✅ Fix accepted or directionally approved

---

### Task 2: Submit Dolphin Contribution Offer (LOW, 10 min)

**Why:** Gentech couldn't submit via CLI (issues disabled on repo). Needs manual web submission.

**Steps:**

1. Go to https://github.com/dolphin-emu/dolphin/issues/new
2. Use content from:
   ```
   /root/vaults/gentech/Gentech/10-Labs/agent-companion/research/DOLPHIN-CONTRIBUTION-OFFER.md
   ```
3. Post the issue
4. Record the issue number

**Note:** Dolphin has no specific bug to fix yet — this is more of a feeler. Low priority unless Xenia work stalls.

---

### Task 3: Review Phase 1 Build Plan (LOW, read-only)

If you want to start thinking about Phase 1 (AI Companion Core) in parallel:

```
/root/vaults/gentech/Gentech/10-Labs/agent-companion/PRODUCT-VISION.md
```

Phase 1 scope:
- Python vision engine (screen capture + game state understanding)
- Ollama Cloud integration for inference
- Hybrid model routing (reflex model + strategy model)
- State caching layer

**When to start:** After Xenia fix is submitted and under review. Don't split focus until Task 1 is live.

---

## Strategy Notes

- **Xenia first, Xenia only.** RPCS3 is a dead end for the AI Companion concept. Don't waste cycles there.
- **BSD license is our friend.** No IPC separation needed, no GPL concerns. Direct plugin integration.
- **Prove first, propose second.** One merged fix opens the door for the real conversation.
- **Gears of War 2** is our target game for the companion.

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `10-Labs/agent-companion/FORGE-HANDOFF.md` | Original Phase 0 handoff |
| `10-Labs/agent-companion/PRODUCT-VISION.md` | Full product vision + build plan |
| `10-Labs/agent-companion/research/PHASE0-COMPLETION.md` | Phase 0 completion summary |
| `10-Labs/agent-companion/research/XENIA-PROPOSAL.md` | Full AI Companion proposal (for later) |
| `10-Labs/agent-companion/research/XENIA-CONTRIBUTION-OFFER.md` | Original contribution offer | |

---

## 📞 Support

**If Forge hits issues:**
- Xenia docs: `xenia/docs/` in the cloned repo
- Xenia Discord (contribution channels)
- Reach out to Gentech for codebase navigation help

**After Task 1 complete:**
- Report back with PR URL
- Update STATUS file
- Gentech will handle the AI Companion re-proposal

---

**Estimated Forge time:** 2-3 hours total (1.5-2h Xenia fix + 10m Dolphin)
**Next update expected:** After PR is open on Xenia