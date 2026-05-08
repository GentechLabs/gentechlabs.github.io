---
name: hermes-agent
description: "Configure, extend, or contribute to Hermes Agent."
version: 2.0.1
author: Hermes Agent + Teknium
license: MIT
metadata:
  hermes:
    tags: [hermes, setup, configuration, multi-agent, spawning, cli, gateway, development]
    homepage: https://github.com/NousResearch/hermes-agent
related_skills: ["claude-code", "codex", "opencode", "hermes-maintenance-scripts"]
---

# Hermes Agent

Hermes Agent is an open-source AI agent framework by Nous Research that runs in your terminal, messaging platforms, and IDEs. It belongs to the same category as Claude Code (Anthropic), Codex (OpenAI), and OpenClaw — autonomous coding and task-execution agents that use tool calling to interact with your system. Hermes works with any LLM provider (OpenRouter, Anthropic, OpenAI, DeepSeek, local models, and 15+ others) and runs on Linux, macOS, and WSL.

What makes Hermes different:

- **Self-improving through skills** — Hermes learns from experience by saving reusable procedures as skills. When it solves a complex problem, discovers a workflow, or gets corrected, it can persist that knowledge as a skill document that loads into future sessions. Skills accumulate over time, making the agent better at your specific tasks and environment.
- **Persistent memory across sessions** — remembers who you are, your preferences, environment details, and lessons learned. Pluggable memory backends (built-in, Honcho, Mem0, and more) let you choose how memory works.
- **Multi-platform gateway** — the same agent runs on Telegram, Discord, Slack, WhatsApp, Signal, Matrix, Email, and 10+ other platforms with full tool access, not just chat.
- **Provider-agnostic** — swap models and providers mid-workflow without changing anything else. Credential pools rotate across multiple API keys automatically.
- **Profiles** — run multiple independent Hermes instances with isolated configs, sessions, skills, and memory.
- **Extensible** — plugins, MCP servers, custom tools, webhook triggers, cron scheduling, and the full Python ecosystem.

People use Hermes for software development, research, system administration, data analysis, content creation, home automation, and anything else that benefits from an AI agent with persistent context and full system access.

**This skill helps you work with Hermes Agent effectively** — setting it up, configuring features, spawning additional agent instances, troubleshooting issues, finding the right commands and settings, and understanding how the system works when you need to extend or contribute to it.

**Docs:** https://hermes-agent.nousresearch.com/docs/

## Quick Start

```bash
# Install
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Interactive chat (default)
hermes

# Single query
hermes chat -q "What is the capital of France?"

# Setup wizard
hermes setup

# Change model/provider
hermes model

# Check health
hermes doctor
```

---

## CLI Reference

### Global Flags

```
hermes [flags] [command]

  --version, -V             Show version
  --resume, -r SESSION      Resume session by ID or title
  --continue, -c [NAME]     Resume by name, or most recent session
  --worktree, -w            Isolated git worktree mode (parallel agents)
  --skills, -s SKILL        Preload skills (comma-separate or repeat)
  --profile, -p NAME        Use a named profile
  --yolo                    Skip dangerous command approval
  --pass-session-id         Include session ID in system prompt
```

No subcommand defaults to `chat`.

### Chat

```
hermes chat [flags]
  -q, --query TEXT          Single query, non-interactive
  -m, --model MODEL         Model (e.g. anthropic/claude-sonnet-4)
  -t, --toolsets LIST       Comma-separated toolsets
  --provider PROVIDER       Force provider (openrouter, anthropic, nous, etc.)
  -v, --verbose             Verbose output
  -Q, --quiet               Suppress banner, spinner, tool previews
  --checkpoints             Enable filesystem checkpoints (/rollback)
  --source TAG              Session source tag (default: cli)
```

### Configuration

```
hermes setup [section]      Interactive wizard (model|terminal|gateway|tools|agent)
hermes model                Interactive model/provider picker
hermes config               View current config
hermes config edit          Open config.yaml in $EDITOR
hermes config set KEY VAL   Set a config value
hermes config path          Print config.yaml path
hermes config env-path      Print .env path
hermes config check         Check for missing/outdated config
hermes config migrate       Update config with new options
hermes login [--provider P] OAuth login (nous, openai-codex)
hermes logout               Clear stored auth
hermes doctor [--fix]       Check dependencies and config
hermes status [--all]       Show component status
```

### Tools & Skills

```
hermes tools                Interactive tool enable/disable (curses UI)
hermes tools list           Show all tools and status
hermes tools enable NAME    Enable a toolset
hermes tools disable NAME   Disable a toolset

hermes skills list          List installed skills
hermes skills search QUERY  Search the skills hub
hermes skills install ID    Install a skill (ID can be a hub identifier OR a direct https://…/SKILL.md URL; pass --name to override when frontmatter has no name)
hermes skills inspect ID    Preview without installing
hermes skills config        Enable/disable skills per platform
hermes skills check         Check for updates
hermes skills update        Update outdated skills
hermes skills uninstall N   Remove a hub skill
hermes skills publish PATH  Publish to registry
hermes skills browse        Browse all available skills
hermes skills tap add REPO  Add a GitHub repo as skill source
```

### MCP Servers

```
hermes mcp serve            Run Hermes as an MCP server
hermes mcp add NAME         Add an MCP server (--url or --command)
hermes mcp remove NAME      Remove an MCP server
hermes mcp list             List configured servers
hermes mcp test NAME        Test connection
hermes mcp configure NAME   Toggle tool selection
```

### Gateway (Messaging Platforms)

```
hermes gateway run          Start gateway foreground
hermes gateway install      Install as background service
hermes gateway start/stop   Control the service
hermes gateway restart      Restart the service
hermes gateway status       Check status
hermes gateway setup        Configure platforms
```

Supported platforms: Telegram, Discord, Slack, WhatsApp, Signal, Email, SMS, Matrix, Mattermost, Home Assistant, DingTalk, Feishu, WeCom, BlueBubbles (iMessage), Weixin (WeChat), API Server, Webhooks. Open WebUI connects via the API Server adapter.

Platform docs: https://hermes-agent.nousresearch.com/docs/user-guide/messaging/

### Sessions

```
hermes sessions list        List recent sessions
hermes sessions browse      Interactive picker
hermes sessions export OUT  Export to JSONL
hermes sessions rename ID T Rename a session
hermes sessions delete ID   Delete a session
hermes sessions prune       Clean up old sessions (--older-than N days)
hermes sessions stats       Session store statistics
```

### Cron Jobs

```
hermes cron list            List jobs (--all for disabled)
hermes cron create SCHED    Create: '30m', 'every 2h', '0 9 * * *'
hermes cron edit ID         Edit schedule, prompt, delivery
hermes cron pause/resume ID Control job state
hermes cron run ID          Trigger on next tick
hermes cron remove ID       Delete a job
hermes cron status          Scheduler status
```

### Webhooks

```
hermes webhook subscribe N  Create route at /webhooks/<name>
hermes webhook list         List subscriptions
hermes webhook remove NAME  Remove a subscription
hermes webhook test NAME    Send a test POST
```

### Profiles

```
hermes profile list         List all profiles
hermes profile create NAME  Create (--clone, --clone-all, --clone-from)
hermes profile use NAME     Set sticky default
hermes profile delete NAME  Delete a profile
hermes profile show NAME    Show details
hermes profile alias NAME   Manage wrapper scripts
hermes profile rename A B   Rename a profile
hermes profile export NAME  Export to tar.gz
hermes profile import FILE  Import from archive
```

### Credential Pools

```
hermes auth add             Interactive credential wizard
hermes auth list [PROVIDER] List pooled credentials
hermes auth remove P INDEX  Remove by provider + index
hermes auth reset PROVIDER  Clear exhaustion status
```

### Other

