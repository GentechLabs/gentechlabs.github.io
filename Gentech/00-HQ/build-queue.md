# Build Queue

> Rebuilt 2026-07-11 after git sync cleanup. Items preserved from memory.

---

### 28. PixelRAG — Visual Search Demo for Jordan 📸
**Status**: ✅ Installed on Forge's laptop (RTX 3070, CUDA verified). Agent Kit tool built.
**Forge**: Run the demo, show Jordan what visual search looks like.
**Location**: `10-Labs/pixelrag-tool/pixelrag-demo.py`

**Steps:**
- [ ] Run `pixelrag-demo.py` on GPU laptop — captures Vanito's Hub + Jordan's Hub + GenTech Atlas
- [ ] Share output JSON + screenshot results with Jordan
- [ ] Discuss integration — agent chat, marketplace HUD, city pack discovery

**Context:**
- PixelRAG is a Berkeley SkyLab project, Apache 2.0, 694 stars
- Uses Qwen3-VL-Embedding to visually search web pages
- Needs CUDA GPU (RTX 3070+) — Forge's desktop is the only machine with one

---

### 29. Local TTS & Voice Cloning Pipeline 🎤
**Status**: 🔵 Researched — ready for Forge when laptop is operational.
**Goal**: Replace paid ElevenLabs API with local GPU-powered TTS/voice cloning.

**Stack (RTX 3070):**
| Tool | Use Case |
|------|----------|
| **Gepard 1.0** | Real-time streaming TTS, voice cloning |
| **OpenVoice** | Instant clone on-the-fly (10s audio) |
| **StyleTTS 2** | Fast batch production |
| **Coqui XTTS v2** | Long-form narration |

**Steps:**
- [ ] Install & validate Gepard 1.0 first (Apache 2.0, 555M params)
- [ ] Install OpenVoice for instant cloning
- [ ] Install StyleTTS 2 for batch production
- [ ] Wire as local FastAPI endpoints

**Context:** ElevenLabs Creator plan = $22/mo, 121K chars. Local = $0/mo after setup.

---

### 30. Deploy Subscription Hub to gentechlabs.net 🚀
**Status**: 🔵 Ready — HTML built, handoff doc written.
**Goal**: Turn `gentechlabs.net` into a commercial storefront with Q402 subscription tiers.

**Tiers:**
| Plan | Price | What |
|------|-------|------|
| Basic | $3/mo | LP alerts, Atlas packs, journal |
| Pro | $10/mo | API access, signals, registrations |
| Max | $25/mo | Build requests, early access |
| Vanito Music | $3/mo | Tracks + early releases |
| Vanito Vault | $10/mo | Music + anime + exclusives |

**Files (need recreating after git sync):**
- `gentech-ops/gentechlabs-subscription-hub.html`
- `Gentech/handoffs/gentech-to-forge/2026-07-11-gentechlabs-subscription-deploy.md`

---

### 31. GenTech Character API — Consistent Character Generation 🎨
**Status**: 🔵 Proposed — ready for Forge prototyping.
**Goal**: x402 endpoint that takes a reference image + prompt and outputs character-consistent generations.

**Stack:** Stable Diffusion + IP-Adapter + ControlNet + LoRA (all open-source)

**Pricing:**
| Tier | Price | What |
|------|-------|------|
| Standard | $0.05/gen | Character-consistent image from ref |
| Batch | $0.03/gen | 10+ at once |
| Animation | $0.10/frame | Consistent across frames |

**Steps (Forge):**
- [ ] Research IP-Adapter + SD 1.5 pipeline on RTX 3070
- [ ] Install SD 1.5 + IP-Adapter + ControlNet
- [ ] Test with KAGE character sheet — verify consistency
- [ ] Wrap as FastAPI + x402 endpoint
- [ ] Deploy on BlockRun Modal for 24/7 production

**Context:** Market gap — AI agents describe from text, character morphs every time. No one offers a "lock this character" x402 endpoint.

---

### Quick Reference — Vault Handoffs (may need recreation)
| Handoff | Purpose |
|---------|---------|
| `handoffs/gentech-to-forge/2026-07-11-forge-handoff.md` | Existing — survived git sync |
| `handoffs/gentech-to-forge/2026-07-11-gentechlabs-subscription-deploy.md` | Needs recreating |
