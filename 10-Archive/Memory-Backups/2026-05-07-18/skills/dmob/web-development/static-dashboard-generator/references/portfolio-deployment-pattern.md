# Portfolio Site Deployment Pattern

## Repo Structure (ProtoJay4789.github.io)

- **Location**: `/root/ProtoJay4789.github.io` (session-agnostic, under `/root/`)
- **Single-page**: `index.html` — all CSS inline in `<style>` blocks, all JS inline in `<script>` tags
- **Data**: Projects stored as inline JS array (`const projects = [...]`) rendered by two separate render functions:
  - Filtered view (`#projects-container`) — cards with filter buttons (All/Live/Building/Research/Audit)
  - Categorized view (`#projects-now`, `#projects-wip`, `#projects-tba`) — 3-column grid
- **GitHub Actions**: `.github/workflows/update-projects.yml` auto-syncs `projects.json` from vault on push + daily cron. This means pushing can get rejected if the action committed first.

## Deployment Flow

1. Edit `index.html` locally
2. `git add index.html && git commit -m "fix: ..."`
3. `git pull --rebase origin main` (handle any Actions auto-commit conflicts)
4. `git push origin main`
5. Wait 25-30s for GitHub Pages CDN
6. Verify: `curl -s https://protojay4789.github.io/ | grep '<changed element>'`

## CSS gotchas

- Two `<style>` blocks — second overrides first for overlapping selectors
- `.deadline` and `.timeline` must have `white-space: nowrap` (flex rows cause mid-text wrapping)
- Dark theme: use `#9ca3af` for secondary text, never `#6b7280` on black backgrounds
- `.status-row` is `display: flex; gap: 10px` — child spans need nowrap to stay on one line

## Key file paths

- Local portfolio (vault copy): `/root/vaults/gentech/06-Content/portfolio-current.html`
- Live repo: `/root/ProtoJay4789.github.io/index.html`
- Data file: `/root/ProtoJay4789.github.io/data/projects.json`