```
hermes insights [--days N]  Usage analytics
hermes update               Update to latest version
hermes pairing list/approve/revoke  DM authorization
hermes plugins list/install/remove  Plugin management
hermes honcho setup/status  Honcho memory integration (requires honcho plugin)
hermes memory setup/status/off  Memory provider config
hermes completion bash|zsh  Shell completions
hermes acp                  ACP server (IDE integration)
hermes claw migrate         Migrate from OpenClaw
hermes uninstall            Uninstall Hermes
```

---

## Slash Commands (In-Session)

Type these during an interactive chat session.

### Session Control
```
/new (/reset)        Fresh session
/clear               Clear screen + new session (CLI)
/retry               Resend last message
/undo                Remove last exchange
/title [name]        Name the session
/compress            Manually compress context
/stop                Kill background processes
/rollback [N]        Restore filesystem checkpoint
/background <prompt> Run prompt in background
/queue <prompt>      Queue for next turn
/resume [name]       Resume a named session
```

### Configuration
```
/config              Show config (CLI)
/model [name]        Show or change model
/personality [name]  Set personality
/reasoning [level]   Set reasoning (none|minimal|low|medium|high|xhigh|show|hide)
/verbose             Cycle: off → new → all → verbose
/voice [on|off|tts]  Voice mode
/yolo                Toggle approval bypass
/skin [name]         Change theme (CLI)
/statusbar           Toggle status bar (CLI)
```

### Tools & Skills
```
/tools               Manage tools (CLI)
/toolsets            List toolsets (CLI)
/skills              Search/install skills (CLI)
/skill <name>        Load a skill into session
/cron                Manage cron jobs (CLI)
/reload-mcp          Reload MCP servers
/plugins             List plugins (CLI)
```

### Gateway
```
/approve             Approve a pending command (gateway)
/deny                Deny a pending command (gateway)
/restart             Restart gateway (gateway)
/sethome             Set current chat as home channel (gateway)
/update              Update Hermes to latest (gateway)
/platforms (/gateway) Show platform connection status (gateway)
```

### Utility
```
/branch (/fork)      Branch the current session
/fast                Toggle priority/fast processing
/browser             Open CDP browser connection
/history             Show conversation history (CLI)
/save                Save conversation to file (CLI)
/paste               Attach clipboard image (CLI)
/image               Attach local image file (CLI)
```

### Info
```
/help                Show commands
/commands [page]     Browse all commands (gateway)
/usage               Token usage
/insights [days]     Usage analytics
/status              Session info (gateway)
/profile             Active profile info
```

### Exit
```
/quit (/exit, /q)    Exit CLI
```

---

## Key Paths & Config

```
~/.hermes/config.yaml       Main configuration
~/.hermes/.env              API keys and secrets
$HERMES_HOME/skills/        Installed skills
~/.hermes/sessions/         Session transcripts
~/.hermes/logs/             Gateway and error logs
~/.hermes/auth.json         OAuth tokens and credential pools
~/.hermes/hermes-agent/     Source code (if git-installed)
```

Profiles use `~/.hermes/profiles/<name>/` with the same layout.

### Config Sections

Edit with `hermes config edit` or `hermes config set section.key value`.

| Section | Key options |
|---------|-------------|
| `model` | `default`, `provider`, `base_url`, `api_key`, `context_length` |
| `agent` | `max_turns` (90), `tool_use_enforcement` |
| `terminal` | `backend` (local/docker/ssh/modal), `cwd`, `timeout` (180) |
| `compression` | `enabled`, `threshold` (0.50), `target_ratio` (0.20) |
| `display` | `skin`, `tool_progress`, `show_reasoning`, `show_cost` |
| `stt` | `enabled`, `provider` (local/groq/openai/mistral) |
| `tts` | `provider` (edge/elevenlabs/openai/minimax/mistral/neutts) |
| `memory` | `memory_enabled`, `user_profile_enabled`, `provider` |
| `security` | `tirith_enabled`, `website_blocklist` |
| `delegation` | `model`, `provider`, `base_url`, `api_key`, `max_iterations` (50), `reasoning_effort` |
| `checkpoints` | `enabled`, `max_snapshots` (50) |

Full config reference: https://hermes-agent.nousresearch.com/docs/user-guide/configuration

### Providers

20+ providers supported. Set via `hermes model` or `hermes setup`.

| Provider | Auth | Key env var |
|----------|------|-------------|
| OpenRouter | API key | `OPENROUTER_API_KEY` |
| Anthropic | API key | `ANTHROPIC_API_KEY` |
| Nous Portal | OAuth | `hermes auth` |
| OpenAI Codex | OAuth | `hermes auth` |
| GitHub Copilot | Token | `COPILOT_GITHUB_TOKEN` |
| Google Gemini | API key | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| DeepSeek | API key | `DEEPSEEK_API_KEY` |
| xAI / Grok | API key | `XAI_API_KEY` |
| Hugging Face | Token | `HF_TOKEN` |
| Z.AI / GLM | API key | `GLM_API_KEY` |
| MiniMax | API key | `MINIMAX_API_KEY` |
| MiniMax CN | API key | `MINIMAX_CN_API_KEY` |
| Kimi / Moonshot | API key | `KIMI_API_KEY` |
| Alibaba / DashScope | API key | `DASHSCOPE_API_KEY` |
| Xiaomi MiMo | API key | `XIAOMI_API_KEY` |
| Kilo Code | API key | `KILOCODE_API_KEY` |
| AI Gateway (Vercel) | API key | `AI_GATEWAY_API_KEY` |
| OpenCode Zen | API key | `OPENCODE_ZEN_API_KEY` |
| OpenCode Go | API key | `OPENCODE_GO_API_KEY` |
| Qwen OAuth | OAuth | `hermes login --provider qwen-oauth` |
| Custom endpoint | Config | `model.base_url` + `model.api_key` in config.yaml |
| GitHub Copilot ACP | External | `COPILOT_CLI_PATH` or Copilot CLI |

Full provider docs: https://hermes-agent.nousresearch.com/docs/integrations/providers

### Toolsets

Enable/disable via `hermes tools` (interactive) or `hermes tools enable/disable NAME`.

| Toolset | What it provides |
|---------|-----------------|
| `web` | Web search and content extraction |
| `browser` | Browser automation (Browserbase, Camofox, or local Chromium) |
| `terminal` | Shell commands and process management |
| `file` | File read/write/search/patch |
| `code_execution` | Sandboxed Python execution |
| `vision` | Image analysis |
| `image_gen` | AI image generation |
| `tts` | Text-to-speech |
| `skills` | Skill browsing and management |
| `memory` | Persistent cross-session memory |
| `session_search` | Search past conversations |
| `delegation` | Subagent task delegation |
| `cronjob` | Scheduled task management |
| `clarify` | Ask user clarifying questions |
| `messaging` | Cross-platform message sending |
| `search` | Web search only (subset of `web`) |
| `todo` | In-session task planning and tracking |
| `rl` | Reinforcement learning tools (off by default) |
| `moa` | Mixture of Agents (off by default) |
| `homeassistant` | Smart home control (off by default) |

Tool changes take effect on `/reset` (new session). They do NOT apply mid-conversation to preserve prompt caching.

---

## Security & Privacy Toggles

Common "why is Hermes doing X to my output / tool calls / commands?" toggles — and the exact commands to change them. Most of these need a fresh session (`/reset` in chat, or start a new `hermes` invocation) because they're read once at startup.

### Secret redaction in tool output

Hermes auto-redacts strings that look like API keys, tokens, and secrets in all tool output (terminal stdout, `read_file`, web content, subagent summaries, etc.) so the model never sees raw credentials. If the user is intentionally working with mock tokens, share-management tokens, or their own secrets and the redaction is getting in the way:

```bash
hermes config set security.redact_secrets false      # disable globally
```

