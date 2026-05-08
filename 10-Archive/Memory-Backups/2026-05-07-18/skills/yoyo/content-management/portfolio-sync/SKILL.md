---
name: portfolio-sync
trigger:
  - phrases:
      - "update portfolio"
      - "portfolio refresh"
      - "sync portfolio site"
      - "recent activity on site"
      - "update website with latest"
  - context:
      - vault paths: 06-Content/, 08-Daily/, 03-Projects/
      - outputs: public HTML for ProtoJay4789.github.io
description: Synchronize GenTech portfolio site with vault-updated project statuses,
  hackathon deadlines, and recent activity. Content extraction → HTML regeneration
  → deployment guidance.
owed-to: YoYo (Strategies)
version: 0.2.0
---

## Overview

This skill handles **periodic portfolio updates** — taking the authoritative source (the vault) and reflecting it on the public site (`https://protojay4789.github.io`).

**Core principle: Vault is the source of truth. The site is a render.** Never inject information into the site that isn't already recorded in the vault. If Jordan tells you something new, verify it appears in `08-Daily/` or `03-Projects/` first.

**Typical cadence:** After each sprint review, hackathon deadline pass, or project milestone — usually every 1–2 weeks.

## Design Principles (v2+)

The portfolio uses these consistent patterns (preserve across updates):

- **Mobile-first responsive** — CSS includes `@media (max-width: 768px)` breakpoints. New sections must be mobile-friendly (single-column grids on narrow screens).
- **Team attribution** — Every project card includes a `div.project-team` with "Team: <names>" showing owner/contributor roles. This demonstrates the agent stack as an amplifier.
- **Status badges** — Use exact CSS classes only: `status-live` (green), `status-dev` (yellow), `status-audit`/`status-research` (red), `status-prototype` (dashed yellow). Do NOT invent new classes without CSS.
- **Roadmap timeline** — Vertical timeline with green line and dots. See `references/roadmap-timeline-patterns.md` for CSS patterns and data structure. Replaced deprecated horizontal `.roadmap-step` pattern as of May 2026.
- **Hero title** — Use clean text without emoji prefixes. Format: `Jordan the ProtoJay` (not `👤 Jordan the ProtoJay`).
- **Storytelling / Methodology** — A dedicated "How Our Agent Stack Is Different" section with 4 key narratives: (1) AAE multi-layer architecture, (2) Brain system + Green Room + Mess Hall, (3) Error-first culture, (4) 4-department collaboration model. Use `.methodology-card` grid layout.
- **Tagline** — Current: "GenTech Founder · Solidity Developer · Agent Economy Builder". Positioning emphasizes **safety-first, cost-saving, agent-as-amplifier**. Any tagline change must preserve personal brand clarity.

## When To Use

- After a hackathon deadline passes or project status changes
- Sprint wrap / weekly sync where project statuses shifted
- Jordan asks "what's new on the site?" or "update portfolio"
- New project cards need to be added or existing ones refreshed
- Design refresh (responsive, new sections, storytelling additions)

## When To Use

- After a hackathon deadline passes or project status changes
- Sprint wrap / weekly sync where project statuses shifted
- Jordan asks "what's new on the site?" or "update portfolio"
- New project cards need to be added or existing ones refreshed

## What This Skill Covers

1. **Discovery** — locate current site HTML, identify repo source
2. **Content audit** — extract current sections (About, Projects, Hackathon track, Tech Stack, Focus)
3. **Vault sourcing** — pull latest data from daily syncs, project docs, deadline trackers
4. **Status reconciliation** — map vault statuses to site badge classes
5. **HTML regeneration** — rebuild index.html with updated content
6. **Deployment guidance** — provide exact push instructions (SSH/HTTPS)

## What This Skill Does NOT Cover

- Direct git push (you must have repo access)
- Design overhauls (this maintains existing CSS/structure)
- Adding new sections beyond defined template (extend with caution)

## Step-by-Step

### 1. Locate Current Site & Repo

```bash
# Fetch live site
curl -s https://protojay4789.github.io/ > /tmp/portfolio-current.html

# Source repo: ProtoJay4789/ProtoJay4789.github.io
**Vault portfolio dir:** `02-Labs/jordan-portfolio/`
#   ├── generate.py       ← reads projects.json, embeds into index.html
#   ├── projects.json     ← project data (title, id, status, etc.)
#   ├── index.html        ← the rendered site
#   └── assets/           ← images (avatar, etc.)
# NOTE: Path moved from 03-Projects/ to 02-Labs/ in May 2026
```

