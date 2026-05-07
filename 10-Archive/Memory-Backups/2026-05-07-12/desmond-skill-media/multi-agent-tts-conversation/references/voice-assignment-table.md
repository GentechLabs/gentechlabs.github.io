# Canonical Voice Assignment Table

**Source:** `elevenlabs-tts-integration` skill (agent-voice-assignments.md)

**Last synced:** 2026-05-03

| Agent | Voice Name | Voice ID | Model |
|---|---|---|---|
| Gentech | George | JBFqnCBsd6RMkjVDRZzb | eleven_multilingual_v2 |
| DMOB | Charlie | IKne3meq5aSn9XLyUdCD | eleven_multilingual_v2 |
| YoYo | YoYo | EXAVITQu4vr4xnSDxMaL | eleven_multilingual_v2 |
| Desmond | Desmond | FGY2WhTYpPnrIDTdsKH5 | eleven_multilingual_v2 |

**Backup voices:**
- Gentech-Iroh: NqA7ncEPGGt1nDbCrDex
- IvanOnTech: ToA54GQ3jBRB2zt0fBXj

**Usage:** When generating multi-agent conversations, look up each agent's voice ID from this table. Do NOT hardcode voice IDs in scripts; instead query this file or the `elevenlabs-tts-integration` skill's assignment table.

**Update protocol:** If a new voice is cloned, update THIS file AND the `elevenlabs-tts-integration` skill's `agent-voice-assignments.md` simultaneously to avoid drift.