**Restart required.** `security.redact_secrets` is snapshotted at import time — setting it mid-session (e.g. via `export HERMES_REDACT_SECRETS=false` from a tool call) will NOT take effect for the running process. Tell the user to run `hermes config set security.redact_secrets false` in a terminal, then start a new session. This is deliberate — it prevents an LLM from turning off redaction on itself mid-task.

Re-enable with:
```bash
hermes config set security.redact_secrets true
```

### PII redaction in gateway messages

Separate from secret redaction. When enabled, the gateway hashes user IDs and strips phone numbers from the session context before it reaches the model:

```bash
hermes config set privacy.redact_pii true    # enable
hermes config set privacy.redact_pii false   # disable (default)
```

### Command approval prompts

By default (`approvals.mode: manual`), Hermes prompts the user before running shell commands flagged as destructive (`rm -rf`, `git reset --hard`, etc.). The modes are:

- `manual` — always prompt (default)
- `smart` — use an auxiliary LLM to auto-approve low-risk commands, prompt on high-risk
- `off` — skip all approval prompts (equivalent to `--yolo`)

```bash
hermes config set approvals.mode smart       # recommended middle ground
hermes config set approvals.mode off         # bypass everything (not recommended)
```

Per-invocation bypass without changing config:
- `hermes --yolo …`
- `export HERMES_YOLO_MODE=1`

Note: YOLO / `approvals.mode: off` does NOT turn off secret redaction. They are independent.

### Shell hooks allowlist

Some shell-hook integrations require explicit allowlisting before they fire. Managed via `~/.hermes/shell-hooks-allowlist.json` — prompted interactively the first time a hook wants to run.

### Disabling the web/browser/image-gen tools

To keep the model away from network or media tools entirely, open `hermes tools` and toggle per-platform. Takes effect on next session (`/reset`). See the Tools & Skills section above.

---

## Voice & Transcription

### STT (Voice → Text)

Voice messages from messaging platforms are auto-transcribed.

Provider priority (auto-detected):
1. **Local faster-whisper** — free, no API key: `pip install faster-whisper`
2. **Groq Whisper** — free tier: set `GROQ_API_KEY`
3. **OpenAI Whisper** — paid: set `VOICE_TOOLS_OPENAI_KEY`
4. **Mistral Voxtral** — set `MISTRAL_API_KEY`

Config:
```yaml
stt:
  enabled: true
  provider: local        # local, groq, openai, mistral
  local:
    model: base          # tiny, base, small, medium, large-v3
```

### TTS (Text → Voice)

| Provider | Env var | Free? |
|----------|---------|-------|
| Edge TTS | None | Yes (default) |
| ElevenLabs | `ELEVENLABS_API_KEY` | Free tier |
| OpenAI | `VOICE_TOOLS_OPENAI_KEY` | Paid |
| MiniMax | `MINIMAX_API_KEY` | Paid |
| Mistral (Voxtral) | `MISTRAL_API_KEY` | Paid |
| NeuTTS (local) | None (`pip install neutts[all]` + `espeak-ng`) | Free |

Voice commands: `/voice on` (voice-to-voice), `/voice tts` (always voice), `/voice off`.

---

## Spawning Additional Hermes Instances

Run additional Hermes processes as fully independent subprocesses — separate sessions, tools, and environments.

### When to Use This vs delegate_task

| | `delegate_task` | Spawning `hermes` process |
|-|-----------------|--------------------------|
| Isolation | Separate conversation, shared process | Fully independent process |
| Duration | Minutes (bounded by parent loop) | Hours/days |
| Tool access | Subset of parent's tools | Full tool access |
| Interactive | No | Yes (PTY mode) |
| Use case | Quick parallel subtasks | Long autonomous missions |

### One-Shot Mode

```
terminal(command="hermes chat -q 'Research GRPO papers and write summary to ~/research/grpo.md'", timeout=300)

# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

Hermes uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```
# Start
terminal(command="tmux new-session -d -s agent1 -x 120 -y 40 'hermes'", timeout=10)

# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)

# Read output
terminal(command="sleep 20 && tmux capture-pane -t agent1 -p", timeout=5)

# Send follow-up
terminal(command="tmux send-keys -t agent1 'Add rate limiting middleware' Enter", timeout=5)

# Exit
terminal(command="tmux send-keys -t agent1 '/exit' Enter && sleep 2 && tmux kill-session -t agent1", timeout=10)
```

### Multi-Agent Coordination

```
# Agent A: backend
terminal(command="tmux new-session -d -s backend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t backend 'Build REST API for user management' Enter", timeout=15)

# Agent B: frontend
terminal(command="tmux new-session -d -s frontend -x 120 -y 40 'hermes -w'", timeout=10)
terminal(command="sleep 8 && tmux send-keys -t frontend 'Build React dashboard for user management' Enter", timeout=15)

# Check progress, relay context between them
terminal(command="tmux capture-pane -t backend -p | tail -30", timeout=5)
terminal(command="tmux send-keys -t frontend 'Here is the API schema from the backend agent: ...' Enter", timeout=5)
```

### Session Resume

```
# Resume most recent session
terminal(command="tmux new-session -d -s resumed 'hermes --continue'", timeout=10)

# Resume specific session
terminal(command="tmux new-session -d -s resumed 'hermes --resume 20260225_143052_a1b2c3'", timeout=10)
```

### Tips

- **Prefer `delegate_task` for quick subtasks** — less overhead than spawning a full process
- **Use `-w` (worktree mode)** when spawning agents that edit code — prevents git conflicts
- **Set timeouts** for one-shot mode — complex tasks can take 5-10 minutes
- **Use `hermes chat -q` for fire-and-forget** — no PTY needed
- **Use tmux for interactive sessions** — raw PTY mode has `\r` vs `\n` issues with prompt_toolkit
- **For scheduled tasks**, use the `cronjob` tool instead of spawning — handles delivery and retry

---

## Cross-Profile Cron Consolidation

When the same task runs across multiple Hermes profiles (e.g. YoYo, DMOB, Desmond all monitoring the same LP position), jobs drift into duplication. This workflow finds and merges them.

### 1. Audit All Profiles

```python
python3 -c "
import json, os
for profile in ['yoyo', 'dmob', 'desmond', 'gentech']:
    path = f'/root/.hermes/profiles/{profile}/cron/jobs.json'
    with open(path) as f:
        data = json.load(f)
    for j in data.get('jobs', []):
        name = j.get('name', '')
        if 'LP' in name or 'DeFi' in name:  # filter by topic
            print(f'{profile}: {name} | id={j[\"id\"][:12]} | {j.get(\"schedule\",{}).get(\"display\",\"?\")}')
"
```

**Key:** Job IDs live in `jobs[].id` (not `job_id`). The `cronjob` tool's `list` action returns a flat list — use raw JSON parsing for cross-profile views.

### 2. Identify Duplicates

Look for jobs with overlapping schedules and similar prompts. Compare:
- Prompt content (which rules/formulas are included)
- Script references (which script files they call)
- Schedule (same times = strong duplicate signal)
- Data sources (CoinGecko vs DexScreener vs DeFiLlama)

**Pick the canonical version** based on: most complete rules, working data sources (CoinGecko is rate-limited — prefer DexScreener/DeFiLlama), correct position data (check vault for latest range/values).

### 3. Execute Consolidation

**Update canonical job** (in the primary profile):
```python
# Read consolidated prompt from file or vault docs
with open('/tmp/consolidated-prompt.md') as f:
    new_prompt = f.read()