⚠️ **Common wrong path:** Cron jobs sometimes reference `03-Projects/portfolio-site/` — the correct path is `03-Projects/jordan-portfolio/` or `02-Labs/jordan-portfolio/` (moved in May 2026). Always verify with `ls` before running. Find it with: `find /root/vaults/gentech -name "index.html" -path "*/jordan-portfolio/*"`

### 2. Clean-Clone Deployment Pattern (Recommended)

When the portfolio repo lives **outside the vault** (separate GitHub Pages repo), use a clean clone to avoid contaminating it with vault files:

```bash
# 1. Get a fresh token via gh CLI (most reliable — credential store often fails)
GH_TOKEN=$(gh auth token 2>/dev/null)

# 2. Fresh clone into temp directory
rm -rf /tmp/portfolio-clean 2>/dev/null
git clone "https://x-access-token:${GH_TOKEN}@github.com/ProtoJay4789/ProtoJay4789.github.io.git" /tmp/portfolio-clean

# 3. Copy ONLY web files from vault source
cp /root/vaults/gentech/02-Labs/jordan-portfolio/index.html /tmp/portfolio-clean/index.html
cp -r /root/vaults/gentech/02-Labs/jordan-portfolio/assets /tmp/portfolio-clean/ 2>/dev/null || true

# 4. Commit & push from clean directory
cd /tmp/portfolio-clean
git add index.html
git commit -m "Portfolio update: $(date +%Y-%m-%d)" || true
git push origin main

# 5. Cleanup
rm -rf /tmp/portfolio-clean
```

**Why:** The vault contains many non-web files (Obsidian configs, internal docs, large binaries) that must never be pushed to the public portfolio repo. A clean clone ensures only intended files are deployed.

⚠️ **CRITICAL:** Never run `git add .` or `git commit -a` from inside the vault. The vault contains sensitive data and large files unsuitable for GitHub Pages.

⚠️ **Git auth pitfall:** The vault's remote URL embeds a token (`ghp_...@github.com`), but cloning with that token and then pushing fails — Git can't read the password from the embedded token on push. Always use `gh auth token` + `x-access-token` auth for the clean clone instead. The `git credential.helper store` approach also fails in this environment.

### 2a. Automated Regeneration via generate.py

The `generate.py` script reads `projects.json` and embeds the project array into `index.html` (replacing the `<script id="project-data">` block). Run this BEFORE deploying:

```bash
python3 /root/vaults/gentech/03-Projects/jordan-portfolio/generate.py
# Output: ✓ Portfolio regenerated — N projects embedded
```

**Note:** As of May 2026, the portfolio HTML may be edited directly for non-project changes (roadmap, hero, sections). The `generate.py` script is primarily for project card updates from `projects.json`. For roadmap or structural changes, edit the HTML directly following the patterns in `references/roadmap-timeline-patterns.md`.

**projects.json field structure** (note: uses `title` not `name`):
```json
{
  "projects": [
    {"title": "AgentEscrow", "id": "agent-escrow", "status": "building"},
    {"title": "Kite AI Governance", "id": "kite-ai", "status": "building"}
  ]
}
```

When counting projects programmatically, use `p.get('title')` not `p.get('name')`.

### 3. Parse Existing Structure

The site uses a **single-file HTML** structure with these sections:

| Section | ID/Class | Purpose |
|---------|----------|---------|
| Hero | `.hero` | Name, tagline, social links |
| About | `.section` (first) | Short bio + recent highlights |
| Projects | `.section#projects` | Project cards in grid |
| Hackathon track | `.hackathon-track` | Table with deadline + status |
| Tech Stack | `.skills` | Skill tag pills |
| Current Focus | Last `.section` | Near-future goals |

**Project card fields (keep same order):**
```html
<div class="project-card">
  <h3>😀 Emoji + Name</h3>
  <div class="tech">Tech · Stack · Here</div>
  <p>Description paragraph</p>
  <span class="status status-XXX">→ STATUS</span>
</div>
```

### 3. Extract Vault Truth

Pull **authoritative** data from these locations (in priority order):

