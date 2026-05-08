---
name: hermes-operations
description: Hermes Agent operational workflows — backup, cron management, vision debugging, vault connectivity, and cross-profile maintenance.
version: 1.0.0
author: Hermes Agent Curator
license: MIT
metadata:
  hermes:
    tags: [hermes, operations, devops, cron, backup, vault, vision]
    related_skills: [vault-atomic-operations]
---

# Hermes Operations

Class-level skill covering all Hermes Agent operational workflows. Use this for:
- Backing up the agent brain
- Auditing and consolidating cron jobs
- Debugging vision model failures
- Connecting Obsidian vaults to remote agents
- Cross-profile maintenance and drift detection

---

## 1. Hermes Brain Backup

Back up the entire agent "brain" (vault, profiles, memory, skills, cron configs) to a private GitHub repo.

### Key Paths
- **Gentech (main agent):** `~/.hermes/SOUL.md` and `~/.hermes/config.yaml`
- **Sub-agents (YoYo, DMOB, Desmond):** `~/.hermes/profiles/{agent}/SOUL.md` and `~/.hermes/profiles/{agent}/config.yaml`
- **Vault:** `/root/vaults/gentech/`
- **Skills:** `~/.hermes/skills/`
- **Cron Registry:** Vault cron manifest (`03-Strategies/cron-jobs.md`)
- **Backup Exclusions:** Dual-layer strategy—rsync-level AND gitignore-level are both required.

### Vault Exclusion Taxonomy
The vault contains directories that must be excluded from backup to prevent repo bloat:

**Archive directories (large historical data):**
- `10-Archive/` — vault sweeps, handoffs, sessions (hundreds of MB to GB)
- `Memory-Backups/` — brain snapshots (massive binary blobs)
- `08-Daily-Old/`, `08-Logs-Old/` — deprecated daily logs

**Security / special-purpose data:**
- `red-teaming/` — pentest findings (large, sensitive)
- `00-System/secrets.env` — already gitignored but double-check

**Embedded git repositories (submodules or standalone):**
- `02-Labs/tech-payment-router/` — standalone git repo
- `03-Projects/hermes-kanban/` — embedded git repo
- `03-Projects/tech-burn-test/` — embedded git repo
- `03-Projects/BirdeyeBIP/` — embedded git repo
- Any `**/.git/` directory (covered by `**/.git/` gitignore rule)

**Build / dependency artifacts:**
- `**/target/` (Rust)
- `**/.anchor/` (Solana)
- `**/node_modules/`
- `**/venv/`, `**/.venv/`
- `**/site-packages/`
- `**/__pycache__/`, `**/*.pyc`
- `**/out/`, `**/artifacts/`, `**/broadcast/` (Foundry)
- `**/*.egg-info/`

**Media and large assets:**
- `**/*.mp3`, `**/*.wav`, `**/*.ogg`, `**/*.mp4`, `**/*.mov`, `**/*.avi`
- `**/*.pdf`
- `assets/voices/`, `assets/videos/`, `assets/branding/*.png`, etc.
- `**/images/` (if large)

**Obsidian / IDE noise:**
- `.obsidian/workspace`, `.obsidian/workspace.json`, `.obsidian/graph.json`

**Agent runtime caches:**
- `~/.hermes/image_cache/` (vision images)
- `~/.hermes/audio_cache/`

**General large binary patterns:**
- `**/*.bin`, `**/*.so`, `**/*.dll`, `**/*.dylib`

### Setup Steps
1. **Create private repo** via `gh repo create <org>/hermes-brain-backup --private`
2. **Initialize git** with token-authenticated remote URL
3. **Create `.gitignore`** in backup repo root with comprehensive exclusions (see vault exclusions above + secrets)
4. **Write `backup.sh`** — rsync vault with `--exclude` filters, copy agent SOUL/config/memory, sync skills, git commit+push
5. **Write `restore.sh`** — reverse: pull repo, rsync back to vault, copy agent files back
6. **Schedule cron** — every 6 hours run `backup.sh`
7. **Run initial backup** to populate the repo

### Recovery from Bloated Commits (Accidental Large Files)
If a commit accidentally includes large directories (e.g., `10-Archive/`, `site-packages/`, `.venv`), use this recovery pattern:

