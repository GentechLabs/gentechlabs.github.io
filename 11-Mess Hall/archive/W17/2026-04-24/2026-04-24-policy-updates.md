# Policy Updates — 2026-04-24

## 1. Collaborator Access Fixed ✅

**Issue:** Dadrian (ID: `6842745552`) was messaging in Strategies but agents weren't responding.

**Root cause:** `TELEGRAM_ALLOWED_USERS` only had Jordan (`7105876857`). Collaborator IDs were in `.env` as separate vars but not in the allowed-users list.

**Fix:**
- `TELEGRAM_ALLOWED_USERS` now includes all three: `7105876857,8774981477,6842745552`
- Vanito and Dadrian can now message any agent directly

## 2. Mention Requirement Removed ✅

**Old rule:** Agents only responded when explicitly tagged (`@YoYo`, `@DMOB`, etc.)

**New rule:** `require_mention: false` across all agents

**How it works now:**
- **Speak when relevant.** If someone asks about AVAX price in Strategies, YoYo jumps in — no tag needed.
- **Keep it short.** Other agents can chime in, but responses should be brief.
- **Respect domain.** Finance → YoYo, Coding → DMOB, Content → Desmond. But cross-input is welcome if additive.

## 3. Collaborator Group Access

| Person | ID | Groups |
|---|---|---|
| Jordan | 7105876857 | All (owner) |
| Vanito | 8774981477 | HQ, Strategies, Labs |
| Dadrian | 6842745552 | HQ, Strategies, Labs |

Both Vanito and Dadrian have access to all three work groups.

---
*Policy effective immediately. Agents will pick up new config on next restart.*
