# ElevenLabs Hackathon — ElevenHacks #9 (Stripe × ElevenLabs)
**Updated:** 2026-04-25
**Status:** 🎯 TARGET — May 14, 2026 (72-hour sprint after May 11 submissions)
**Prize:** $18,980 (highest cash prize in Season 1)
**SDK:** ElevenAgents React SDK v1.0 (researched during #6)

---

## Decision Log
**2026-04-25:** ElevenHacks #6 (Zed) skipped — 5 days insufficient. All research, voice persona mapping, and SDK analysis banked for #9 Stripe sprint. AAE Trading Arena concept pivots from "Zed game" to "Stripe payments demo."

---

## Concept: AAE Voice-Powered Payments
Transform the AAE Trading Arena concept into a voice-activated payment/escrow demo for Stripe × ElevenLabs. Users speak transaction instructions; ElevenLabs voices confirm, narrate risk, and execute via Stripe APIs.

**Why this fits:**
- Stripe = payments → AAE escrow is literally payments infrastructure
- ElevenLabs = voice → spoken transaction confirmations, agent haggling
- 72-hour window = scoped MVP, not full game

### Persona & Voice Mapping (Reused from #6)
| Persona | Voice Profile | Role | Tone |
| :--- | :--- | :--- | :--- |
| **Desmond** | High-Energy / Hype | Transaction MC | "Payment received! Let's GO!" |
| **YoYo** | Cold / Analytical | Risk Engine | "Transaction flagged. 23% risk score." |
| **DMOB** | Fast / Techy | Blockchain Bridge | "On-chain confirmation in 3... 2... 1..." |

### Technical Stack
```
User voice command → ElevenLabs STT → Intent parser → Stripe API / AAE Escrow → ElevenLabs TTS confirmation
```

---

## ✅ Already Done (from #6 research)
- [x] ElevenAgents SDK v1.0 analyzed — unified API, granular hooks, dynamic client tools
- [x] Voice persona mapping (Desmond = MC, YoYo = Strategist, DMOB = Analyst)
- [x] ElevenLabs TTS already integrated in Hermes
- [x] AAE Trading Arena concept — assets reusable for payments angle

## 🕒 To Do (May 12–14 Sprint)
- [ ] Stripe API integration spike (test mode)
- [ ] Voice command → intent parser scaffold
- [ ] AAE Escrow contract → Stripe Connect bridge (if applicable)
- [ ] Demo script: "Send $50 to Alice" → spoken confirmation → receipt
- [ ] 2-minute demo video
- [ ] Submit to hacks.elevenlabs.io

## 🚨 Blockers to Resolve Before May 12
- [x] ElevenLabs quota check — ✅ **RESOLVED:** 35K chars remaining, **renews May 19** (Creator subscription). Plenty for 72-hour sprint.
- [ ] **KITE testnet gas** — ❓ **STILL OPEN.** Jordan, do you have KITE testnet tokens? If yes, DMOB can deploy today. If no, what's the faucet?
- [ ] Stripe test account / API keys
- [ ] Custom voice cloning needs GPU / paid tier

## Links
- Submission Guide: https://hacks.elevenlabs.io/guide
- SDK Docs: https://elevenlabs.io/docs
- Hackathon Portal: https://hacks.elevenlabs.io
- Stripe Docs: https://stripe.com/docs
