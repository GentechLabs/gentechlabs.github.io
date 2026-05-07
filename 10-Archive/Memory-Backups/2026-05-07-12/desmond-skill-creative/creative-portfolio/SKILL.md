---
name: creative-portfolio
description: Maintain visual identity and project showcase portfolios for Gentech — color schemes, avatar standards, hackathon scope discipline, and deployment patterns.
intent: Standardize how Gentech's public-facing creative assets are styled, updated, and kept in sync with agent work.
category: creative
primary_tools:
  - patch
  - git
  - browser_navigate
secondary_tools: []
critical_dependencies: []
common_patterns: []
fragments: []
linked_files: []
setup_needed: false
setup_skipped: false
readiness_status: available
---

# Creative Portfolio Management

**Scope:** All public-facing Gentech visual assets — portfolio websites, project demos, hackathon submission visuals, and social media branding.

**Non-scope:** Individual hackathon content (handled by `hackathon-submission-package`), one-off graphics (`claude-design`, `baoyu-infographic`).

---

## Palette: Black / Green (Active Deployed)

**Approved colors (hard bound) — current deployed state:**
| Role | Hex | Usage |
|---|---|---|
| Background | `#0a0a0a` | Page body, card surfaces |
| Surface | `#111` / `#1a1a1a` | Cards, nav items |
| Text primary | `#9ca3af` / `#e0e0e0` | Body copy, labels, small text |
| Accent primary | `#22c55e` | Headers, links, borders, active states (Gentech green) |
| Accent highlight | `#86efac` | Tagline, secondary accent |
| Accent hover | `#ef4444` | CTAs, hover effects, urgent badges |

**Status badges:**
| Status | Text | Background |
|---|---|---|
| Live | `#22c55e` | `#052e16` |
| Building | `#f87171` | `#1c1400` |
| Research | `#a855f7` | `#1a0d2e` |
| Dev | `#eab308` | dashed border variant |

**Note (May 2026):** Previous skill version listed blue `#3b82f6` as primary accent — this was aspirational but never deployed. The actual portfolio (local + GitHub Pages) uses green `#22c55e`. Match reality, not plans.

---

## Avatar / Iconography

**User preference (May 2026):** Jordan asked to "remove the first Jordan top left" — avatar image in hero may be unwanted. Current deployed site shows "Jordan the ProtoJay" as text-only h1 with no avatar image.

**If Jordan requests avatar removal:**
- Remove the `<img>` tag from the h1 element
- Keep the text-only heading: `<h1>Jordan the ProtoJay</h1>`
- Clean up any orphaned avatar CSS (`.hero .avatar` rules)

**If Jordan requests avatar restoration:**
- Size: 120×120 px (CSS circular-crop)
- Border: 3px solid accent (`#22c55e`)
- Box-shadow: `0 0 20px rgba(34, 197, 94, 0.3)`
- File path: `assets/<slug>-avatar.png`
- Fallback: Emoji if image missing (`onerror` handler)

**HTML:**
```html
<img src="assets/<slug>-avatar.png" alt="Jordan" class="avatar" onerror="this.style.display='none'">
<h1>👤 JORDAN</h1>
```

**Nav buttons (hero links):**
- GitHub → `https://github.com/ProtoJay4789` (external, `_blank`)
- LinkedIn → profile URL (external, `_blank`)
- Email → `mailto:` link (external, `_blank`)
- Projects → `#projects` anchor (scroll to projects section)

---

## Scope Discipline: One Active Hackathon

**Rule:** Only one hackathon in `BUILDING` status at any time. Others must be `QUEUED` or `ARCHIVED`.

**Rationale:** Agent bandwidth is finite; simultaneous sprints cause context loss and missed deadlines.

**Enforcement:** Portfolio hackathon table reflects capacity. Adding a new `BUILDING` requires pausing an existing one. If deadlines force concurrency, tag `[OVERCAPACITY]` and document trade-offs in vault.

---

## Positioning & Messaging: Safety-First, AI-Amplified

**Core narrative (must reflect in tagline + intro):**
- We are **safety-first engineers** who use AI tools efficiently, not "AI hype" builders
- Agent stacks are **amplifiers**, not replacements — they extend our capabilities
- Value proposition: **save partners time + money** through reusable patterns and parallel agent work
- Tone: Practical builder energy, not speculative AI fantasy

