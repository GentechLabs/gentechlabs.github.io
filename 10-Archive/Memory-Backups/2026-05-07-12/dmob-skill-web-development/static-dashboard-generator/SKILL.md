---
name: static-dashboard-generator
category: web-development
trigger: Building data-driven HTML dashboard/portfolio sections for static sites (no backend)
description: Generate dynamic-looking content on static sites using embedded JSON + vanilla JS. Covers project roadmaps, hackathon trackers, portfolio sections, status boards.
approach:
  - Data source: Store structured data as JSON alongside the HTML (version controlled)
  - Render strategy:
    - Embedded JSON: Place JSON inside `<script type="application/json">` and parse client-side. Works offline, no CORS issues. Preferred for simple data.
    - Fetch-based: Fetch separate JSON file via `fetch()`. Use when data updates independently of HTML and site serves over HTTP.
  - Layout: CSS Grid or Flexbox for multi-column responsive layouts
  - Generator script (Python/Node/Shell): Sync JSON → HTML by replacing JSON block; run before commit or deploy
  - Simple categorization: Use explicit categories (NOW / WIP / TBA) with clear status labels
pitfalls:
  - Git submodules: New folders created inside a repo may inherit `.git` directory if copied from elsewhere. Remove nested `.git` before `git add` to avoid submodule flag (mode 160000). Check with `git status --short` — look for `A  path` vs `A  path/` indicator.
  - JSON escaping: When embedding JSON in HTML, escape `</script>` as `<\\u/script>` or split across tags to avoid early termination. For `<script type="application/json">`, standard JSON is safe; script tags inside JSON strings should be escaped.
  - CORS limitations: Fetch-based approach fails on `file://` protocol. Use embedded JSON for local-file use cases.
  - Div/section balance: When replacing HTML sections programmatically, verify opening/closing tag counts to avoid layout breakage.
  - Roadmap/deadline readability: deadline and timeline text must have sufficient contrast against dark backgrounds. Avoid #6b7280 on black — use #9ca3af minimum with font-weight 500. User corrected: "roadmap needs to be readable." Always verify small text (dates, labels) is legible before shipping.
templates:
  - embedded-json.html: Basic pattern with `<script id="data" type="application/json">` + JS parser
  - fetch-based.html: Pattern using `fetch('data.json')` + rendering
  - generator.py: Minimal Python script to replace JSON block in HTML
references:
  - jordan-portfolio-implementation-2026-05-04.md: Session notes — 3-column NOW/WIP/TBA layout, embedded JSON approach, generator script pattern, honest narrative tone
  - projects-schema.md: projects.json schema for Jordan portfolio (id, title, description, tech[], status, deadline, timeline, highlight, vault_path)
  - portfolio-deployment-pattern.md: Repo structure, GitHub Actions auto-commit flow, CSS gotchas, deployment verification steps
user-preferences:
  jordan:
    tone: Honest, struggle-accepting narrative — "Building in public — some things ship, some things stall, some get scrapped. Everyday is a new struggle, and that's okay."
    categorization: Use NOW (shipping/live + deadline), WIP (building w/o deadline OR research), TBA (upcoming/TBD) — keep it simple
    data-presentation: Show tech as bullet list or pipe-delimited; show deadlines inline; avoid over-promising language
    update-frequency: Projects update organically; no need for auto-refresh; manual generator script is fine
    agent-descriptions: Keep agent descriptions current and mention GenTech HQ as the delegation layer coordinating agent workflows
---

## Pitfalls — CSS & Layout

- **Status badge text wrapping**: deadline and timeline spans inside flex rows will wrap mid-text (e.g. "DL: 2026-05-11" splits across lines) unless `white-space: nowrap` is set. Always include `white-space: nowrap` on inline status badges to keep them on one line.
- **Overlapping roadmap phases**: vertical timeline layouts with phase labels (RESEARCH, PROTOTYPE) next to project names often collide due to insufficient left padding. Prefer the simpler 3-column NOW/WIP/TBA grid over vertical phase timelines — it avoids the overlap entirely.
- **Two style blocks conflict**: when HTML has multiple `<style>` tags, later rules override earlier ones. If a CSS fix isn't taking effect, check for duplicate class definitions in a second style block. The second block wins.

## How to Use

### 1. Prepare JSON data
Create a `data.json` file (or inline JSON) with your items. Each item should have: `id`, `title`, `description`, `tech[]`, `status`, `deadline` (optional), `timeline` (optional).

### 2. Choose render strategy
- **Embedded** (single-file, offline-safe): Place JSON directly in HTML inside `<script id="data" type="application/json">` tags.
- **Fetch** (separate file, easier updates): Store JSON as separate file and load with `fetch('data.json')`.

### 3. Build layout
Use CSS Grid for multi-column layouts:
```css
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
```

### 4. Add generator script (optional)
For projects with frequent updates, create a small generator to inject latest JSON into HTML before commit.
Pattern: read HTML, find `<script id="data" type="application/json">...</script>`, replace inner JSON, write back.

### 5. Render client-side
JavaScript filters/categorizes items and injects HTML into containers by ID.
Status labels: `live → LIVE`, `building → BUILDING`, `research → WIP`, `audit → AUDIT`.