**1. Identify the bad commit:**
```bash
git log --oneline -3
git show HEAD --stat  # see what files were added
```

**2. Soft-reset to unstage everything:**
```bash
git reset HEAD~    # or HEAD if last commit is bad
git status         # now changes are unstaged
```

**3. Remove unwanted files from working tree:**
```bash
# Remove entire unwanted directory trees
rm -rf vault/10-Archive/
rm -rf vault/Memory-Backups/
find vault -name ".venv" -type d -exec rm -rf {} +

# Or use git clean for tracked-but-unwanted files
git clean -fd vault/10-Archive/
```

**4. Verify cleanliness before restaging:**
```bash
# Quick check for large directories still present
find vault -name "10-Archive" -o -name "Memory-Backups" -o -name ".venv"
find vault -path "*/site-packages/*" -o -path "*/.local/*"
```

**5. Re-stage clean state and commit:**
```bash
git add vault
git add agents/ skills/
git commit -m "🧠 Daily backup — $(date +%Y-%m-%d)"
```

**6. (Optional) Remove the bad commit from history:**
If the bad commit was already pushed or you want to clean local history:
```bash
# Interactive rebase to drop the bad commit
git rebase -i HEAD~3   # mark the bad commit with 'drop'
# OR, if it's the most recent and you want to discard completely:
git reset --hard HEAD~1   # ⚠️ DANGER: discards working changes
```

**7. If you've already pushed the bad commit:** You must force-push the cleaned history (coordinate with team):
```bash
git push --force-with-lease
```

---

### Pre-Commit Vault Health Verification
Before creating the backup commit, run these checks to ensure backup quality:

```bash
# 1. Check for excluded directories still present
for dir in 10-Archive Memory-Backups red-teaming; do
  if [ -d "vault/$dir" ]; then
    echo "⚠️  FOUND $dir in vault — should be excluded!"
    exit 1
  fi
done

# 2. Check for Python virtualenvs and site-packages
if find vault -name ".venv" -o -path "*/site-packages/*" | grep -q .; then
  echo "⚠️  Python env found in vault"
  exit 1
fi

# 3. Check for embedded git repos
if find vault -path "*/.git" -type d | grep -q .; then
  echo "⚠️  Embedded git repos found (use git submodule or exclude)"
  exit 1
fi

# 4. Size sanity check (active vault < 200MB typical)
VAULT_SIZE=$(du -sm vault | cut -f1)
if [ "$VAULT_SIZE" -gt 200 ]; then
  echo "⚠️  Vault size ${VAULT_SIZE}MB exceeds 200MB threshold"
  echo "Large directories:"
  du -sh vault/* | sort -rh | head -10
  exit 1
fi

echo "✅ Vault health check passed"
```