| Site field | Vault source | Notes |
|------------|--------------|-------|
| Project status | `08-Daily/YYYY-MM-DD.md` → section headers (`## 🚀 Labs`, `## 📈 Strategies`) | Use latest daily sync |
| Hackathon deadlines | `03-Projects/HACKATHON-ROSTER-2026.md` OR `08-Daily/*` hackathon table | Verify against `03-Strategies/DEADLINES-*.md` |
| Project descriptions | `03-Projects/<ProjectName>/README.md` or `index.md` | Keep concise (1–2 sentences) |
| Recent activity | `08-Daily/YYYY-MM-DD.md` → "## TL;DR" and section summaries | Add 2–3 bullets to About if notable |
| Tech stack additions | `03-Strategies/` scripts and `06-Content/` notes | Rarely changes; review quarterly |

**Status → badge class mapping** (must match existing CSS):

| Vault status phrase | Site badge class | Visual |
|--------------------|------------------|--------|
| `IN PRODUCTION` / `LIVE` | `status status-live` | Green |
| `BUILDING` / `DEV` | `status status-dev` or `status status-building` | Yellow |
| `AUDIT` / `REVIEW` | `status status-audit` | Red |
| `SUBMITTED` | `badge badge-submit` | Green (hackathon table only) |
| `SCOPED` / `QUEUED` | `badge badge-queued` | Purple |

⚠️ **CRITICAL:** Do NOT invent new badge classes. The CSS only defines `status-live`, `status-dev`, `status-audit`, `badge-submit`, `badge-building`, `badge-queued`. Reuse or request CSS addition from Jordan.

### 4. Regenerate HTML

**Primary method:** Run `generate.py` (see Section 2a) to embed `projects.json` into `index.html`. This is the standard regeneration path for project data changes.

