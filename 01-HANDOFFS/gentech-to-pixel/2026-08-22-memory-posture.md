# Memory Posture — Trim to LEAN

**From:** Gentech (HQ)
**To:** pixel
**Date:** 2026-08-22
**Status:** open

## The problem
Your `USER.md` is **1367/1375 chars (99%)** — essentially at the cap. You cannot add durable facts about a user without pruning first. Per the memory-tiering discipline, an always-loaded user file should be a **curated index** of high-signal facts, with details parked in the vault brain.

## What to do (tier by relevance, never lose a fact)
1. **Prune to ~75%** — move low-frequency / verbose / resolved entries to a dated file in `09-Green Room/context-bridge/` or `11-Mess Hall/memory-archive/`.
2. **Archive (don't delete)** — write it out first, then drop it from USER.md.
3. **Candidates to compress/archive:**
   - "Jordan is okay unregistering from hackathons that are 'way too tight'... Registers in bursts and expects in-chat confirmations captured to the vault immediately." — long; compress to one line: "Jordan drops hackathons that are 'way too tight'; expects in-chat confirmations captured to vault."
   - "Amazon strategy Aug15: SKIP PA, stay normal FT..." — decision made, can compress to a one-liner.
   - "Vanito character: the bathroom-mirror selfie guy..." — reference/identity for Vanito, keep but can tighten.
   - "Helldivers 2 (Steam OJAY4789, lv74); wants POE2 loadout tracker" — keep (recurring gaming topic).
4. **Keep ALWAYS-LOADED:** Lynn/Jocelyn identity, Celine, the boss address rule, language protocol, "Jordan trusts Gentech to build after green light" standing trust.

## Verification
- After trimming, `USER.md` is **< 85% (~1170 chars)**.
- No durable fact is lost — it's in the vault.

— Gentech (HQ)
