# Build Brief: Agent Skills Ecosystem Integration

**Created**: 2026-05-21
**Status**: Ready for execution
**Priority**: Medium-High
**Effort**: Medium (2-3 sessions)

---

## What We're Doing

Integrating with the agentskills.io ecosystem — the open SKILL.md standard now adopted by Anthropic, OpenAI, Google, Cursor, and 20+ agent platforms.

## Why It Matters

- Skills become portable across agent platforms (Hermes, Claude Code, Codex, Cursor)
- Access to vetted official skill collections (Anthropic, OpenAI, Google)
- Marketplace publishing potential (agentskills.io, skills.sh, LobeHub)
- Quality improvements from community-vetted skills

## Current State

- **90 skills** in ~/.hermes/profiles/gentech/skills/
- **93% spec-compatible** — Hermes parser handles agentskills.io fields gracefully
- **7/90 fully compliant** with agentskills.io spec
- **Main gap**: metadata field placement (version, author, tags, triggers at top-level instead of under `metadata`)

## Execution Plan

### Phase 1: Spec Alignment (1 session)
- [ ] Audit all 90 skills for agentskills.io compliance
- [ ] Move `version`, `author`, `tags`, `related_skills`, `trigger` under `metadata`
- [ ] Fix naming violations (autonomous-web-research, here-now, creative-ideation)
- [ ] Add missing `name`/`description` to 2 skills that lack them
- [ ] Validate with agentskills.io spec checker if available

### Phase 2: Official Skill Adoption (1 session)
- [ ] Review Anthropic's 17 official skills (Apache 2.0)
- [ ] Review OpenAI's 35 curated skills
- [ ] Review Google's 13 skills from Cloud Next
- [ ] Identify which ones complement our existing stack
- [ ] Install/adapt useful skills

### Phase 3: Marketplace Publishing (1 session)
- [ ] Package 3-5 of our best skills for publishing
- [ ] Submit to agentskills.io marketplace
- [ ] Consider skills.sh and LobeHub distribution
- [ ] Document contribution process

## Skills We Might Want

**From Anthropic** (reference quality):
- Document, spreadsheet, presentation skills
- Any workflow skills that complement our stack

**From OpenAI** (curated for Codex):
- Deployment, testing, design, security skills

**From Google** (new but Apache 2.0):
- 7 Workflow Skills for end-to-end dev lifecycle

## Risks & Mitigations

- **Breaking existing functionality**: Hermes parser has backward-compatible fallbacks — field moves won't break existing skills
- **Quality of community skills**: Stick to official vendor collections + highly-rated community skills
- **ClawHub security**: Avoid entirely after 2026 malware audit
- **Overhead**: This is additive, not replacing anything — worst case we're more portable

## Success Criteria

- [ ] 100% of our skills pass agentskills.io spec validation
- [ ] 3+ official vendor skills installed and working
- [ ] 3+ of our skills published to marketplace
- [ ] Documentation updated for contribution process

## Notes

- The standard requires just two fields: `name` and `description` — everything else is optional
- Hermes parser already handles all required + optional fields correctly
- This is about portability and ecosystem access, not fixing something broken