# Update the target job's prompt
with open(f'/root/.hermes/profiles/{profile}/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if j['id'] == target_id:
        j['prompt'] = new_prompt
        j['name'] = j['name'] + ' (Consolidated)'
with open(path, 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

**Remove duplicates** from other profiles:
```python
data['jobs'] = [j for j in data['jobs'] if j['id'] != duplicate_id]
```

**Verify** all files are valid JSON after edits.

### 4. Sync Vault Documentation

Update these files to reflect the consolidation:
- `03-Strategies/cron-jobs.md` — canonical manifest (job IDs, schedules, status)
- Related rules docs (e.g. `LP-Monitor-Rules.md`) — update job ID references

**Pattern in manifest:**
```markdown
| Former Job | Profile | ID | Reason Removed |
|------------|---------|-----|----------------|
| Job Name | ProfileName | `id123` | Consolidated into Canonical `id456` |
```

### Cron Job Model Pinning (Provider Resilience)

When the gateway provider chain is unstable (OAuth revocation, fallback failures, provider outages), cron jobs with `model: null` inherit the default provider chain and fail with `RuntimeError: No LLM provider configured` or `401` errors. This is the most common cause of mass cron failures after gateway restarts.

**Fix:** Explicitly set `model` and `provider` on each cron job to bypass the resolution chain entirely:

```python
# Via cronjob tool (gateway API) — the ONLY way to set model overrides
cronjob(action="update", job_id="<id>", model={"model": "mimo-v2.5", "provider": "custom:XiaomiMega"})
```

**⚠️ CLI limitation:** `hermes cron edit` does NOT support `--model` or `--provider` flags. The CLI only supports `--schedule`, `--prompt`, `--name`, `--deliver`, `--repeat`, `--skill`, `--script`, `--workdir`. You MUST use the `cronjob` tool (gateway API) for model overrides.

**Custom provider naming:** Custom providers defined in `custom_providers:` with a `name` field are referenced as `custom:<name>` (e.g., `custom:XiaomiMega`). The `model.provider` field in `config.yaml` uses just `custom`, but the cronjob API needs the full `custom:<name>` format.

**Batch update pattern:**
```python
# Update all jobs at once
for job_id in all_job_ids:
    cronjob(action="update", job_id=job_id, model={"model": "mimo-v2.5", "provider": "custom:XiaomiMega"})
```

**Verification:** After pinning, trigger one job with `cronjob(action="run", job_id="<id>")` and confirm `last_status: ok`.

**Session reference:** `references/cron-model-pinning-session-2026-05-05.md` — full incident timeline, provider error window, all 30 job IDs updated.

**Diagnosis shortcut:** When diagnosing mass cron failures, correlate `last_run_at` timestamps against provider error windows in `gateway.log`. Jobs that ran during a provider outage window will all show errors; jobs before/after will succeed. This temporal correlation is the fastest way to distinguish systemic (provider) vs per-job (prompt/config) failures.

**Pitfalls:**
- Jobs with `model: null` use the global default, which goes through the OAuth/fallback chain. If that chain is broken, ALL null-model jobs fail simultaneously.
- After bulk model pinning, the `last_status: error` field persists until the next successful run. Don't assume the fix didn't work just because the status still shows error.
- Delivery target validation: some jobs may have wrong Telegram chat IDs (e.g., truncated IDs). Check `deliver` field matches expected chat IDs.

### Pitfalls

- **Job ID format:** `jobs[].id` in JSON, not `job_id`. The `cronjob` tool returns `job_id` in its output but the raw JSON uses `id`.
- **JSON structure:** `{"jobs": [...]}` wrapper — a bare `[]` causes `AttributeError`. Fix: `echo '{"jobs": []}' > path`.
- **CoinGecko is rate-limited** — don't build new prompts around it. Use DexScreener (free, no key) or DeFiLlama as primary.
- **Don't remove jobs you don't fully understand** — check the prompt content before deleting. Two jobs with the same name might have different rules.
- **Gentech profile** often has a daily brief version (different purpose) that should NOT be merged with the 4×/day monitor.
- **Auto-removal on repeated failure** — cron jobs that fail repeatedly get silently removed from the list. If a job disappears, recreate it after fixing the root cause.

## Script Deployment for Cron Jobs

Scripts authored in the vault don't automatically work in cron jobs. They must be deployed to the runtime scripts directory.

### Deploy Path

```bash
# Copy script from vault to profile scripts dir
cp /root/vaults/gentech/06-Content/Skills/scripts/my-script.py \
   ~/.hermes/profiles/<profile>/scripts/my-script.py
chmod +x ~/.hermes/profiles/<profile>/scripts/my-script.py
```

Cron jobs reference scripts by filename only (`script: "my-script.py"`), and Hermes resolves them relative to `~/.hermes/profiles/<profile>/scripts/`.

### HOME Path Resolution (Critical)

Each profile sets `HOME` to its own home directory:
- **Gentech:** `HOME=/root/.hermes/profiles/gentech/home`
- **YoYo:** `HOME=/root/.hermes/profiles/yoyo/home`

This means `os.path.expanduser("~")` inside a cron script resolves to the **profile's home**, not `/root`. If your script uses `~/.hermes/scripts/`, it actually resolves to:
```
/root/.hermes/profiles/gentech/home/.hermes/scripts/
```

**Fix:** Either:
1. Put config files at the expanded path (check with `python3 -c "import os; print(os.path.expanduser('~'))"`)
2. Or use absolute paths in the script instead of `~`

### Config File Dependencies

Scripts often load config from `~/.hermes/scripts/` or similar. After deploying the script, also deploy its config:

```bash
# Find what config the script expects
grep -n "CONFIG\|config\|expanduser" my-script.py

# Deploy config to the profile's expanded home
mkdir -p ~/.hermes/profiles/<profile>/home/.hermes/scripts/
cp /root/vaults/gentech/path/to/config.json \
   ~/.hermes/profiles/<profile>/home/.hermes/scripts/
```

### Verification

After deploying script + config, test manually before relying on cron:

```bash
cd ~/.hermes/profiles/<profile>/scripts && python3 my-script.py
```

Check for JSON output (success) or error messages (missing config, API failures).

## Disaster Recovery: Skills Restore from Brain Backup

When a profile has zero or corrupted skills (e.g. after a wipe or migration), restore from the brain backup repo.

### 1. Locate the Backup
```bash
BACKUP_DIR="/root/hermes-brain-backup/skills"
ls $BACKUP_DIR/   # Should show category dirs: blockchain/, finance/, devops/, etc.
```

### 2. Restore Critical Skills First (Priority Order)
```bash
TARGET="$HOME/.hermes/skills"
mkdir -p $TARGET

# Priority 1: Core domain skills
cp -r $BACKUP_DIR/blockchain $TARGET/
cp -r $BACKUP_DIR/finance $TARGET/

# Priority 2: DevOps & operational skills
mkdir -p $TARGET/devops
for s in hermes-brain-backup hermes-vision-debug multi-agent-telegram-org \
         gentech-agent-health-diagnosis gentech-agent-reactivation; do
  cp -r $BACKUP_DIR/devops/$s $TARGET/devops/
done

# Priority 3: Everything else
for cat in github research software-development creative media mcp \
           social-media email data-science mlops productivity; do
  cp -r $BACKUP_DIR/$cat $TARGET/
done
```

### 3. Verify
```bash
find $TARGET -name "SKILL.md" | wc -l   # Should be 70+ from a full backup
```

### 4. If Brain Backup Repo Isn't Local
```bash
cd /root/hermes-brain-backup
git pull origin main
# Then run step 2 above
```

### Pitfalls
- The backup has 847 skills (all hub + custom), but only ~75 are custom domain skills. The rest auto-install via `hermes skills update`.
- Skill files use `SKILL.md` as the filename — don't rename them.
- After restore, skills load automatically on next session. No restart needed.
- The `hermes profile export/import` commands work for full profile backups, but not for individual skill cherry-picking from the brain backup repo.

---

## Skill Ecosystem Audit & Reconciliation

When skills go missing, profiles get corrupted, or you just want to know what's installed vs. what should be — run this audit workflow.

### 1. Get Installed Skills

```bash
# Via CLI
hermes skills list

# Or from the skill registry in-session
# (skills_list tool returns all loaded skills)
```

For profile-specific installs:
```bash
ls ~/.hermes/profiles/<profile>/skills/
```

### 2. Get Reference Manifest

The vault tracks what *should* be installed in `00-System/agent-profiles/<agent>/skills-manifest.txt`.

```bash
# From local vault
cat /root/vaults/gentech/00-System/agent-profiles/gentech/skills-manifest.txt

# From GitHub backup
gh api repos/Gentech-Labs/gentech-vault/contents/00-System/agent-profiles/gentech/skills-manifest.txt \
  -q '.content' | base64 -d
```

### 3. Compare & Identify Gaps

```bash
# Diff installed vs manifest
comm -23 <(hermes skills list --names | sort) <(cat manifest.txt | sort)
```

Or cross-reference the vault's skill backup in `10-Archive/Memory-Backups/`:
```bash
ls <vault>/10-Archive/Memory-Backups/<date>/*-SKILL.md \
  | sed 's/.*skills-//;s/-SKILL.md//' | sort
```

### 4. Check Pending Installs

The vault tracks skills to evaluate in `12-Skills/Skills-Tracker.md` and `02-Labs/skill-watchlist.md`. Review HIGH priority items first.

### 5. Restore Missing Skills

```bash
# From vault backup
cp -r <vault-backup>/<skill-dir> ~/.hermes/profiles/<profile>/skills/

# From hub (if available)
hermes skills install <skill-id>

# From direct URL
hermes skills install https://example.com/SKILL.md --name my-skill
```

### 6. Update Skills Manifest

After reconciliation, update the manifest so the next audit has a clean baseline:
```bash
hermes skills list --names > /tmp/current-skills.txt
# Copy to vault location
```

### 7. Set Up Weekly Cron (Optional)

Schedule a weekly skill audit that reports gaps:
```bash
hermes cron create "every Sunday 12:00" \
  --prompt "Audit installed skills against vault manifest. Report missing HIGH priority items." \
  --name "Weekly Skill Audit"
```

### Pitfalls
- **Manifest drift** — if you install skills without updating the manifest, the next audit reports false gaps
- **Profile isolation** — each profile has its own skills dir; don't copy across profiles without checking compatibility
- **Hub vs. custom** — hub skills auto-update; custom skills (saved via skill_manage) only change when you edit them
- **846 vs 75** — the full hub has 846 skills, but only ~75 are custom domain skills. The rest are hub-provided.

## Hermes Update Assessment

Before running `hermes update`, assess what's pending and whether it's safe.

### 1. Check Current vs Upstream

```bash
# Current version
hermes --version

# Check for updates (shows commits behind)
cd /usr/local/lib/hermes-agent && git fetch origin 2>&1
git log HEAD..origin/main --oneline   # list pending commits
git diff HEAD..origin/main --stat     # files changed summary
```

### 2. Assess Severity

Categorize pending commits:
- **Breaking** — changes to `run_agent.py`, `model_tools.py`, `toolsets.py`, provider adapters, config schema. Review diff carefully.
- **Feature** — new tools, new platform adapters, new CLI commands. Usually safe.
- **Fix** — bug fixes to existing features. Low risk.
- **UI/Docs** — TUI changes (`ui-tui/`), docs (`website/`), style changes. Safe to merge.

```bash
# Quick severity check
git log HEAD..origin/main --oneline | grep -E "^[a-f0-9]+ (fix|docs|style|chore)" | wc -l
# vs total
git log HEAD..origin/main --oneline | wc -l
```

### 3. Compare Skill Manifests

Skills bundled with Hermes update alongside the core. Check if local skills match upstream:

```bash
# Profile-specific skills diff
diff <(cat /usr/local/lib/hermes-agent/skills/.bundled_manifest 2>/dev/null) \
     <(cat ~/.hermes/profiles/<profile>/skills/.bundled_manifest 2>/dev/null)

# Or find skills with content differences
find /usr/local/lib/hermes-agent/skills/ -name "SKILL.md" -exec md5sum {} \; | sort > /tmp/upstream.txt
find ~/.hermes/skills/ -name "SKILL.md" -exec md5sum {} \; | sort > /tmp/local.txt
diff /tmp/upstream.txt /tmp/local.txt
```

### 4. Decision Matrix

| Scenario | Action |
|----------|--------|
| Only UI/docs fixes behind | Update anytime — low risk |
| Feature additions, no config changes | Update when convenient |
| Core agent changes (`run_agent.py`, `model_tools.py`) | Review diffs first, update during maintenance window |
| Provider adapter changes | Test with your primary provider after update |
| Skills differ between profile and upstream | Run `hermes skills update` after core update |

### 5. Apply Update

```bash
# Core update
hermes update

# Skills update (if needed)
hermes skills update

# Verify
hermes --version
hermes doctor
```

### Pitfalls
- **Custom skills** (saved via `skill_manage`) are NOT overwritten by `hermes skills update` — only hub skills update
- **Config changes** in new versions may require `hermes config migrate` — check release notes
- **Gateway restart** needed after update: `hermes gateway restart` or `/restart` in chat
- **Profile isolation** — each profile's skills update independently; run from the correct profile context

---

## Troubleshooting

### Voice not working
1. Check `stt.enabled: true` in config.yaml
2. Verify provider: `pip install faster-whisper` or set API key
3. In gateway: `/restart`. In CLI: exit and relaunch.

### Tool not available
1. `hermes tools` — check if toolset is enabled for your platform
2. Some tools need env vars (check `.env`)
3. `/reset` after enabling tools

### Model/provider issues
1. `hermes doctor` — check config and dependencies
2. `hermes login` — re-authenticate OAuth providers
3. Check `.env` has the right API key
4. **Copilot 403**: `gh auth login` tokens do NOT work for Copilot API. You must use the Copilot-specific OAuth device code flow via `hermes model` → GitHub Copilot.

### OAuth session revocation (fleet-wide)

When multiple Hermes profiles simultaneously start failing with `RuntimeError: Refresh session has been revoked`, theNous Portal OAuth refresh token has been invalidated. This affects all agents using the sameNous credentials and will trigger cascading 401 errors from any provider that relies onNous authentication.

**Detection:**
- `Nous OAuth Proactive Refresh` cron job fails with `RuntimeError: Refresh session has been revoked`
- Agent logs contain repeated: `Refresh session has been revoked Run 'hermes model' to re-authenticate.`
- Gateway messages show `RuntimeError: Error code: 401` forNous-dependent providers

**Impact:**
- LLM API calls fail (OpenRouter, Anthropic, etc.) if routed throughNous
- Cron jobs that require LLM stop working
- Voice and other provider tools fail with 401

**Recovery:**
1. On each affected profile, run `hermes model` (or `hermes login --provider nous`)
2. Complete the OAuth device code flow in a browser
3. Authenticate as the sameNous user that originally set up the profile
4. Restart the gateway: `hermes gateway restart --profile <name>`
5. Verify the `Nous OAuth Proactive Refresh` job succeeds on next tick

**Pitfalls:**
- **auth.json may appear empty** after revocation — this is normal; running `hermes model` will repopulate it with fresh tokens
- **Do NOT delete `auth.json`** — manual deletion loses all OAuth tokens; use `hermes logout` then `hermes model` for a clean re-auth
- **Gateway restart is mandatory** — without it, the running gateway process continues using the old (revoked) credentials; `hermes gateway restart --profile <name>` or `/restart` in gateway chat
- **Stagger re-authentication** if managing many profiles to avoid coordinated downtime
- **OAuth requires interactive TTY** — `hermes model` cannot be run non-interactively (it will error: "requires an interactive terminal"). Cron jobs cannot automate OAuth resolution; human intervention is required.

**Notes:**
- The `refresh_nous_oauth.py` script runs every 10 minutes but cannot recover from a revoked session — manual intervention required
- If you manage multiple profiles, consider staggered re-authentication to avoid downtime
- After recovery, check `hermes auth list` to confirm theNous credential is active

**Extended scenario — cascading credential failure:** When OAuth revocation cascades into secondary failures (Git operations for brain backup repos), see `references/brain-backup-credential-recovery.md` for the full recovery workflow: locating working PATs, writing profile-specific `.git-credentials`, SSH deploy key setup, and multi-repo coordination.

**Non-interactive OAuth constraint:** The `hermes model` OAuth flow requires an interactive TTY and cannot be run from cron jobs or non-interactive scripts. See `references/oauth-non-interactive-constraints.md` for the operational patterns: detect-only monitoring, API-key fallback for zero-touch operation, and provider selection guidance for scheduled environments.

---

### Auxiliary provider fallback and OAuth dependencies

The `auto` provider for auxiliary tasks (vision, compression, session_search, web_extract) follows a fallback chain. Understanding this chain is critical when OAuth-dependent providers fail.

**Auto-detection priority (from `_resolve_auto` in `agent/auxiliary_client.py`):**

1. **Main provider** — if the user's primary model provider is configured and working, auxiliary tasks use it directly (respects `model.provider` from config)
2. **Fallback chain** — only used when main provider is unavailable:
   - OpenRouter (requires `OPENROUTER_API_KEY`)
   - **Nous** (OAuth — requires active Nous auth)
   - Custom/local (requires `model.base_url` + `model.api_key`)
   - API-key providers (any provider with valid env var)

**Critical gotcha — explicit auxiliary overrides bypass main provider fallback:**

If `auxiliary.<task>.provider` is set explicitly in `config.yaml`, that provider is used *regardless* of the main provider's availability. Example:

```yaml
auxiliary:
  vision:
    provider: nous      # ← forcesNous even if main provider is OpenCode Go
    model: stepfun/step-3.5-flash
```

This means:
- Main provider auto-detection can fall back to OpenCode Go (API-key) ✅
- But vision tasks still try to useNous (OAuth) and will fail ❌ ifNous is logged out

**Resolution patterns:**

When an auxiliary provider's auth expires (e.g., OAuth revocation):
1. **Temporary workaround:** Clear the explicit provider to let `auto` inherit the main provider:
   ```bash
   hermes config set auxiliary.vision.provider auto
   ```
   Then the working main provider (OpenCode Go) handles vision too.

2. **Permanent fix for cron/non-interactive environments:** Use an API-key provider for auxiliary tasks to avoid OAuth dependency:
   ```bash
   # Set vision to use StepFun (if STEPFUN_API_KEY is available)
   hermes config set auxiliary.vision.provider stepfun
   hermes config set auxiliary.vision.model stepfun/step-3.5-flash
   ```
   Or change the main provider entirely via `hermes model` and pick a non-OAuth option.

3. **For all auxiliary tasks:** Apply the same pattern to `auxiliary.web_extract`, `auxiliary.compression`, `auxiliary.session_search`, etc.

**Verification:**
```bash
# Check which provider resolved for auxiliary tasks (runtime)
hermes chat -q "What is my vision provider?" \
  --toolName=get_auxiliary_extra_body 2>/dev/null || true

# Or inspect logs (gateway)
grep "Auxiliary auto-detect" ~/.hermes/logs/gateway.log | tail -5
```

**Pitfalls:**
- Setting `auxiliary.<task>.provider: auto` does NOT mean "try all providers" — it means "use the main provider", and if that fails, fall back through the chain. If the main provider is working, auxiliary tasks use it even if it's not ideal for that task type.
- Nous Portal OAuth requires interactive login — cannot be automated in cron. Do NOT rely onNous for scheduled job auxiliary tasks if you need zero-touch operation.
- Vision models vary by provider; if you switch fromNous to an API-key provider, you may need to adjust the model name (e.g., `stepfun/step-3.5-flash` vs `google/gemini-3-flash-preview`).

**Related:** See `references/oauth-non-interactive-constraints.md` for details on OAuth device_code flow limitations in cron contexts. For a deep-dive into the auto-detection fallback chain logic, see `references/auxiliary-fallback-chain.md`.

---

### Cascading credential failure: Brain backup Git push authentication

In GenTech deployments, OAuth revocation may cascade into secondary credential failures — specifically, Git operations for brain backup repos (`hermes-brain-backup`, `hermes-brain`) that rely on HTTPS credentials stored in git's credential helper. These repos maintain the shared Obsidian vault backup and agent state, and when their push credentials are invalid (placeholder `***`, expired PAT, or revoked OAuth token), the daily backup cron jobs silently fail while still committing locally. The result: the local brain backup repository accumulates commits that never reach GitHub, breaking the multi-agent shared brain.

**Pattern recognition:**
- `git push` fails with `fatal: could not read Username for 'https://github.com': No such device or address` or `Invalid username or token`
- `git status` shows commits ahead of `origin/main` but `git push` is rejected
- The brain backup cron job log shows `Auto-backup` commits locally but no push confirmation
- `~/.git-credentials` contains placeholder `***` instead of actual token
- The credential helper is `store` but points to the wrong HOME path (Hermes profiles use isolated HOME under `~/.hermes/profiles/<profile>/home/`)

**Recovery workflow:**
1. **Locate a working GitHub PAT** (Personal Access Token) in the ecosystem:
   - Check vault `.env` files (e.g., `/root/vaults/gentech/.env` for `GITHUB_PAT`)
   - Check agent profile `.env` files
   - Use `gh auth token` if GitHub CLI is authenticated (but often out of sync)
   - As last resort, generate a new fine-grained PAT with `repo` scope on GitHub

2. **Write credentials to the correct git credentials file** (Gentech-specific):
```bash
# Determine the active profile HOME (Gentech example)
PROFILE_HOME="/root/.hermes/profiles/gentech/home"
CRED_FILE="${PROFILE_HOME}/.git-credentials"

# Write credentials in store format: https://<username>:<token>@github.com
echo "https://ProtoJay4789:${GITHUB_PAT}@github.com" > "$CRED_FILE"
chmod 600 "$CRED_FILE"
```
   - **Important:** The `store` helper expands `~` relative to the gitconfig's HOME, which for Gentech is `/root/.hermes/profiles/gentech/home`, NOT `/root`. The Gentech gitconfig at that location sets `credential.helper=store`.

3. **Verify the credential helper resolution:**
```bash
# From the brain backup repo directory, test credential fill
git credential fill <<EOF
protocol=https
host=github.com
EOF
# Should output: username=<user>\npassword=<token>
```

4. **Ensure the git remote is HTTPS (not SSH) for credential helper:**
```bash
git remote set-url origin https://github.com/Gentech-Labs/<repo>.git
```

5. **Test push with verbose output:**
```bash
git push origin main --verbose
```

6. **If HTTPS still fails, switch to SSH deploy key** (more reliable for automated cron):
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "hermes-brain-backup@gentechlabs.io" -f ~/.ssh/hermes-brain-backup -N ""

# Add to ~/.ssh/config to force use for github.com
cat >> ~/.ssh/config <<EOF
Host github.com
  IdentityFile /root/.ssh/hermes-brain-backup
  IdentitiesOnly yes
EOF
chmod 600 ~/.ssh/config

# Change remote to SSH
git remote set-url origin git@github.com:Gentech-Labs/<repo>.git

# Add public key as a Deploy Key in GitHub repo settings (requires owner access)
# Then test
ssh -i ~/.ssh/hermes-brain-backup -o BatchMode=yes git@github.com
# Should succeed with "successfully authenticated" message
```

**Multi-repo coordination:**
GenTech maintains two brain backup repositories:
- `/root/hermes-brain-backup` — vault + skills backup (`Gentech-Labs/hermes-brain-backup`)
- `/root/repos/hermes-brain` — agent memory/config backup (`Gentech-Labs/hermes-brain`)

Both need working credentials independently. Run the recovery steps for each repo.

**Pitfalls:**
- **Wrong HOME for credentials** — each Hermes profile has isolated HOME; credentials must be placed in that profile's home, not `/root`
- **Placeholder `***` in `.git-credentials`** indicates redacted password from previous audit; replace with actual token
- **Credential helper hierarchy** — repo-local `.git/config` overrides global gitconfig; check `git config --show-origin credential.helper` to see which file sets the helper
- **SSH key not added to GitHub** — generating a key locally is not enough; must add the public key as a Deploy Key in the repo settings with Write access
- **gh CLI token ≠ Git credential** — GitHub CLI tokens sometimes lack `git` permission or use a different auth mechanism; if `gh auth token` fails as Git password, use a classic PAT or SSH
- **Multiple remotes** — always verify `git remote -v` before push; some repos accidentally use SSH while credentials are configured for HTTPS
- **Silent cron failure** — the backup script commits locally even if push fails, so the repo grows ahead of origin; check `git rev-list --left-right --count HEAD...origin/main` to detect drift

### Changes not taking effect
- **Tools/skills:** `/reset` starts a new session with updated toolset
- **Config changes:** In gateway: `/restart`. In CLI: exit and relaunch.
- **Code changes:** Restart the CLI or gateway process

### Skills not showing
1. `hermes skills list` — verify installed
2. `hermes skills config` — check platform enablement
3. Load explicitly: `/skill name` or `hermes -s name`

### Gateway issues
Check logs first:
```bash
grep -i "failed to send\|error" ~/.hermes/logs/gateway.log | tail-20
```

Common gateway problems:
- **Gateway dies on SSH logout**: Enable linger: `sudo loginctl enable-linger $USER`
- **Gateway dies on WSL2 close**: WSL2 requires `systemd=true` in `/etc/wsl.conf` for systemd services to work. Without it, gateway falls back to `nohup` (dies when session closes).
- **Gateway crash loop**: Reset the failed state: `systemctl --user reset-failed hermes-gateway`

### Platform-specific issues
- **Discord bot silent**: Must enable **Message Content Intent** in Bot → Privileged Gateway Intents.
- **Slack bot only works in DMs**: Must subscribe to `message.channels` event. Without it, the bot ignores public channels.
- **Windows HTTP 400 "No models provided"**: Config file encoding issue (BOM). Ensure `config.yaml` is saved as UTF-8 without BOM.

### Cron jobs: 'list' object has no attribute 'get'

When `hermes cron list` or `hermes cron create` throws `AttributeError: 'list' object has no attribute 'get'`, the cron `jobs.json` file is corrupted — it contains a bare JSON array `[]` instead of the expected `{"jobs": [...]}` wrapper.

Diagnose:
```bash
cat ~/.hermes/profiles/<profile>/cron/jobs.json
# If output is just [] — that's the problem
```

Fix:
```bash
echo '{"jobs": []}' > ~/.hermes/profiles/<profile>/cron/jobs.json
```

For the default profile, the path is `~/.hermes/cron/jobs.json`. For named profiles, it's `~/.hermes/profiles/<name>/cron/jobs.json`.

After fixing, verify:
```bash
hermes cron list    # should return empty list, no error
```

This usually happens after a failed cron operation or manual file edit. The `cronjob` tool calls `load_jobs()` which does `data.get("jobs", [])` — so the file must be a dict with a `"jobs"` key, not a bare list.

### Profile config.yaml is invalid YAML

When a gateway fails to start or a profile behaves unexpectedly, the `config.yaml` may contain a YAML syntax error. Even if the gateway is currently running, a restart will fail to load the profile.

**Diagnose:**
```bash
hermes profile show <profile>  # may show parse error
# Or test directly:
python3 -c "import yaml; yaml.safe_load(open('/root/.hermes/profiles/<profile>/config.yaml','r'))"
```

**Example error:** `yaml.scanner.ScannerError: mapping values are not allowed here in "config.yaml", line 130, column 13`

**Common cause:** Incorrect indentation under nested keys, especially in the `auxiliary:` section. Example broken pattern:
```yaml
auxiliary:
  vision:
    provider: ollama-cloud
  default: mistral-large-3:675b
    base_url: https://ollama.com/v1   # ← wrong: base_url must be indented under default
```

**Fix:** Ensure all keys under a mapping are indented consistently. The corrected version:
```yaml
auxiliary:
  vision:
    provider: ollama-cloud
  default:
    model: mistral-large-3:675b
    base_url: https://ollama.com/v1
```

### Cron zombie — gateway alive but jobs not firing

A separate failure mode from stale `next_run_at`: the gateway process is running (PID exists), `hermes cron list` shows jobs with valid future `next_run_at` timestamps, but `last_run_at` has not updated for days and no new sessions are spawned.

**Symptoms:**
- `ps aux | grep hermes` shows gateway PID
- `next_run_at` is in the future
- `last_run_at` stayed constant for 5+ days
- `agent.log` shows `OSError: [Errno 5] Input/output error` (gateway TUI crashed but process didn't exit)

**Root cause:** The scheduler's internal `AsyncioScheduler` or cron loop has silently died (e.g., after a terminal disconnect) while the gateway process remains alive as a zombie.

**Fix:** Restart the gateway with `--replace` to create a fresh scheduler instance:
```bash
hermes gateway run --profile <profile> --replace
```

**After restart, verify:**
```bash
hermes cron list  # check last_run_at updates after next scheduled time
```

**Pitfalls:**
- `hermes cron tick` will not resurrect a dead scheduler — it only triggers already-queued jobs
- `--replace` is safer than `kill` + `start` because it prevents orphaned socket file issues
- Check for config YAML errors (see section above) before restarting — a bad `config.yaml` will cause the new gateway to crash immediately

### Cron jobs stuck — next_run_at in the past

When `hermes cron list` shows jobs but they never fire, or the scheduler silently skips them, the `next_run_at` timestamps in `jobs.json` are stuck in the past. This happens after gateway restarts, profile migrations, or when the scheduler process was down for an extended period.

**Diagnose:**
```bash
# Check for past-due jobs across all profiles
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import json, os
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
for profile in ['gentech', 'yoyo', 'dmob', 'desmond']:
    path = f'/root/repos/hermes-brain/profiles/{profile}/cron/jobs.json'
    if not os.path.exists(path): continue
    with open(path) as f:
        data = json.load(f)
    for job in data.get('jobs', []):
        nr = job.get('next_run_at')
        if nr and datetime.fromisoformat(nr) < now:
            print(f'PAST DUE: [{profile}] {job[\"name\"]} (next: {nr})')
"
```

**Fix — recalculate all stale timestamps:**
```bash
/usr/local/lib/hermes-agent/venv/bin/python3 -c "
import json, os
from datetime import datetime, timezone
from croniter import croniter

profiles = ['gentech', 'yoyo', 'dmob', 'desmond']
now = datetime.now(timezone.utc)

for profile in profiles:
    path = f'/root/repos/hermes-brain/profiles/{profile}/cron/jobs.json'
    if not os.path.exists(path): continue
    with open(path) as f:
        data = json.load(f)
    modified = False
    for job in data.get('jobs', []):
        nr = job.get('next_run_at')
        if nr and datetime.fromisoformat(nr) < now:
            schedule = job.get('schedule', {})
            expr = schedule.get('expr', '')
            kind = schedule.get('kind', '')
            if kind == 'interval':
                minutes = schedule.get('minutes', 60)
                new_next = now + timedelta(minutes=minutes)
            elif expr:
                new_next = croniter(expr, now).get_next(datetime)
            else:
                continue
            job['next_run_at'] = new_next.isoformat()
            modified = True
            print(f'FIXED: [{profile}] {job[\"name\"]} -> {new_next.isoformat()}')
    if modified:
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
"
```

**After fixing, restart affected gateways:**
```bash
hermes gateway restart --profile <profile>
```

**Pitfalls:**
- **Jobs.json path** — cron data lives at `/root/repos/hermes-brain/profiles/<profile>/cron/jobs.json`, not `~/.hermes/`
- **Interval vs cron** — jobs with `"kind": "interval"` use `schedule.minutes`, not a cron expression. Handle separately with `timedelta`
- **Gateway may create duplicate entries** — after restart, the gateway might assign new IDs to jobs. Check for duplicates in the JSON and remove stale entries
- **Delivery errors after restart** — `cannot schedule new futures after interpreter shutdown` is transient and clears on next fire
- **croniter required** — install if missing: `/usr/local/lib/hermes-agent/venv/bin/pip install croniter` (usually pre-installed)
- **`hermes cron tick`** may not fix stale timestamps — it runs due jobs but doesn't always recalculate `next_run_at` for future ones

### Auxiliary models not working

If `auxiliary` tasks (vision, compression, session_search) fail silently, the `auto` provider can't find a backend. Either set `OPENROUTER_API_KEY` or `GOOGLE_API_KEY`, or explicitly configure each auxiliary task's provider:
```bash
hermes config set auxiliary.vision.provider <your_provider>
hermes config set auxiliary.vision.model <model_name>
```

**Xiaomi MiMo vision support:** MiMo-V2.5 is a native omnimodal model (text, image, video, audio) with a 729M-param Vision Transformer. If your main model is MiMo-V2.5 via a custom provider, you can point the vision auxiliary to the same endpoint:

```yaml
auxiliary:
  vision:
    provider: custom        # or your custom provider name
    model: mimo-v2.5
    base_url: https://token-plan-sgp.xiaomimimo.com/v1
    api_key: <your-xiaomi-key>
```

This avoids the common pitfall of vision pointing at a dead `ollama-cloud` + `gemini-3-flash-preview` combo (which returns `400: Not supported model`). The Xiaomi API accepts image inputs natively.

**Pitfall:** If `auxiliary.vision.provider` is set to `ollama-cloud` with `gemini-3-flash-preview`, vision will fail with a 400 error even though the main model works fine — the auxiliary config is independent of the main model config.

---

## Contributor Quick Reference

For occasional contributors and PR authors. Full developer docs: https://hermes-agent.nousresearch.com/docs/developer-guide/

### Project Layout

```
hermes-agent/
├── run_agent.py          # AIAgent — core conversation loop
├── model_tools.py        # Tool discovery and dispatch
├── toolsets.py           # Toolset definitions
├── cli.py                # Interactive CLI (HermesCLI)
├── hermes_state.py       # SQLite session store
├── agent/                # Prompt builder, context compression, memory, model routing, credential pooling, skill dispatch
├── hermes_cli/           # CLI subcommands, config, setup, commands
│   ├── commands.py       # Slash command registry (CommandDef)
│   ├── config.py         # DEFAULT_CONFIG, env var definitions
│   └── main.py           # CLI entry point and argparse
├── tools/                # One file per tool
│   └── registry.py       # Central tool registry
├── gateway/              # Messaging gateway
│   └── platforms/        # Platform adapters (telegram, discord, etc.)
├── cron/                 # Job scheduler
├── tests/                # ~3000 pytest tests
└── website/              # Docusaurus docs site
```

Config: `~/.hermes/config.yaml` (settings), `~/.hermes/.env` (API keys).

### Adding a Tool (3 files)

**1. Create `tools/your_tool.py`:**
```python
import json, os
from tools.registry import registry

def check_requirements() -> bool:
    return bool(os.getenv("EXAMPLE_API_KEY"))

def example_tool(param: str, task_id: str = None) -> str:
    return json.dumps({"success": True, "data": "..."})

registry.register(
    name="example_tool",
    toolset="example",
    schema={"name": "example_tool", "description": "...", "parameters": {...}},
    handler=lambda args, **kw: example_tool(
        param=args.get("param", ""), task_id=kw.get("task_id")),
    check_fn=check_requirements,
    requires_env=["EXAMPLE_API_KEY"],
)
```

**2. Add to `toolsets.py`** → `_HERMES_CORE_TOOLS` list.

Auto-discovery: any `tools/*.py` file with a top-level `registry.register()` call is imported automatically — no manual list needed.

All handlers must return JSON strings. Use `get_hermes_home()` for paths, never hardcode `~/.hermes`.

### Adding a Slash Command

1. Add `CommandDef` to `COMMAND_REGISTRY` in `hermes_cli/commands.py`
2. Add handler in `cli.py` → `process_command()`
3. (Optional) Add gateway handler in `gateway/run.py`

All consumers (help text, autocomplete, Telegram menu, Slack mapping) derive from the central registry automatically.

### Agent Loop (High Level)

```
run_conversation():
  1. Build system prompt
  2. Loop while iterations < max:
     a. Call LLM (OpenAI-format messages + tool schemas)
     b. If tool_calls → dispatch each via handle_function_call() → append results → continue
     c. If text response → return
  3. Context compression triggers automatically near token limit
```

### Testing

```bash
python -m pytest tests/ -o 'addopts=' -q   # Full suite
python -m pytest tests/tools/ -q            # Specific area
```

- Tests auto-redirect `HERMES_HOME` to temp dirs — never touch real `~/.hermes/`
- Run full suite before pushing any change
- Use `-o 'addopts='` to clear any baked-in pytest flags

### Commit Conventions

```
type: concise subject line

Optional body.
```

Types: `fix:`, `feat:`, `refactor:`, `docs:`, `chore:`

### Key Rules

- **Never break prompt caching** — don't change context, tools, or system prompt mid-conversation
- **Message role alternation** — never two assistant or two user messages in a row
- Use `get_hermes_home()` from `hermes_constants` for all paths (profile-safe)
- Config values go in `config.yaml`, secrets go in `.env`
- New tools need a `check_fn` so they only appear when requirements are met

---

## GenTech Installation Details

This section captures environment-specific setup and operational details for the GenTech Hermes installation that differ from vanilla upstream documentation.

### Actual Installation Paths

| Standard path | Gentech actual |
|---------------|----------------|
| `~/.hermes/hermes-agent/` (source install) | **N/A — not used** |
| Source code location | `/usr/local/lib/hermes-agent/` (pip-installed package, includes .git) |
| Hermes binary | `/usr/local/lib/hermes-agent/venv/bin/hermes` |
| Skills base dir | `/usr/local/lib/hermes-agent/skills/` |
| Hub skills in repo | `/usr/local/lib/hermes-agent/skills/<category>/` |
| Custom skill sync dir | **Git-based:** `/root/skills/` (vault mirror) → may be copied into `/usr/local/lib/hermes-agent/skills/gentech/` |

**Discovery:** `pip show hermes-agent` returns `Location: /usr/local/lib/hermes-agent`. That directory is the git clone of `https://github.com/NousResearch/hermes-agent.git` with `origin` as the sole remote.

### Sync Status Workflow (GenTech)

No `upstream` remote exists. Compare against `origin/main`:

```bash
cd /usr/local/lib/hermes-agent
git fetch origin
git rev-list --left-right --count HEAD...origin/main   # "<behind> <ahead>"
git log HEAD..origin/main --oneline                     # commits to pull
git log origin/main..HEAD --oneline                     # local-only commits
```

**Pitfall:** The expected fork location `/root/hermes-agent` does not exist on this system. Always check the installed package path.

### Custom Skill Deployment

GenTech maintains custom skill definitions in `/root/skills/gentech/`. The skill manager does not auto-deploy there. To make them available to Hermes, copy or symlink into `/usr/local/lib/hermes-agent/skills/gentech/` and verify the skill appears in `hermes skills list`.

**Check current manifest:**
```bash
find /usr/local/lib/hermes-agent/skills/ -name SKILL.md | wc -l   # upstream docs
find /root/skills/ -name SKILL.md | wc -l                        # vault copy
```
