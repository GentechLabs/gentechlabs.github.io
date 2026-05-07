# Portfolio Site — Session Notes (May 4, 2026)

## Repo & Paths
- **GitHub Pages repo:** `ProtoJay4789/ProtoJay4789.github.io`
- **Vault source:** `/root/vaults/gentech/06-Content/portfolio-current.html`
- **Local clone target (if added):** `/root/ProtoJay4789.github.io/`

## Authentication Discovery
1. `gh auth status` confirms login as `ProtoJay4789` via HTTPS with a PAT (full repo scopes)
2. SSH key exists at `/root/.ssh/hermes-brain-backup` but **agent has no identities loaded** (`ssh-add -l` returns empty)
3. `ssh -T git@github.com` fails with "Permission denied (publickey)"
4. **Conclusion:** Use `gh` CLI for git operations; SSH requires manual agent add

## Clone Command (first-time setup)
```bash
cd /root
gh repo clone ProtoJay4789/ProtoJay4789.github.io
```

## Deploy Command (after editing)
```bash
# 1. Vault file already edited → commit in vault repo
cd /root/vaults/gentech
git add 06-Content/portfolio-current.html
git commit -m "deploy: update portfolio colors + avatar placeholder"

# 2. Copy to Pages repo
cp 06-Content/portfolio-current.html /root/ProtoJay4789.github.io/index.html
# (plus copy assets/ if adding avatar image)

# 3. Push
cd /root/ProtoJay4789.github.io
git add .
git commit -m "update: deploy May 4 portfolio refresh"
git push
```

## Avatar Integration
- Expected file: `assets/jordan-avatar.png` inside the Pages repo
- CSS expects 120×120px (circular border + glow applied)
- Fallback: emoji avatar (`👤`) renders if image path 404s (handled by `onerror` inline handler)

## Color Palette Reference
| Role | Hex | Source |
|---|---|---|
| Background | `#0a0a0a` | Vault update 2026-05-03 |
| Surface | `#111` / `#1a1a1a` | — |
| Text primary | `#9ca3af` (silver) | — |
| Accent primary | `#3b82f6` (blue) | — |
| Accent highlight | `#ef4444` (red) | — |
| Status colors | `#3b82f6` / `#f87171` / `#a855f7` | badges |

**Avoid:** Legacy green `#22c55e` — deprecated in portfolio CSS

## Open Questions / Follow-ups
- [ ] Add weekly cron to automate vault → Pages sync (noted in skill TODO)
- [ ] Confirm avatar image source file and add to `assets/`
- [ ] Consider migrating from gh CLI to SSH-only for headless automation (requires agent key loading strategy)

## Related Vault Files
- `/root/vaults/gentech/06-Content/portfolio-update-2026-05-03.md` — change log
- `/root/vaults/gentech/03-Projects/portfolio-site/` — generator project (different output; not used for live Pages deploy)
