---
name: link-research-summary
description: "Research and summarize links Jordan shares — GitHub repos, X/Twitter posts, articles. Fetch content efficiently, extract key info, provide structured analysis with context and implications."
version: 1.0.0
author: Gentech
license: MIT
tags: [research, summary, github, twitter, link-analysis]
---

# Link Research & Summary

When Jordan shares a URL, research it and provide a structured summary. Optimize for speed and depth.

## URL Type Detection

| URL Pattern | Method | Tool |
|---|---|---|
| `github.com/{owner}/{repo}` | GitHub API | `curl` + `python3` |
| `x.com/{user}/status/{id}` or `twitter.com/...` | xurl CLI | `xurl read` |
| Other URLs | Browser | `browser_navigate` |

## GitHub Repos (Primary Pattern)

Use the GitHub REST API — no auth needed for public repos, no rate limit issues for occasional requests.

### Step 1: Get repo metadata + README in parallel

```bash
# Metadata (stars, license, language, description)
curl -s "https://api.github.com/repos/{owner}/{repo}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for key in ['full_name', 'description', 'stargazers_count', 'forks_count', 'language', 'license', 'created_at', 'updated_at', 'topics']:
    print(f'{key}: {data.get(key, \"N/A\")}')"

# README content
curl -s "https://api.github.com/repos/{owner}/{repo}/readme" | python3 -c "
import json, sys, base64
data = json.load(sys.stdin)
if 'content' in data:
    print(base64.b64decode(data['content']).decode('utf-8')[:8000])"
```

### Step 2: Analyze & Summarize

Structure the summary as:
1. **What it is** — one-liner description
2. **Key features/capabilities** — bullet list
3. **Why it matters** — context, positioning vs alternatives
4. **Relevance to GenTech** — how it connects to our projects
5. **Action** — save to vault? Try it? Bookmark?

### Pitfalls
- README truncation at 8000 chars is usually fine; the important stuff is in the first section
- If README is missing, check the repo description and topics for context
- Some repos have massive READMEs — focus on Quick Start and Features sections
- `license` field can be null — note "no license" explicitly

## Search Engine Blocking & Vision Failures

### CAPTCHA Blocking on Search Engines

Google, DuckDuckGo, and Bing frequently block headless browsers with CAPTCHAs. When this happens:

1. **Skip search engines entirely** — go directly to the target site
2. For model/library research → `huggingface.co/{org}` or `huggingface.co/models?search={query}`
3. For code → `github.com/{org}` or `github.com/search?q={query}`
4. For docs → the project's own docs site

Direct site browsing is often faster than search anyway, since you land on the exact content instead of a results page.

### `browser_vision` Model Failures

`browser_vision` can fail with "Not supported model" errors when the configured vision model is unavailable or misconfigured. The screenshot is still captured even when analysis fails.

**Fallback pattern:**
1. Check if `browser_vision` returned a `screenshot_path` — the image exists even if analysis failed
2. If vision fails, describe the image content based on context clues (page title, URL, surrounding elements)
3. For image analysis, try alternative approaches: `browser_get_images` to confirm the image loaded, then describe based on context
4. If the image is critical, ask the user to describe it or paste the text

**Known failure mode:** `gemini-3-flash-preview` returns 400 — this is a provider config issue, not a bug in the browser tool.

## X/Twitter Posts

Use `xurl read` — faster and more reliable than browser scraping.

### Step 1: Read the post

```bash
xurl read https://x.com/{user}/status/{id}
```

This returns JSON with tweet text, author, engagement metrics, and any quoted tweets.

### Step 2: If the post links to something (GitHub repo, article), follow that link too

### Step 2: Summarize

Structure as:
1. **What was posted** — core content
2. **Context** — why it matters, who posted it
3. **Engagement** — views, likes, reposts (signals importance)
4. **Implications** — what this means for us
5. **Action** — save to vault? Monitor? Follow up?

### Pitfalls
- Tweet images often contain key context (title cards, charts) that `xurl read` doesn't capture — use `browser_vision`
- Quoted tweets may have the real substance — read both the main tweet and the quote

## Articles & Blog Posts

Use `browser_navigate` → extract content → summarize.

### Step 1: Extract content

Use the fast JS extraction from the "Other URLs" section above. If the page has an `<article>` tag, pull it directly.

### Step 2: Summarize

Structure as:
1. **What it is** — title, author, publication, date
2. **Core thesis** — the main argument or technical contribution
3. **Key details** — bullet points of the important specifics
4. **Context & positioning** — how it fits into the broader landscape
5. **Relevance to GenTech** — what this means for our projects/builds
6. **Action** — save to vault? Build on it? Bookmark for later?

### Pitfalls
- Some blog posts require cookie consent banners — dismiss them before extracting
- Medium posts may have paywall truncation — check if full content loaded
- For technical deep dives, focus on architecture/protocol sections, skip marketing fluff
- Dates matter — check if the content is current (tech moves fast)

Fall back to `browser_navigate` → extract → summarize.

### Fast article extraction

For blog posts with semantic HTML, extract text via JS console — much faster than scrolling snapshots:

```javascript
// Try article tag first (most blogs/docs)
document.querySelector('article')?.innerText?.substring(0, 15000)

// Fallback: main content area
document.querySelector('main')?.innerText?.substring(0, 15000)

// Last resort: full body
document.body.innerText.substring(0, 15000)
```