**Manual edits** (when project data alone isn't enough) — maintain exact same CSS and structure. Only change:

- Hero tagline (only if role shifts significantly — usually static)
- Hero title (clean text, no emoji prefix — see pitfall #9)
- About paragraph (append "Recent work:" bullets)
- Project card descriptions (3–4 sentences max, tech stack line)
- Hackathon table rows (status badge only, deadline if shifted)
- Tech stack tags (append new tools)
- Current Focus bullets (refresh quarterly)
- Roadmap section (use vertical timeline pattern from `references/roadmap-timeline-patterns.md`)
- Footer date (update to current date)

**DO NOT**:
- Rename sections
- Change color scheme (the site is Jordan's personal brand — green Emerald theme)
- Alter font families or spacing
- Reorder project cards arbitrarily (keep priority order: AgentEscrow → AAE → newest → prototype)

### 5. Save & Deploy

Save updated HTML to vault path first:

```
06-Content/portfolio-updated-YYYY-MM-DD.html
```

Then instruct Jordan:

```bash
# On machine with repo access:
cd ~/code/ProtoJay4789.github.io  # or wherever cloned
cp /root/vaults/gentech/02-Labs/jordan-portfolio/index.html ./index.html
git add index.html
git commit -m "Portfolio sync: <date summary>"
git push origin main
# GitHub Pages updates in ~30–60 seconds
```

## Pitfalls

1. **Status class mismatch** — Using a status badge not defined in CSS will render as plain text. Always verify against site's `<style>` block.
2. **Unapproved design changes** — The site uses a specific green (`#22c55e`) and card layout. Do NOT "improve" styling without explicit approval.
3. **Overwriting new sections** — If Jordan manually added a section, your regeneration will drop it. BEFORE replacing, diff your generated HTML against live site and manually preserve any custom additions.
4. **Wrong source of truth** — **VAULT IS AUTHORITATIVE.** Daily syncs and project files are truth. Do NOT use Jordan's verbal updates unless also reflected in vault files. When in doubt, check `08-Daily/` most recent file.
5. **Deployment assumption** — Never assume SSH keys are loaded or repo cloned locally. Always provide manual fallback instructions.
6. **Deadline accuracy** — Hackathon deadlines in the site must match vault sources (`03-Projects/HACKATHON-ROSTER-2026.md`, `03-Strategies/DEADLINES-*.md`). Cross-check before updating table. A single-day error breaks trust. (Discovered: Kite AI deadline was May 11 on site but vault showed May 17 — corrected.)
7. **Vault divergence / large files** — The vault repo and the GitHub Pages repo are separate repos that share git history via earlier merges. When the vault has accumulated many local commits not yet pushed, attempting `git push origin main` from the vault will fail because:
   - The repos have **unrelated histories** (merge with `--allow-unrelated-histories` brings in everything)
   - The vault contains `10-Archive/Hermes-Backups/` with binaries exceeding GitHub's 100MB limit (clang, rustc_driver.so, etc.)
   - `git pull --rebase` fails with conflicts on vault-internal files (LP-Monitor-Rules.md, cron-jobs.md)
   - **Solution:** Always use the clean-clone deployment pattern (Section 2). Never try to push from the vault directly.
8. **projects.json uses `title` not `name`** — When programmatically reading project data, the field is `title` (not `name`). Use `p.get('title')` to avoid silent None values.
9. **CSS date visibility classes** — Project card deadlines use `.deadline` class; roadmap timeline dates use `.phase-date` class. Both must be `#9ca3af` or lighter on the dark background. When fixing date readability, check BOTH classes (and any inline `color: #6b7280`). The `.phase-date` class appeared in the CSS block twice (duplicate definition) — both instances need patching.
9. **Hero title emoji prefix** — Do NOT add emoji prefixes to the hero `<h1>`. The format should be clean text: `Jordan the ProtoJay` (not `👤 Jordan the ProtoJay`). The user explicitly requested removal of the 👤 emoji in May 2026.
10. **Expired GitHub token — silent clone, failed push** — For public repos, `git clone` with an expired PAT succeeds (GitHub allows token-authenticated reads on public repos). The failure only surfaces on `push` with "Invalid username or token." `gh auth status` will show `GITHUB_TOKEN` as invalid. **Always validate the token before clone:** run `gh auth status` first; if invalid, stop and report `gh auth login` needed. Do NOT burn time trying `git config` or SSH workarounds when the token is simply expired.
11. **Cron job path drift** — The canonical portfolio path is `02-Labs/jordan-portfolio/`. Cron job configs sometimes reference `03-Projects/portfolio-site/` (the pre-May-2026 location). If `generate.py` fails with "No such file", use `find /root/vaults/gentech -name "generate.py"` to locate the current path rather than guessing.

## Verification

After proposing an update:

1. Read back changed sections to Jordan (bullet list of differences)
2. Confirm badge classes match intended status semantics
3. Verify no design drift (colors, spacing unchanged)
4. Check that all project cards still render in grid (valid HTML)
5. Update footer date to current date (format: `Month DD, YYYY`)

## Related Skills

- `strategies` — for interpreting project status and milestone semantics
- `vault` — for efficient vault navigation and file finding
- `gentech` — for understanding agent team structure and naming conventions

## Support Files

### `references/roadmap-timeline-patterns.md`
CSS patterns and data structure for the vertical timeline roadmap section. Includes the current inline-style implementation (vertical with green line and dots) and the deprecated horizontal `.roadmap-step` pattern. Documents color scheme and project data as of May 2026.

### `references/portfolio-storytelling.md`
Narrative templates for the "How Our Agent Stack Is Different" methodology section. Contains four key stories: (1) AAE multi-layer architecture, (2) Brain system + Green Room + Mess Hall, (3) Error-first culture, (4) 4-department collaboration. Use verbatim or adapt for `.methodology-card` blocks.

### `references/badge-mapping.md`
Full mapping of vault status strings → CSS classes, including edge cases (e.g., "PRODUCTION" vs "IN PRODUCTION"). Also documents pitfalls like class mismatch and status inflation.

### `scripts/portfolio-deploy-clean.sh`
Clean-clone deployment script for external portfolio repos. Clones fresh copy, copies only web files (index.html, assets/, projects.json), commits, pushes, and cleans up. Avoids vault contamination. Usage: `./scripts/portfolio-deploy-clean.sh /path/to/vault/portfolio/dir <github-token>`

### `scripts/portfolio-diff.sh`
Diff current live site HTML against proposed update to show exactly what changed. Usage: `./scripts/portfolio-diff.sh /tmp/portfolio-current.html /root/vaults/gentech/06-Content/portfolio-updated-YYYY-MM-DD.html`. Run before committing to verify changes are intentional and minimal.
