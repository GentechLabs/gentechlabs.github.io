---
name: hackathon-research
description: Systematic intelligence gathering for hackathon participation — schedule, prizes, eligibility, submission requirements, and resource planning. Multi-source aggregation from official sites, vault caches, and web search with structured output.
triggers:
  - "when is the next.*hackathon"
  - "hackathon schedule"
  - "hackathon requirements"
  - "eligibility.*hackathon"
  - "prize pool"
  - "submission deadline"
  - "elevenhacks"
  - "hackathon rules"
trigger_on: any  # Load when user asks about hackathon details
examples:
  - "When's the next ElevenLabs hackathon?"
  - "What are the requirements for Stripe x ElevenLabs?"
  - "Show me the hackathon schedule for May"
  - "Eligibility rules for ElevenHacks"
approach:
  - Vault-first intelligence scan (02-Labs/, 06-Content/, Hackathon-Tracker.md)
  - Official website browser navigation (hacks.elevenlabs.io)
  - JS-heavy site handling via direct URL + link clicking
  - Official rules page extraction (legal pages often behind nav)
  - Eligibility and constraints verbatim extraction
  - Prize pool and schedule collation from live pages
  - Quota/resource gap identification for build feasibility
---
# Hackathon Research

**Purpose**: Systematically gather and structure hackathon intelligence (schedule, prizes, eligibility, submission requirements) to inform participation decisions and build planning.

## Trigger Conditions

Load this skill when the user asks for:
- Hackathon dates, schedules, or countdowns
- Prize pools and reward structures
- Eligibility requirements or participation constraints
- Submission guidelines or judging criteria
- Specific hackathon series (e.g., ElevenHacks, ETHGlobal, Encode Club)

## Research Methodology

### 1. Vault-First Scan
Search local cached intelligence before web calls:
- `02-Labs/Hackathon-Tracker.md` — prioritized active/upcoming events
- `02-Labs/ElevenHacks-Research.md` — ElevenHacks-specific deep research
- `06-Content/research/elevenhacks-season*.md` — season archives
- `02-Labs/Hackathons/Active/` and `02-Labs/Hackathons/Archived/` — structured hackathon folders

**Rationale**: Vault contains curated, historically accurate data with Gentech-specific context (relevance scores, status flags). Use it as primary source; only web-verify for live updates.

### 2. Official Website Navigation
For ElevenHacks and similar series:
- Navigate to `https://hacks.elevenlabs.io/` (or equivalent official domain)
- Extract **Live now** card (current hackathon name, deadline countdown, prize amount)
- Extract **Upcoming** cards (date, sponsor, prize, time)
- Cross-reference with vault Tracker to detect new additions or date changes

**Pitfall**: Many hackathon sites are JS-heavy and may not render via simple `curl`. Use browser navigation (`browser_navigate`) and snapshot parsing rather than relying on SEO snippets.

### 3. Official Rules Extraction
Eligibility and legal constraints are typically on separate `/legal` or `/rules` pages:
- Click "Official Rules" link from footer or navigation
- If direct URL fails, try common patterns:
  - `/terms`
  - `/legal/official-rules`
  - `/rules`
- Extract the **Eligibility** section verbatim
- Key data points to capture:
  - Minimum age (usually 18+)
  - Residency restrictions (e.g., Brazil, Québec, Italy, OFAC countries)
  - Employment restrictions (government employees, sponsor affiliates)
  - Account requirements (must have active ElevenLabs account in good standing)
  - Entry limits (typically 1 entry per person per hackathon)

**Output format**: Quote the eligibility list items directly, then summarize in plain language.

### 4. Prize Structure Parsing
Capture both guaranteed prizes and season-long points system:
- Weekly hackathon prize amounts (cash + credits breakdown)
- Grand prize status (TBA or specified)
- Season leaderboard points for placements and social engagement:
  - 1st: +400, 2nd: +200, 3rd: +150
  - Most Viral/Most Popular: +200 each
  - Per social post (X, LinkedIn, etc.): +50

### 5. Submission Requirements
From the official rules "How to Enter" section:
1. Account creation on the hackathon platform
2. Build requirement using designated partner technology
3. Demo video posted on social media (platforms, hashtags, tags)
4. Submission form completion (description, links, optional repo/demo URL)

**Video format**: Usually 60-90 seconds; emphasize this is 50% of judging weight (presentation quality).

### 6. Judging Criteria
Always extract the judging breakdown from Selection section:
- Creativity/Originality (typically 40%)
- Effective Use of Technology (typically 40%)
- Presentation/Demo Quality (typically 20%)

