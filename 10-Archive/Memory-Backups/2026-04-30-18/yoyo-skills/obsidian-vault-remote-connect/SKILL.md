---
name: obsidian-vault-remote-connect
description: Connect an Obsidian vault to Hermes running on a remote Linux server when the vault is on a different machine (Windows/Mac). Covers sync strategies and path configuration.
---

# Obsidian Vault — Remote Connection

When the user's Obsidian vault is on a different machine than the Hermes server (common: Windows desktop + Linux server), the vault files are not directly accessible.

## Step 1: Determine the situation

- Check `uname -a` and `ls /mnt/c/Users/` to detect WSL
- If WSL: vault path maps to `/mnt/c/Users/<user>/...` — done
- If bare Linux server: need sync solution

## Step 2: Sync options (offer to user)

| Method | Pros | Cons |
|--------|------|------|
| **Syncthing** (recommended) | Free, live P2P sync | Requires install on both machines |
| **Git** (private repo) | Version controlled | Manual push/pull |
| **Obsidian Headless** | Official Sync API, runs on headless servers, E2E encrypted | npm package, needs encryption password |
| **Obsidian Sync (GUI)** | Official, E2E encrypted | Requires Obsidian desktop app — NOT for headless servers |
| **scp/rsync** | Simple one-time copy | Not live-synced |

### Syncthing setup
1. Install on both machines (see syncthing.net)
2. Add vault folder, share between devices
3. Vault appears at synced path on server

### Obsidian Headless setup (recommended for headless servers)
Uses Obsidian's official Sync API without the GUI app.

1. Install: `npm install -g obsidian-headless` (provides `ob` CLI, invoked via `npx obsidian-headless`)
2. Login: `npx obsidian-headless login` (interactive — enters email + password)
3. List remote vaults: `npx obsidian-headless sync-list-remote`
4. Set up local sync: `npx obsidian-headless sync-setup --remote <vault-id> --path /root/vaults/<name>`
5. Sync: `npx obsidian-headless sync --path /root/vaults/<name>`
6. Continuous mode: `npx obsidian-headless sync --path /root/vaults/<name> --continuous`

**Verification workflow:**
```
npx obsidian-headless login                          # check logged in
npx obsidian-headless sync-list-remote               # see available vaults
npx obsidian-headless sync-list-local                # see configured local vaults
npx obsidian-headless sync-status --path <vault-path>  # check sync state
```

**Notes:**
- Encryption password is stored after first successful sync — subsequent syncs don't prompt
- Device name is set during `sync-setup` (e.g., `gentech-server`)
- Sync mode defaults to bidirectional with merge conflict strategy
- File types synced: image, audio, pdf, video (config syncing is separate)

### Git setup
Initialize git in vault, create private repo, push, then clone on server.

## Step 3: Configure Hermes

1. Install kepano obsidian-skills into hermes note-taking skills directory
2. Set OBSIDIAN_VAULT_PATH environment variable
3. Verify with find to list markdown files

## Pitfalls

- OneDrive paths require sync client running. Syncthing more reliable for server access.
- Obsidian Headless replaces the old limitation of needing the GUI app for headless Sync access.
- Using both Obsidian Headless Sync and Syncthing/git on the same vault can cause conflicts. Pick one sync method.
- Always quote vault paths with spaces.
- Large vaults with attachments need git-lfs or .gitignore.
