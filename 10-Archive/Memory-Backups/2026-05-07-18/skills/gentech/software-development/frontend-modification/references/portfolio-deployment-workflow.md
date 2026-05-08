# Portfolio Deployment Workflow

**Repo:** `ProtoJay4789/ProtoJay4789.github.io`
**Local path:** `~/portfolio/`
**Live URL:** `https://protojay4789.github.io/`
**Branch:** `main` (auto-deploys on push)

## Deployment Pipeline

1. Edit `~/portfolio/index.html` (single-file static site)
2. `git add index.html && git commit -m "description"`
3. `git pull --rebase && git push`
4. Verify live at `https://protojay4789.github.io/?v=N` (cache-bust)

## Known Gotchas

### Git index staleness after patch tool
The `patch` tool modifies files but git may not detect changes:
```bash
git update-index --refresh   # forces git to re-check file hashes
git add index.html
git status                   # should now show "modified: index.html"
```

### Remote push rejection
If another agent pushed first:
```bash
git pull --rebase && git push
```

### CSS cache on GitHub Pages
GitHub Pages CDN caches aggressively. After CSS fixes:
- Append `?v=N` to URL for fresh load
- Or use `browser_console` to verify computed styles directly

## Architecture Notes

- **Two `<style>` blocks**: Head (lines 7-351) + inline in section div (lines 764-957)
- **JS-rendered project cards**: Projects data is inline JSON, rendered by `renderProjects()` function
- **Filter system**: Status filter buttons (All/Live/Building/Research/Audit) via data-filter attributes
- **Projects link**: Header `🚀 Projects` button → `https://github.com/ProtoJay4789` (opens in new tab)

## CSS Class Reference

| Class | Purpose | Color |
|-------|---------|-------|
| `.deadline` | DL date labels | `#9ca3af` + `font-weight: 500` + `nowrap` |
| `.status-live` | Live badge | `#22c55e` on `#052e16` |
| `.status-building` | Building badge | `#fbbf24` on `#1c1400` |
| `.status-research` | Research/WIP badge | `#a855f7` on `#1a0d2e` |
| `.phase-date` | Roadmap dates | `#6b7280` (intentionally muted) |
