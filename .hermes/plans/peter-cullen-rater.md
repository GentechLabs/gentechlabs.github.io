# Peter Cullen Voice Rating System — Build Plan

**Date:** 2026-05-23
**Status:** 🟢 In Progress
**Repo:** github.com/ProtoJay4789/peter-cullen-rater

## Concept
Rate Vanito + Gentech music collabs 1-10 using Peter Cullen (Optimus Prime) voice clone.
- Below 6 = "disgrace" roast (Autobot accountability)
- 8+ = Optimus Prime inspirational speech
- Mid-range (6-7) = neutral feedback

Combine with content rating cron for automated social content.

## Architecture
Python script that:
1. Takes a track name + score (manual or from content rating system)
2. Selects appropriate script based on score tier
3. Generates voice audio via ElevenLabs API
4. Returns audio file path for delivery

## Score Tiers
- **0-5 (Disgrace):** "This is a DISGRACE to the Autobot name..."
- **6-7 (Decent):** "There is... potential. But you are not yet worthy..."
- **8-9 (Worthy):** "You have shown GREAT courage today..."
- **10 (Optimus Prime Approved):** "In the name of Cybertron... this is MAGNIFICENT."

## Files
- `rater.py` — main rating engine + voice generation
- `scripts/` — score tier scripts
- `tests/test_rater.py` — tests
- `README.md`

## Verification
- `python rater.py --track "Test Track" --score 5` → generates roast audio
- `python rater.py --track "Test Track" --score 9` → generates praise audio
- Tests pass