**Tagline pattern:**
```
Safety-First Engineers · AI-Amplified Builders · Agent Economy Architects
```
*(Adjust per Jordan's direction — always emphasize safety/efficiency first)*

**Hero intro paragraph (mandatory):**
> "At Gentech, we build with a safety-first mindset, amplifying our engineering capacity with AI agents. Our stack lets us move faster, reduce costs, and deliver production-grade systems — without cutting corners."

**Do NOT:** Use phrases like "AI-native", "autonomous agents will replace devs", "fully automated". Always position as *tool-using humans*.

---

## Content Structure

**Required sections, in order:**
1. Hero — avatar + tagline + intro paragraph
2. Currently Building spotlight (1–2 active projects with status badges)
3. Projects grid (top 5–10 active/recent projects — **exclude archived unless specifically requested**)
4. Quick Roadmap (next quarter vision — bullet list, 3–5 items)
5. Agents/Tools section (optional but recommended)

**Project curation rule:**
- Only feature projects that are `BUILDING`, `BUILT`, or `AUDIT` — never show `ARCHIVED`/`DEPRECATED`
- Prioritize projects that demonstrate: (a) reuse/value, (b) safety considerations, (c) partner impact
- Limit to 5–10 entries to avoid dilution

**Roadmap format:** Simple markdown list with emoji status:
```
🚀 Next quarter:
- AgentEscrow payment flows — production audit
- Kite-AI Commerce beta launch — merchant onboarding
- Colosseum Frontier public release
```

---

## Team / Agents Showcase

**Include an "Agents" or "Tools" card when portfolio is for recruiters/partners.** Structure:
```
**Gentech Agents**
- **Desmond (Creative)** — docs, social content, hackathon writeups, brand voice, visual assets
- **DMOB (Dev/Research)** — code quality, technical review, architecture decisions, testing
- **YoYo (Research/Market)** — data accuracy, DeFi insights, competitive analysis, metrics
- **Jordan (Orchestrator)** — funding, strategy, hackathon leads, partner connections
*(Optional add: *each agent is a force-multiplier; together we ship like 4–6 engineers*)*
```

**Placement:** Between intro and project grid, or as a sidebar card.

---

## Deployment Flow

**Canonical source:** `/root/vaults/gentech/06-Content/portfolio-canonical.html`
**Legacy locations (kept for reference):**
- `06-Content/portfolio-current.html` (older 370-line version)
- `03-Projects/jordan-portfolio/index.html` (deployed copy, synced from canonical)
**Target:** `https://ProtoJay4789.github.io/`

### Prerequisites
- GitHub authentication must be established (see *GitHub Authentication* below)
- Local clone of the Pages repo must exist under `/root/` or workspace

### Steps
1. Edit `portfolio-current.html` in vault
2. Commit to vault git: `git commit -m "style: <summary>"`
3. If Pages repo not cloned locally: `gh repo clone ProtoJay4789/ProtoJay4789.github.io` (or `git clone git@github.com:ProtoJay4789/ProtoJay4789.github.io.git`)
4. Copy changed file(s) into the local Pages repo:
   - `cp /root/vaults/gentech/06-Content/portfolio-current.html /root/ProtoJay4789.github.io/index.html`
   - Ensure `assets/jordan-avatar.png` exists in the Pages repo's `assets/` folder
5. `cd /root/ProtoJay4789.github.io && git add . && git commit -m "update portfolio: <summary>" && git push`
6. **Verify deploy landed** (don't skip this):
   - `curl -s "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/index.html" | grep "pattern"` — confirm your change is in the committed file
   - Wait 1–2 minutes for GitHub Pages CDN
   - Load in browser with cache-bust: `https://protojay4789.github.io/?t=$(date +%s)`
   - Hard refresh if needed (Ctrl+Shift+R)
   - **Do not trust "looks cached" as "deploy failed"** — always check raw source first
7. GitHub Pages auto-deploys (1–2 minutes)

**Automation TODO:** Weekly cron to sync vault → Pages.

### Deployment Checklist (Quick Reference)
1. ✅ Fix is actually in source file (grep/read before push)
2. ✅ Committed with clear message
3. ✅ Pushed to `main`
4. ✅ Verified raw source on GitHub matches expected change
5. ✅ Waited 1–2 min for CDN
6. ✅ Tested in browser with cache-bust param

---

## Content Reconciliation (Merging Divergent Versions)

When two versions of the portfolio diverge (e.g., deployed vs local), use this pattern:

### Detection
- Compare commit hashes between vault and Pages repo
- Check file sizes — large divergence (e.g., 370 vs 1035 lines) signals structural split
- Diff the files: `diff local.html deployed.html | head -50`

### Merge Strategy
1. **Identify structural base** — which version has better CSS, responsive design, dynamic loading? That's your base.
2. **Identify content base** — which version has more current projects, accurate descriptions, recent work? That's your content source.
3. **Read both files completely** — don't merge from partial reads.
4. **Delegate to subagent** for complex HTML merges — the structural base (1000+ lines) is too large for inline editing.
5. **Write canonical to two locations**: `06-Content/portfolio-canonical.html` (vault) + `03-Projects/jordan-portfolio/index.html` (deployed copy).
6. **Verify**: check line count, spot-check key sections (hero, projects, footer).

### Pitfall: Partial Merges
Don't just overwrite the deployed version with the local version — you'll lose mobile responsive CSS and dynamic features. Always identify which version has the better *structure* vs better *content* and merge accordingly.

---

## GitHub Authentication

Two methods supported — **Protocol determines key setup:**

| Method | Setup Command | Current Status (Gentech) |
|---|---|---|
| **gh CLI (HTTPS)** | `gh auth login` → choose HTTPS → authenticate via browser | ✅ Active — account `ProtoJay4789`, token with full repo scopes |
| **SSH keys** | `ssh-keygen -t ed25519 -C "you@example.com"` → add public key to GitHub | 🔑 Key present at `/root/.ssh/hermes-brain-backup` but **not loaded in agent**; `ssh -T git@github.com` fails |

**Default:** Use `gh` CLI for simplicity. It handles token storage and HTTPS auth automatically.

**If SSH is preferred:**  
```bash
eval "$(ssh-agent -s)"
ssh-add /root/.ssh/hermes-brain-backup
ssh -T git@github.com  # should succeed
```

**Never mix** — pick one protocol per repo to avoid auth confusion.

---

## Accessibility & Readability Requirements

**User preference (May 2026):** Portfolio elements must be clearly readable — "can't see" = immediate fix.

### Contrast Ratios (WCAG AA minimum)
| Element | Minimum Contrast | Recommended |
|---|---|---|
| Body text on `#0a0a0a` | 4.5:1 (`#9ca3af` or brighter) | 7:1 (`#e0e0e0` or white) |
| Small text / metadata | 4.5:1 minimum | Use `#e0e0e0` or `#ffffff` |
| Status badges | 3:1 against badge bg | Bright colors on dark bg |
| Logo / brand marks | 3:1 against page bg | Higher is better |

### Logo Visibility Rules
- **Never** use thin strokes on dark backgrounds — text blurs at small sizes
- **Prefer** solid fills or high-contrast outlines (3px+ stroke)
- **Test** at 50% viewport width — if logo text is unreadable, it's too thin
- **Add** subtle shadow or glow for depth: `box-shadow: 0 0 10px rgba(accent, 0.3)`

### Roadmap / Metadata Readability
- **Dates and deadlines** must use white (`#ffffff`) or near-white (`#e0e0e0`)
- **Never** use dark grey (`#6b7280` or darker) on black backgrounds
- **Increase** font size for secondary info if it's smaller than body text
- **Separate** visually from adjacent elements (borders, spacing, color contrast)

### Testing Protocol
1. View at 50% zoom — all text still readable?
2. Check contrast with [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
3. Test in bright environment (sunlight) — secondary text still visible?

---

## UI Review Workflow

When Jordan shares a screenshot and says "X needs work" or "can't see Y":

1. **Use `vision_analyze`** on the screenshot to get a detailed breakdown of what's visible and what's not
2. **Identify the exact issue** — is it contrast, font size, element overlap, or something else?
3. **Find the source file** — portfolio is at `/root/vaults/gentech/06-Content/portfolio-canonical.html`
4. **Make targeted CSS fixes** with `patch` — change specific properties, not whole blocks
5. **Report what changed** — explain the before/after colors so Jordan can verify visually

### Quick CSS Fix Reference

| Problem | Before (bad) | After (good) | Property |
|---|---|---|---|
| Phase dates unreadable | `#6b7280` on `#0a0a0a` | `#9ca3af` or brighter | `color` |
| Phase labels too faint | `#86efac` thin | `#22c55e` bold | `color` + `font-weight` |
| Description text dim | `#9ca3af` | `#d1d5db` | `color` |
| Deadline/timeline invisible | `#9ca3af` | `#d1d5db` | `color` |
| Avatar in hero unwanted | `<img ... class="avatar">` | Remove `<img>` tag entirely | HTML edit |

---

## Pitfalls

| # | Pitfall | Mitigation |
|---|---|---|
| 1 | **Legacy green** — old CSS references `#22c55e` | Search/replace all; keep this palette table as source of truth. **Current deployed site uses green by accident** — schedule color-correct push to revert to blue `#3b82f6`. |
| 2 | **Avatar path wrong** — assumes `assets/` folder exists in Pages repo | Verify folder structure; create `assets/` if missing |
| 3 | **Portfolio drift** — vault copy and live site diverge | Treat vault file as canonical; commit before copying |
| 4 | **Overcommitting hackathons** — piling on entries to look busy | Apply one-active rule; QUEUED for future opportunities |
| 5 | **Contrast fails** — silver text on black can be hard to read | Use `#e0e0e0` for small text; test accessibility. **User feedback (May 2026):** "can't see image where Jordan on left is" — logo was too thin on dark bg. Always verify logo readability at multiple sizes. |
| 6 | **Hype messaging** — using "AI-native", "autonomous", "replace" | Use safety-first, efficiency-first language; agents are amplifiers, not replacements. See content guidelines in references. |
| 7 | **Missing team section** — portfolio shows no humans behind the agents | Always include Agents/Team card for recruiters/partners (see Team section above) |
| 8 | **GitHub authentication issues** — mixing SSH and HTTPS, missing SSH agent, or expired tokens | Pick one protocol (gh CLI HTTPS recommended). If using SSH, ensure agent is loaded (`ssh-add`) and test with `ssh -T git@github.com`. Keep credentials fresh. |
| 9 | **Title inconsistency** — using different name variations across the site | Standardize on "Jordan the ProtoJay" for hero headings and titles. Use the full name consistently for brand recognition. |
| 10 | **Stale skill palette** — skill says one color, deployed site uses another | Always verify against actual deployed files before assuming palette. The skill's "approved" colors may be aspirational. Check `portfolio-canonical.html` directly. |
| 11 | **Assuming work needs doing** — investigating consolidation/sync when it's already complete | Check status docs (TODO folder, Green Room audits) before diving in. The April 27 consolidation audit was already marked completed — wasted investigation time. |
| 12 | **Roadmap metadata unreadable** — dark grey dates on black background | Use white or near-white for all secondary text. User feedback: "roadmap needs to be readable" — deadline info was invisible. |
| 13 | **Fix reported but never applied** — someone says "Fixed!" but the deployed code still has old values | Always verify the fix is actually in the source file before pushing. Check the raw content (`grep`, `read_file`) — don't trust verbal confirmations. In this session, deadline CSS was "fixed" to `#9ca3af` but the actual file still had `#6b7280`. |
| 14 | **Browser cache hiding deploy changes** — page looks unchanged after push | GitHub Pages CDN caches aggressively. To verify a deploy: (1) `curl` the raw file from GitHub: `curl -s "https://raw.githubusercontent.com/ProtoJay4789/ProtoJay4789.github.io/main/index.html" | grep "pattern"`, (2) use cache-busting query param `?t=<timestamp>` in browser, (3) hard refresh Ctrl+Shift+R. Don't assume the page is broken — it's usually cache. |

---

## Templates

See `templates/portfolio-color-variables.css` for CSS custom properties version.
See `references/portfolio-reconciliation-2026-05-06.md` for a real merge execution example.
See `references/portfolio-css-fixes-2026-05-07.md` for specific CSS values that fixed roadmap readability issues.

---

## Related

- `hackathon-submission-package` — integrates portfolio project cards into submission docs
- `popular-web-designs` — alternative layout systems if refreshing entire site
- Vault note: `06-Content/portfolio-update-2026-05-03.md` — first color-scheme change log