Increase the 15000 limit for longer technical articles. If JS extraction returns nothing useful, fall back to `browser_snapshot` → read from snapshot.

### "Add to vault" from conversation context

When Jordan says "add to vault" referencing content already in the chat (not a fresh URL):

1. **Reconstruct the source URL** from the conversation context if possible
2. **Fetch the full article** — the message in chat is often truncated
3. **Search the vault** for existing related notes before creating new ones
4. **Create the note** with full structured content (not just the truncated chat message)
5. **Cross-reference** from any related existing notes

### Tweet images/graphics

When X posts include images, charts, or graphics that aren't in the tweet text, use `browser_vision` to read them:

```
browser_vision(question="What does the image/graphic in this tweet show?")
```

This catches visual context that `xurl read` misses — title cards, infographics, charts, screenshots.

## Vault Integration

When Jordan says "add to vault", "save this", or shows sustained interest, save a structured research note to the vault.

### Step 1: Find existing related notes

Before creating a new note, search the vault for related content:

```bash
# Search by filename
find "$VAULT" -name "*.md" -iname "*keyword*"

# Search by content
grep -rli "keyword" "$VAULT" --include="*.md"
```

Read any related notes to understand what's already documented and avoid duplication.

### Step 2: Create the research note

Save to the appropriate vault location:

| Topic | Location |
|-------|----------|
| Tech tools / protocols | `03-Projects/{ProjectName}/` (e.g., `03-Projects/AAE/`) |
| Hackathon research | `03-Projects/Hackathons/` |
| DeFi/market data | `00-HQ/Market/` |
| Travel | `00-HQ/Travel/{Country}/` |
| General research | `03-Projects/Research/` (create if needed) |

**Note naming convention:** `kebab-case-descriptive-name.md`

**Required frontmatter in vault notes:**
```markdown
# Title

**Source:** [source description](URL)
**Date:** YYYY-MM-DD
**Author:** author name
**Tags:** #tag1 #tag2

---

## TL;DR
(2-3 sentence summary)

---

## Key Sections
(structured content with tables, headers, bullet points)

---

## GenTech Relevance
(1-2 paragraphs: how this connects to our projects/builds)

## Open Questions
(anything unanswered)

## Sources
(links to original materials)
```

### Step 3: Cross-reference existing notes

If related notes were found in Step 1, update them with cross-references:

```markdown
## Related
→ See [[path/to/new-note]] (date, source description)
```

For approval/tracking notes, update open questions with answers found in the new research.

### Step 4: Sync vault

```bash
cd /root/vaults/gentech && ob sync
```

## Strategic Evaluation Mode

When Jordan asks "do we need this", "should we build on this", "dig deep and see if we will need this", or similar evaluative questions — go beyond summary into a structured assessment.

### Additional Steps (beyond standard summary)

1. **Product viability probe** — Try to access the actual product, not just the landing page:
   - Test `app.{domain}`, `cloud.{domain}`, `docs.{domain}`, `api.{domain}` — DNS failures = red flag
   - Check if there's a working API or just a "Schedule a Demo" page
   - Note: enterprise-only sales model vs self-serve developer access

2. **GitHub deep check** (beyond repo metadata):
   - Team size (People tab) — small team + enterprise claims = concern
   - Follower count — low followers = low traction
   - Recent commit activity — are they actually building?
   - Issue/PR activity — community engagement?

3. **Vault + session cross-reference** — Before writing the assessment:
   - Search vault for existing notes on the project, team, or competitors
   - Read related notes to understand what's already documented
   - Cross-reference with active hackathon projects and AAE architecture
   - Search session history with `session_search` for dynamic context — recent decisions, ongoing work, team discussions that aren't in the vault yet (e.g., "search for Kite AI", "search for AgentEscrow sprint status")

4. **Strategic verdict** — End with a clear recommendation:
   - **Build on it** — actively integrate into our stack
   - **Watch** — interesting but too early / wrong chain / wrong buyer
   - **Ignore** — not relevant or vaporware
   - Include specific reasons tied to our current stack (Solana, AAE, hackathon deadlines)

### Vault Save Format for Evaluations

Save strategic assessments to `02-Labs/Assessment-{ProjectName}-deep-dive-{date}.md`:

```markdown
# {Project} — Deep Dive Assessment

## What They Are
(1-2 paragraphs)

## The Product
(What actually exists vs what's claimed)

## GitHub Analysis
(team size, repos, activity, red flags)

## Red Flags / Concerns
(numbered list)

## Relevance to GenTech / AAE

### What Overlaps
(bullet points)

### What Doesn't Fit
(bullet points)

### Verdict: **Watch / Build On / Ignore**

(1-2 paragraphs with reasoning)

## Action Items
- [ ] specific next steps
```

### Pitfalls
- Don't confuse marketing copy with shipped product — always probe for working endpoints
- "Launching today" is marketing language, not proof of deployment
- Testimonial from a single company is not social proof
- Cross-chain integration adds complexity — factor this into relevance assessments

## Output Style

- Use tables for comparisons
- Use emoji sparingly for section headers
- Keep summaries scannable — Jordan should get the gist in 10 seconds
- Always end with a clear "what next" or action suggestion
