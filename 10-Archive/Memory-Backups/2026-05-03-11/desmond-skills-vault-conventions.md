# Vault Conventions — Gentech

**Scope:** `/root/vaults/gentech/`

## Folder Purpose Reference

| Folder | Purpose | Size Expectation | Cleanup Rules |
|--------|---------|------------------|---------------|
| `00-HQ/` | HQ comms, approvals, travel, brainstorm | Small (<10MB) | Never delete without Jordan approval |
| `01-Agency/` | Agency docs, org charts | Small | Keep |
| `02-Labs/` | Engineering, contracts, hackathon repos | Medium | Keep; archive old hackathons to 10-Archive |
| `03-Projects/` | Active project codebases | Variable | Keep; snapshot inactive to 10-Archive |
| `03-Strategies/` | Market data, cron manifests | Small-medium | Keep; prune old data files weekly |
| `04-Entertainment/` | Social content drafts, media plans | Small | Keep; archive published to 06-Content |
| `05-Learning/` | Tutorials, research notes | Small | Keep |
| `06-Content/` | Published content (blogs, docs, READMEs) | Small | Keep |
| `07-Ideas/` | Brainstorm fragments | Small | Keep; archive realized to 10-Archive |
| `08-Daily/` | Daily logs | Small | Rotate monthly → 10-Archive |
| `08-Logs/` | System logs (agent output) | Small | Rotate weekly → 10-Archive |
| `09-Green Room/` | Cross-agent handoffs | Small | Keep active; archive closed to 10-Archive |
| `09-Templates/` | Reusable templates | Small | Keep |
| `10-Archive/` | Long-term cold storage | Large (intentional) | Compress old (>90d) items via `tar` |
| `11-Mess Hall/` | General comms, status updates | Small | Keep |
| `12-Skills/` | Hermes skill docs | Small | Keep |

## Health Check Thresholds

- **Vault total > 100GB** → investigate `10-Archive` compression
- **Any folder > 10GB** (except 10-Archive) → outlier, audit contents
- **`06-Content/` + `04-Entertainment/` combined > 1GB** → likely media bloat; optimize/compress images
- **`09-Green Room/` > 50MB** → too many active handoffs; close stale ones

## What BELONGS in Vaults (Gentech assets only)
- Hackathon submission docs
- Creative briefs and storyboards
- Strategy decks and market research
- Architecture diagrams (Excalidraw JSON, SVG)
- Internal meeting notes
- Approval forms and compliance docs

## What does NOT belong in vaults
- Node modules (`node_modules/`)
- Build artifacts (`target/`, `dist/`, `build/`)
- Package caches (`.npm`, `.cache/`, `.cargo`)
- Docker images/containers
- VM disk images
- Personal files (photos, music, etc.)

## Archive Policy

1. **Closed hackathons** → tar to `10-Archive/hackathons/<year>/<name>.tar.gz`
2. **Released content** (>30 days) → tar to `10-Archive/content/<year>/<month>/`
3. **Inactive projects** (>60 days, no commits) → tar to `10-Archive/projects/`
4. **Old logs** (>90 days) → tar to `10-Archive/logs/`

**Compression:** `tar -czf <archive>.tar.gz <folder> && rm -rf <folder>`

## Quick Health Command

```bash
# Vault-only size check
du -sh /root/vaults/gentech/* | sort -rh
echo "Total vault usage:"
du -sh /root/vaults/gentech
```

**Normal baseline:** ~50–100MB total (excluding 10-Archive).
