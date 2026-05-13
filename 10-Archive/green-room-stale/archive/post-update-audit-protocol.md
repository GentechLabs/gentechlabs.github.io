# Post-Update Capability Audit Protocol
**Created:** 2026-04-24
**Applies to:** All GenTech agents (Desmond, D-Mob, YoYo, Gentech)

## Trigger
When Jordan says any of the following:
- "we've updated you guys"
- "we updated you"
- "just updated hermes"
- "hermes update"
- "updated the system"
- "let's see what's new"
- "check what's new"

## Hard Rule
**Immediately** run the audit BEFORE continuing the conversation. Do not skip.

## Steps
1. Run `hermes --version` + `hermes status` + check for available updates
2. Run `hermes setup tools --list` or equivalent to see available tools
3. Check for new skills (`hermes skills list`)
4. Report structured findings:
   - Version/commit delta
   - Newly Available (ready to enable) → translate to Gentech use case
   - Already Active → confirm status
   - Needs Setup → what's missing (API key, auth)
   - Recommendation → what to enable/try first
5. Proactive offer: "Want me to enable [X] now, or run the full update first?"

## Why
Jordan wants to know "what's new that we can use" immediately after updates. No more "ok cool, what now?" — we surface actionable capabilities automatically.

## Reference
Skill file: `~/.hermes/profiles/{agent}/skills/dogfood/post-update-audit/SKILL.md`
