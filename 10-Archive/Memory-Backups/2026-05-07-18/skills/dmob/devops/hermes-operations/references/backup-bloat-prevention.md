# Backup Bloat Prevention

## Problem
Hermes backups (`ob sync`) recursively copy **entire vault directories**, including:
- Solana Anchor `target/` directories (2–5GB each)
- `.anchor/` directories (100MB+)
- Python `__pycache__/` and `.venv/` (500MB+)
- Hermes image cache (`~/.hermes/image_cache/`, 1–10GB)

This causes disk usage spikes (e.g., 40GB → 193GB) and slows down syncs.

---

## Solution
### 1. Global `.gitignore`
Add these exclusions to `/root/vaults/gentech/.gitignore`:
```gitignore
target/
.anchor/
__pycache__/
*.pyc
.venv/
.env
*.key
*.pem
auth.json
*.mp3
*.mp4
*.ogg
*.wav
*.png
*.jpg
*.jpeg
*.gif
*.webp
~/.hermes/image_cache/
~/.hermes/logs/
```

### 2. Hermes Sync Filter
Configure Hermes to skip `target/` and `.anchor/` during sync:
```bash
# ~/.hermes/config.yaml
sync:
  exclude:
    - "**/target/"
    - "**/.anchor/"
    - "**/__pycache__/"
    - "**/.venv/"
    - "~/.hermes/image_cache/"
```

### 3. Pre-Sync Cleanup Hook
Add a pre-sync hook to remove build artifacts:
```bash
#!/bin/bash
# ~/.hermes/scripts/pre-sync-cleanup.sh
find /root/vaults/gentech -name "target" -type d -exec rm -rf {} + 2>/dev/null
find /root/vaults/gentech -name ".anchor" -type d -exec rm -rf {} + 2>/dev/null
find /root/vaults/gentech -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
```

Register the hook in `config.yaml`:
```yaml
sync:
  pre_sync_hook: "/root/.hermes/scripts/pre-sync-cleanup.sh"
```

---

## Verification
```bash
# Check disk usage before/after sync
df -h /root/vaults/gentech

# List large files (>100MB)
find /root/vaults/gentech -type f -size +100M -exec ls -lh {} \;
```

---

## References
- [GitHub Docs: Ignoring Files](https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files)
- [Hermes Config Reference](https://hermes-agent.nousresearch.com/docs/configuration/#sync)