### 7. Resource & Technology Alignment
Cross-reference hackathon focus with your current tech stack:
- ElevenLabs API access status (quota, credits)
- Partner technology requirements (Stripe, Cloudflare, Replit, etc.)
- Existing integrations in vault (check for pre-built components)
- Missing pieces that need rapid development

**Quota Alert**: If ElevenLabs TTS is involved and API quota is exhausted (0/XXX chars remaining), flag immediately and recommend:
- Activate Ambassador credits (if eligible)
- Wait for monthly free tier reset (~11th)
- Use fallback TTS provider (Edge TTS) temporarily

### 8. Pre-Build Integration Audit
Before committing to an ElevenLabs-based hackathon project:
1. **Vault check**: Look for existing TTS integration in `03-Strategies/ElevenLabs-MultiAgent-Integration/` or similar
2. **Voice inventory**: Verify agent voice assignments in `00-System/agent-voice-assignments.md`
3. **API health test**: Run a single-character generation to confirm quota > 0
4. **Provider config**: Ensure each agent's `config.yaml` has `tts.provider: elevenlabs` (not fallback)
5. **Dependency check**: Confirm `elevenlabs` SDK and `pydub` installed in Hermes venv; `ffmpeg` present

**Rationale**: Discovered integration was already complete during this session — avoided redundant work and surfaced quota block early.

## Output Structure

Provide a concise, scannable report:

```
## 🗓️ Next [Hackathon Series] Events

| Date | Sponsor | Prize | Timeline |
|------|---------|-------|----------|
| [Thu May 7] | [Cursor × ElevenLabs] | [$7,980] | [⏳ X days away] |

## 📋 Official Rules — Core Requirements

**Eligibility:**
1. [Bullet 1 text]
2. [Bullet 2 text]
...

## 🚀 Submission Process
1. Step one
2. Step two
...

## 🎯 Participation Recommendation
[High/Medium/Low] alignment with current capabilities
[Missing pieces]
[Timeline feasibility]
```

## Integration with Vault

After research completes:
- Update `02-Labs/Hackathon-Tracker.md` with new/updated events (preserve existing formatting)
- Add new deep-dive files to `02-Labs/` or `02-Labs/Hackathons/Active/` as needed
- Link to ElevenHacks-specific research files in `06-Content/research/`

## Pitfalls & Edge Cases

### JS-Rendered Official Rules
- **Symptom**: `curl` returns empty/short page; eligibility text missing
- **Fix**: Use `browser_navigate` → `browser_click` on "Official Rules" footer link → `browser_snapshot` to extract full text
- **Why**: Legal pages often require client-side rendering; direct HTTP fetch bypasses JS

### Stale Vault Cache
- **Symptom**: Vault Tracker shows event as "upcoming" but website shows it's live/ended
- **Fix**: Always verify dates against live website; recommend vault update if discrepancy found
- **Why**: Hackathon schedules change; vault is source of record but not real-time

### Quota Block on TTS Projects
- **Symptom**: ElevenLabs integration ready but API returns `quota_exceeded`
- **Detection**: ElevenLabs SDK call fails with `quota_exceeded` error or remaining characters = 0
- **Workarounds**: 
  - Check for Ambassador credits activation in ElevenLabs dashboard
  - Wait for monthly reset (~11th)
  - Switch to Edge TTS fallback (lower quality but unlimited)
  - Request emergency credits from ElevenLabs support for active hackathon
- **Impact**: TTS-dependent projects (voice agents, audio briefs) blocked until quota resolved

### Eligibility Ambiguity
- **Symptom**: Rules mention "employees of Sponsor and affiliates not eligible" but don't define "affiliate"
- **Resolution**: Check ElevenLabs corporate structure; if uncertain, assume conservative interpretation
- **Note**: Usually applies only to direct employees, not community participants

### Video Post Requirement
- **Symptom**: Rules require demo video on "at least one social media platform"
- **Platform list**: X (Twitter), LinkedIn, Instagram, TikTok (always verify)
- **Hashtag**: `#ElevenHacks`
- **Tag**: `@ElevenLabs`
- **Duration**: 60-90 seconds typical (check specific hackathon page)

## Support Files

- `references/elevenhacks-eligibility-extraction.md` — specific eligibility extraction pattern and verbatim rules from official legal page (last verified 2026-05-03)
- `scripts/check_elevenhacks_status.py` — reusable script template to programmatically fetch current live and upcoming hackathon status from official website

## Related Skills
- `elevenlabs-tts-integration` (if exists) — for quota/credit management
- `project-status-audit` — to assess existing integration state before building new
- `hackathon-lifecycle` — for ongoing monitoring during active hackathons