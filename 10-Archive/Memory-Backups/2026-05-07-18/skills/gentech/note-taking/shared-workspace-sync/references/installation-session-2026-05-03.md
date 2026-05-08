# obsidian-headless Installation Session — 2026-05-03

## Environment
- OS: Ubuntu (WSL2 or native Linux)
- Initial Node: none (apt broken: dpkg errors)
- Final Node: v22.11.0 (official binary tarball)
- npm: 10.2.4 (from Node 22 bundle)
- obsidian-headless: 0.0.8
- Binary: `ob` (not `obsidian-headless-sync`)
- Global npm root: `/usr/local/node/lib/node_modules`
- Binary location: `/usr/local/node/bin/ob` → symlinked to `/usr/local/bin/ob`

## Problem: apt broken + missing npm
```
E: dpkg was interrupted, you must manually run 'dpkg --configure -a'
```

**Fix:** Manual Node binary install from nodejs.org (see `scripts/install-node.sh`).

## Problem: obsidian-headless npm package not found
First tried: `npm install -g obsidian-headless-sync` → 404 Not Found

**Correct:** `npm install -g obsidian-headless`

## Problem: Binary not found after install
`ob: command not found` even though npm reported success.

**Cause:** `/usr/local/node/bin` not in PATH; no symlink to `/usr/local/bin`.

**Fix:** `ln -sf /usr/local/node/bin/ob /usr/local/bin/ob`

## Problem: Node v18 gives EBADENGINE + WebCrypto missing
obsidian-headless requires Node >= 20; Node 18 lacks stable WebCrypto.

Symptoms:
- `npm WARN EBADENGINE required: { node: '>=20' }`
- Runtime: `ReferenceError: crypto is not defined`

**Fix:** Upgrade to Node 22 LTS.

## Verification Steps
```bash
# 1. Node version
node --version  # v22.x.x

# 2. WebCrypto available?
node -e "console.log('webcrypto' in globalThis ? 'YES' : 'NO')"
# Must print: YES

# 3. Binary works
ob --version  # 0.0.8
ob --help     # shows sync, login, publish commands
```

## Obsidian Account Status
- No local config found pre-install (`~/.config/obsidian` absent)
- Need credentials to proceed with `ob login`
- Remote vault creation pending login

## Next Steps (Blocked)
1. Run `ob login` with Obsidian account (email/password or device flow)
2. `ob sync-create-remote --name "GenTech-Brain"` (if vault doesn't exist)
3. `ob sync-setup --vault "GenTech-Brain" --path /root/vaults/gentech`
4. Start daemon: `scripts/vault-sync-daemon.sh` or cron-based sync

## Related Commands
```bash
# Check login status
ob login

# List vaults
ob sync-list-remote
ob sync-list-local

# Setup (first time)
ob sync-setup --vault "NAME" --path /path/to/vault

# Manual sync
ob sync

# Status
ob sync-status

# Unlink
ob sync-unlink
```