**Expected healthy vault characteristics:**
- Total size: **< 150 MB** for active notes only (excluding archives)
- No `10-Archive/`, `Memory-Backups/`, `red-teaming/`
- No `**/.git/` subdirectories (only the main repo's `.git/`)
- No `**/.venv/`, `**/site-packages/`, `**/node_modules/`
- Top-level dirs: `00-HQ/` through `12-Skills/`, `Crypto/`, `Market Data/`, etc.

---

### Pitfalls
- **Agent profile paths:** Sub-agents live in `~/.hermes/profiles/{name}/`, NOT `~/.hermes/{name}/`
- **Git auth — SSH deploy key:** The brain backup repo uses an SSH deploy key (`/root/.ssh/hermes-brain-backup`). If this key is revoked/removed from GitHub, push silently fails. The script `backup-brain.py` exits 0 even on push failure — it logs "⚠️ Push failed" but still reports "✅ Backup complete". Always check the backup.log for push status after cron runs.
- **Git auth fallback flow:** When SSH deploy key fails, try these in order: (1) `ssh-add` the key then retry, (2) check verbose SSH with `ssh -vT -i /root/.ssh/hermes-brain-backup git@github.com`, (3) try HTTPS with token, (4) report to Gentech for key re-add. See `references/ssh-deploy-key-failure.md` for the full diagnostic sequence.
- **`memory.md`:** Not all agents have one — handle missing files gracefully
- **`config.yaml` may contain bot tokens:** Strip secrets before committing or add to `.gitignore`
- **Build artifact bloat:** Ensure `.gitignore` excludes `target/`, `.anchor/`, and other temporary build directories to prevent disk spikes.
- **AAE config dual location:** `.lfj-aae-config.json` lives both in the vault (`03-Strategies/scripts/`) and Hermes runtime (`~/.hermes/profiles/<profile>/home/.hermes/scripts/`). Updating only the vault file does **not** affect running cron jobs — they use the runtime copy. After any config change, manually copy to each profile's runtime dir or run the verification script in `defi-milestone-cron-operations` skill to check and fix drift.
- **Vault sync command `ob sync`:** This command is not available in the Hermes runtime environment. Vault updates require explicit copy operations to Hermes profile script directories if those profiles need the changes. The `ob sync` Obsidian sync is unrelated to Hermes cron config propagation.
- **Concurrent writes:** When multiple agents need to write to the same vault file simultaneously, use `vault-atomic-operations` for file-locking and append-safe patterns. Without it, race conditions can corrupt context.

### References
- [Session-specific backup script template](references/backup-script-template.md)
- [Backup bloat prevention guide](references/backup-bloat-prevention.md)
- **See also:** `vault-atomic-operations` — file-locking pattern for concurrent-safe vault writes when multiple agents share the brain

---

## 2. Hermes Cron Audit

Audit, diagnose, and fix broken Hermes cron jobs across all agent profiles. Covers stale jobs, auth failures, duplicate removal, and cross-profile cleanup.

### Quick Health Check (One-Liner)
```bash
for profile in dmob yoyo desmond gentech; do
  echo "=== $profile ==="
  cat /root/.hermes/profiles/$profile/cron/jobs.json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for j in data.get('jobs', []):
    status = j.get('last_status', 'never') or 'never'
    enabled = '✓' if j.get('enabled', True) else '✗'
    schedule = j.get('schedule', {})
    sched = schedule.get('expr', schedule.get('kind', '?')) if isinstance(schedule, dict) else str(schedule)
    name = j.get('name', 'unnamed')[:45]
    script = j.get('script')
    script_note = ''
    if script:
        import os
        exists = os.path.exists(f'/root/.hermes/scripts/{script}')
        script_note = f' [script: {\"✓\" if exists else \"✗ MISSING\"}]'
    print(f'  {enabled} {status:6} {sched:25} {name}{script_note}')
" 2>/dev/null
done
```

### Common Failure Patterns
| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `last_run_at` stale | Gateway restart missed windows | `hermes --profile X cron run <job_id>` |
| `last_run_at: null` | Job created but scheduler didn't pick it up | Trigger manually, check schedule syntax |
| `error` in `last_status` | Script bug, API failure, parse error | Check error message, fix script or prompt |
| `last_delivery_error` | Telegram group ID wrong, bot kicked | Verify delivery target |
| Duplicate jobs | Consolidation didn't clean up all copies | Remove duplicates, keep canonical |

### Cron Routing Audit

When Jordan says "make sure cron jobs follow smart routing" or similar, validate every job's `deliver` target against the routing guide's channel IDs.

#### Channel ID Reference (Gentech fleet)
| Channel | ID |
|---------|-----|
| Gentech HQ | `-1003863540828` |
| Gentech Labs | `-1003872552815` |
| Gentech Strategies | `-1002916759037` |
| Gentech Entertainment | `-1003893562036` |

#### Routing Rules (from Smart Routing Guide)
| Work Type | Correct Channel |
|-----------|----------------|
| System admin (cron, config, backup) | HQ |
| Development (code, contracts, hackathons) | Labs |
| Research/analysis (DeFi, market, strategy) | Strategies |
| Content (posts, social, branding) | Entertainment |

#### Audit Steps
1. List all jobs: `cronjob(action="list")` for current profile, plus check `/root/.hermes/profiles/*/cron/jobs.json` for other profiles
2. Map each job's `deliver` field to a channel:
   - Explicit `telegram:-100XXXX` → resolve to channel name
   - `origin` → resolve to the channel where the job was created (check creation context)
   - `local` → no Telegram delivery (OK for internal-only jobs)
3. Compare job purpose against routing rules — flag mismatches
4. Present audit table to Jordan for approval before changing
5. Fix with `cronjob(action="update", job_id=X, deliver="telegram:<correct_id>")`

#### Common Mismatches
- **`origin` on system admin jobs** created from HQ → correct (HQ = system admin home)
- **`origin` on research jobs** created from HQ → should deliver to Strategies
- **`origin` on DeFi monitoring jobs** created from HQ → should deliver to Strategies
- **Backup/system jobs** delivering to Labs → should be HQ
- **Truncated IDs** (e.g., `-100386354028` missing digits) → broken delivery target, fix immediately

### Pitfalls
- `origin` resolves at creation time — if you create a job from HQ but its content belongs in Labs, it'll deliver to HQ. Set the explicit deliver target instead.
- Cross-profile jobs (gentech creating jobs for dmob's domain) need explicit routing, not `origin`
- Some jobs may be intentionally cross-channel (e.g., security content pipeline → Entertainment). Don't auto-fix without Jordan's approval.

### References
- [Cron job health checklist](references/cron-health-checklist.md)
- [Script not found debug guide](references/script-not-found-debug.md)
- Smart Routing Guide: `02-Labs/Smart-Routing-Guide.md` (vault)

---

## 3. Hermes Cron Consolidation

Merge two or more Hermes Agent cron jobs into one, porting script logic and keeping all documentation in sync.

### Steps
1. **Survey current state** — `cronjob(action="list")` + vault doc search
2. **Read both scripts** — identify shared vs unique logic
3. **Patch target script** — port missing logic from retired script
4. **Create consolidated cron job** — unified schedule, prompt, script
5. **Remove old jobs** — `cronjob(action="remove", job_id="<old-job-id>")`
6. **Update all documentation** — rules doc, manifest, JSON, vault references
7. **Verify final state** — `cronjob(action="list")`

### Pitfalls
- **Doc drift** — Three files (rules doc, manifest, JSON) can disagree. Update ALL of them.
- **Script paths** — Vault path vs `~/.hermes/scripts/` path. Copy the script to the scripts dir.
- **Confirmation delays** — Port 2-check or N-check patterns explicitly.

### References
- [Cron consolidation template](templates/cron-consolidation-template.md)

---

## 3b. Fleet-Wide Config Migration

When changing a config value across all agents (model, provider, vision, etc.), configs exist at **four layers** — fix ALL of them or the next deploy/restore reintroduces drift.

### Config Hierarchy (Source → Inheritance)

| Layer | Path | Role |
|-------|------|------|
| **Brain repo template** | `/root/repos/hermes-brain/config.yaml` | Source of truth for new deploys and restores |
| **Live global** | `~/.hermes/config.yaml` | Default for all profiles (profile overrides this) |
| **Live profile** | `~/.hermes/profiles/{agent}/config.yaml` | Per-agent override (what actually runs) |
| **Vault backup** | `vault/00-System/agent-profiles/{agent}/config.yaml` | Archived copy for disaster recovery |

**Pitfall:** Updating only the live profile config works TODAY but the next brain restore or vault snapshot overwrites it. Always update the brain repo template too.

### Migration Steps
1. **Audit current state** — grep the target config key across all four layers:
   ```bash
   grep -rn "target_key" /root/repos/hermes-brain/config.yaml \
     /root/.hermes/config.yaml \
     /root/.hermes/profiles/*/config.yaml \
     /root/vaults/gentech/00-System/agent-profiles/*/config.yaml
   ```
2. **Fix brain repo template** first (source of truth)
3. **Fix live global config** (fallback for all profiles)
4. **Fix each live profile** (what's actually running)
5. **Fix vault backups** (prevent restore drift)
6. **Verify consistency** — re-run the audit grep, confirm all values match
7. **Restart gateways** if the change affects running agents: `hermes gateway restart`

### Provider Migration Checklist
When switching providers (e.g., ollama-cloud → openrouter):
- [ ] `model.provider` updated
- [ ] `auxiliary.vision.provider` updated
- [ ] `auxiliary.vision.model` set explicitly (don't rely on auto-detection)
- [ ] Stale `base_url` removed (blank it out for built-in providers)
- [ ] Stale `api_key` removed (built-in providers use credential pools)
- [ ] `custom_providers` section added if using `provider: custom`
- [ ] All four layers updated (brain repo, global, profiles, vault)

Debug Hermes vision/photo analysis failures — trace the auxiliary client resolution chain, diagnose model normalization issues, and fix vision model routing for Nous Portal and other providers.

### Symptoms
- Telegram photos are received and cached (`~/.hermes/image_cache/`) but vision analysis fails
- `tools.vision_tools: Error analyzing image: Error code: 404` in `~/.hermes/logs/agent.log`
- `vision_analyze` tool returns errors or empty results

### Working Vision Config (as of May 2026)
The stable, fleet-wide vision configuration is:
```yaml
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-2.0-flash-001
    base_url: ''
    api_key: ''
```
**Why this works:** `google/gemini-2.0-flash-001` is a stable, vision-capable model on OpenRouter. The deprecated `google/gemini-2.0-flash-exp:free` (free tier) stopped serving vision requests. `gemini-3-flash-preview` works on Nous Portal but NOT reliably on OpenRouter.

**Do NOT use:** `google/gemini-2.0-flash-exp:free` (deprecated), bare `gemini-3-flash` (normalizes to `google/gemini-3-flash` → 404 on some providers).

### Debugging Steps
1. **Check logs** — `grep -i "vision\|photo\|image\|404" ~/.hermes/logs/agent.log`
2. **Quick fleet audit** — verify all configs agree:
   ```bash
   for f in /root/.hermes/config.yaml /root/.hermes/profiles/*/config.yaml /root/repos/hermes-brain/config.yaml; do
     echo "=== $(basename $(dirname $f)) ==="
     grep -A 3 "vision:" "$f" | head -4
   done
   ```
3. **Trace vision model resolution** —
   ```python
   from agent.auxiliary_client import resolve_vision_provider_client, _PROVIDER_VISION_MODELS
   print('Vision model map:', _PROVIDER_VISION_MODELS)
   provider, client, model = resolve_vision_provider_client()
   print(f'Resolved: provider={provider}, model={model}, client={client is not None}')
   ```
4. **Test resolved model directly** —
   ```python
   from openai import OpenAI
   from agent.auxiliary_client import _read_nous_auth, _nous_api_key, _nous_base_url
   nous = _read_nous_auth()
   client = OpenAI(api_key=_nous_api_key(nous), base_url=_nous_base_url())
   tiny_png = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
   resp = client.chat.completions.create(
       model=model,
       messages=[{'role': 'user', 'content': [
           {'type': 'text', 'text': 'What color?'},
           {'type': 'image_url', 'image_url': {'url': f'data:image/png;base64,{tiny_png}'}}
       ]}],
       max_tokens=20
   )
   print(resp.choices[0].message.content)
   ```

### Error Pattern: `400 - Not supported model`
When vision returns `Error code: 400 - {'error': {'code': '400', 'message': 'Not supported model <model_name>'}}`, this is distinct from the 404 normalization issue. It means the provider endpoint actively rejected the model name.

**Most common cause:** The configured provider has no API key in `.env`, so the request falls through to a default/custom endpoint that doesn't support the model.

**Diagnosis flow:**
1. `hermes config` → check `auxiliary.vision` provider and model
2. `grep <PROVIDER_KEY> ~/.hermes/profiles/<profile>/.env` → confirm API key exists
3. If key is missing: either add the key OR switch to a provider that's already configured
4. Quick test: `browser_vision` tool will return this exact error pattern if the provider can't serve the model

**Fix:** Either set the API key for the configured provider, or reconfigure auxiliary.vision to use a provider that already has credentials:
```bash
hermes config set auxiliary.vision.provider <provider_with_key>
hermes config set auxiliary.vision.model <model_name>
```

### Known Bugs & Fixes
- **Duplicate `_PROVIDER_VISION_MODELS` dict** — Remove broken duplicate in `auxiliary_client.py`.
- **Nous vision model normalization** — Use `google/gemini-3-flash-preview` (not `gemini-3-flash`).
- **Stale base_url from provider migrations** — When switching providers (e.g., ollama-cloud → openrouter), leftover `base_url` values (e.g., `https://ollama.com/v1`) force custom endpoint routing that bypasses the provider's credential pool. Always blank out `base_url` and `api_key` when switching to a built-in provider like openrouter.

### References
- [Vision model normalization debug script](scripts/vision-model-debug.py)
- [Nous Portal vision model compatibility table](references/nous-vision-models.md)

---

## 5. ElevenLabs TTS Credential Rotation

When fleet-wide TTS failure occurs (all agents using ElevenLabs return 401), follow this standardized recovery procedure.

### Quick Detection
```bash
# Run pre-flight TTS test (fails fast if key invalid/expired)
curl -s -o /dev/null -w "%{http_code}" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/voices
# Returns 200 if key is valid AND has credits
# Returns 401 with body {"detail":{"status":"quota_exceeded"}} → key valid but 0 credits
# Returns 401 with body {"detail":{"status":"invalid_api_key"}} → key revoked/expired
```

### Known Error Signatures (ElevenLabs)
| Endpoint | 401 + `invalid_api_key` | 401 + `quota_exceeded` |
|----------|------------------------|------------------------|
| `/v1/user` | Key revoked/expired | **Key valid, 0 credits** (missing `user_read` scope is OK) |
| `/v1/voices` | Key revoked/expired | **Key valid, 0 credits** |
| `/v1/text-to-speech/:id` | Key revoked/expired | **Key valid, 0 credits** |

**Key insight:** ElevenLabs sometimes returns `401` with `"missing_permissions"` on the `/user` endpoint even for valid keys (scopes issue). Always test with `/v1/voices` for validity + quota in one call.

### Stale Keys Across Gentech Fleet (as of May 3, 2026)
| Location | Key Prefix | Status | Notes |
|----------|-----------|--------|-------|
| `~/.hermes/.env` (deployed) | `bb158b...` | ❌ Expired (May 2 outage) | Was shared fleet key — now revoked |
| `vault .env` (root) | `ff52c5...` | ❌ Invalid | Stale — needs rotation |
| `00-System/secrets/.env` | `sk_c87...` | ⚠️ Valid but 0 credits | Fresh key (subaccount), not recharged yet |
| `elevenlabs-config.md` | `***` (redacted) | 🔒 Vault-encrypted | Actual live key stored separately |

### Active Credential Discovery Pattern
```bash
# 1. Check vault root .env (stale/invalid)
grep ELEVENLABS_API_KEY /root/vaults/gentech/.env

# 2. Check system secrets (fresh key, may be 0-credit)
cat /root/vaults/gentech/00-System/secrets/.env

# 3. Check per-agent .env files (symlinked or duplicated)
for agent in dmob yoyo desmond gentech; do
  grep ELEVENLABS /root/.hermes/profiles/$agent/.env 2>/dev/null
done

# 4. Check herm
| Method | Pros | Cons |
|--------|------|------|
| **Syncthing** (recommended) | Free, live P2P sync | Requires install on both machines |
| **Git** (private repo) | Version controlled | Manual push/pull |
| **Obsidian Headless** | Official Sync API, runs on headless servers, E2E encrypted | npm package, needs encryption password |
| **Obsidian Sync (GUI)** | Official, E2E encrypted | Requires Obsidian desktop app — NOT for headless servers |
| **scp/rsync** | Simple one-time copy | Not live-synced |

### Obsidian Headless Setup (Recommended for Headless Servers)
1. Install: `npm install -g obsidian-headless`
2. Login: `npx obsidian-headless login` (interactive — enters email + password)
3. List remote vaults: `npx obsidian-headless sync-list-remote`
4. Set up local sync: `npx obsidian-headless sync-setup --remote <vault-id> --path /root/vaults/<name>`
5. Sync: `npx obsidian-headless sync --path /root/vaults/<name>`
6. Continuous mode: `npx obsidian-headless sync --path /root/vaults/<name> --continuous`

### Verification Workflow
```bash
npx obsidian-headless login                          # check logged in
npx obsidian-headless sync-list-remote               # see available vaults
npx obsidian-headless sync-list-local                # see configured local vaults
npx obsidian-headless sync-status --path <vault-path>  # check sync state
```

### Pitfalls
- **OneDrive paths** require sync client running. Syncthing more reliable for server access.
- **Obsidian Headless replaces the old limitation** of needing the GUI app for headless Sync access.
- **Using both Obsidian Headless Sync and Syncthing/git on the same vault can cause conflicts.** Pick one sync method.

### References
- [Obsidian Headless setup guide](references/obsidian-headless-setup.md)
- [Syncthing setup guide](references/syncthing-setup.md)
