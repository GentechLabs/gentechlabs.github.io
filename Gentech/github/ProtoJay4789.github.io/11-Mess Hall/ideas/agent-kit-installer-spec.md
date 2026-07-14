# GenTech Agent Kit Installer — Full Spec

> **Status:** Spec Complete (Phase 1 MVP — CLI)
> **Created:** 2026-06-18
> **Source:** ideas.md + Jordan voice message (2026-06-16)
> **Repo:** github.com/ProtoJay4789/genTech-agent-kit
> **Tagline:** "One command. Full stack. Your agent, running."

---

## 1. Vision

The GenTech Agent Kit Installer packages the entire GenTech stack into a single installable artifact. One command downloads, configures, and launches a fully operational Hermes agent pre-loaded with GenTech skills, cron jobs, dashboards, and wallet infrastructure.

**Target users:** Power users, hackathon builders, GenTech contributors, and anyone who wants their own local agent running in under 5 minutes.

---

## 2. What Gets Installed

### 2.1 Core Runtime
| Component | Description |
|---|---|
| **Hermes Agent CLI** | The main agent runtime (Python, via pip or binary) |
| **Node.js + npm** | Required for skills, dashboards, and x402 tooling |
| **Python 3.11+** | Hermes backend dependency |
| **Git** | For repo sync, backup, and skill updates |

### 2.2 GenTech Profile
| Component | Description |
|---|---|
| **~/.hermes/profiles/gentech/** | Full profile directory (skills, plugins, cron, memories) |
| **Skills (~100+)** | DeFi monitoring, dashboard builders, search, wallet ops, etc. |
| **Cron jobs (22 active)** | Portfolio sync, LP monitoring, news scans, social alerts |
| **Plugins** | BlockRun, Pay, MCP integrations |
| **Memories** | Seed memory files for GenTech context |

### 2.3 Dashboards
| Dashboard | Status |
|---|---|
| 🍳 Cookbook | ✅ LIVE |
| 📓 Journal | ✅ LIVE |
| ✈️ Travel | ✅ LIVE |
| 🎮 Gaming | ✅ LIVE |
| 💰 Finance | ✅ LIVE |

### 2.4 Wallet & DeFi Infrastructure
| Component | Description |
|---|---|
| **BlockRun wallet** | USDC payment wallet (Base + Solana) |
| **Funding wizard** | QR code + top-up instructions |
| **LFJ LP Monitor** | Liquidity position tracking |
| **Compound/Extract Protocol** | LP profit extraction (when available) |
| **ERC-8004 identity** | Agent-to-Agent Economy identity layer |

### 2.5 AAE (Agent-to-Agent Economy) Stack
| Component | Description |
|---|---|
| **AgentEscrow** | Trustless agent-to-agent payments |
| **Agent Credit Score** | On-chain reputation |
| **WURK.FUN integration** | Agent-to-human microtasks |
| **BlockRun x402** | AI model routing + payments |

### 2.6 Backup & Sync
| Component | Description |
|---|---|
| **GitHub backup config** | Auto-commit profile changes |
| **Vault sync** | Optional cloud backup of memories/skills |

---

## 3. Platform Support

### Phase 1: CLI MVP (bash script)
- **Linux** (Ubuntu, Debian, Arch, Fedora) — primary
- **macOS** (Intel + Apple Silicon) — via Homebrew detection
- **Windows** — via WSL2 or Git Bash (Phase 1 limitation)

### Phase 2: GUI Installer
- **Windows** — Electron or Tauri native app
- **macOS** — .app bundle (Tauri)
- **Linux** — AppImage / .deb / .rpm

---

## 4. Prerequisites

| Prerequisite | Auto-installed? | Notes |
|---|---|---|
| Python 3.11+ | ⚠️ Checks, suggests install | Hermes requires this |
| pip | ✅ | Comes with Python |
| Node.js 18+ | ✅ (via nvm or system pkg) | Dashboard + skill runtime |
| npm | ✅ | Comes with Node.js |
| Git | ✅ (via system pkg) | Repo sync |
| curl / wget | ✅ (usually pre-installed) | Downloads |
| BlockRun API key | ❌ (user provides) | x402 payments, AI routing |
| Hermes license key | ❌ (user provides) | If using paid features |

---

## 5. Installation Flow (Phase 1 — CLI)

### Step-by-step execution:

```
1. System check
   ├── Detect OS (Linux/macOS/WSL)
   ├── Detect architecture (x86_64/arm64)
   ├── Check Python, Node, Git versions
   └── Install missing prerequisites (with user consent)

2. Hermes install
   ├── pip install hermes-agent (or from git)
   ├── Verify: hermes --version
   └── Create ~/.hermes/ directory structure

3. GenTech profile setup
   ├── Clone/download genTech-agent-kit repo
   ├── Copy profile skeleton to ~/.hermes/profiles/gentech/
   ├── Install skills (npm packages + custom skills)
   └── Install plugins (BlockRun, Pay, MCP)

4. Configuration wizard
   ├── API key entry (BlockRun, OpenAI, etc.)
   ├── Wallet creation or import
   ├── Dashboard selection (which suites to enable)
   ├── Cron job activation (which jobs to enable)
   └── GitHub backup setup (optional)

5. Post-install verification
   ├── hermes --version ✓
   ├── hermes profile list ✓ (gentech appears)
   ├── hermes skills list ✓ (100+ skills loaded)
   ├── hermes cron list ✓ (22 jobs configured)
   ├── Dashboard smoke test (start + health check)
   ├── Wallet status check
   └── Generate install report → ~/.hermes/agent-kit-install.log

6. Success message
   ├── Summary of what was installed
   ├── First-run command: `hermes start --profile gentech`
   └── Link to dashboard, docs, community
```

---

## 6. Configuration Wizard

The CLI wizard is interactive (prompts) or accepts flags for non-interactive mode:

### Flags (non-interactive)
```bash
./install.sh \
  --blockrun-key=sk_xxx \
  --openai-key=sk-xxx \
  --wallet-create \
  --dashboards=cookbook,journal,travel,gaming,finance \
  --crons=all \
  --github-backup=user/repo \
  --non-interactive
```

### Interactive prompts
1. **"Welcome to GenTech Agent Kit"** — intro screen
2. **"Which AI provider keys do you have?"** — checklist
3. **"Create a new wallet or import existing?"** — choice
4. **"Which dashboards to enable?"** — multi-select
5. **"Enable cron jobs?"** — yes/all/custom/none
6. **"Set up GitHub backup?"** — repo URL or skip
7. **"Ready to install?"** — confirmation + progress bar

---

## 7. Post-Install Verification

Every install produces a verification report at `~/.hermes/agent-kit-install.log`:

```
=== GenTech Agent Kit Install Report ===
Date: 2026-06-18
OS: Linux x86_64
Hermes version: 2.3.1
Python: 3.11.4
Node: 20.14.0

✓ Hermes CLI installed
✓ GenTech profile created (~/.hermes/profiles/gentech/)
✓ Skills loaded: 112
✓ Cron jobs configured: 22
✓ Dashboards enabled: 5 (cookbook, journal, travel, gaming, finance)
✓ BlockRun wallet: 0xabc...def (Base)
✓ Plugins installed: blockrun, pay, mcp
✓ Git backup configured: github.com/user/gentech-backup

⚠ BlockRun API key: NOT SET (required for x402 payments)
⚠ OpenAI key: NOT SET (required for GPT image generation)

Installation complete! Run: hermes start --profile gentech
```

---

## 8. Phase 1: CLI MVP — Bash Script Design

### Script: `install.sh`

```bash
#!/usr/bin/env bash
# GenTech Agent Kit Installer v0.1.0
# Usage: curl -fsSL https://raw.githubusercontent.com/ProtoJay4789/genTech-agent-kit/main/install.sh | bash

set -euo pipefail

# --- Constants ---
INSTALL_DIR="${HOME}/.hermes"
PROFILE_DIR="${INSTALL_DIR}/profiles/gentech"
REPO_URL="https://github.com/ProtoJay4789/genTech-agent-kit"
SCRIPT_VERSION="0.1.0"
LOG_FILE="${INSTALL_DIR}/agent-kit-install.log"

# --- Colors ---
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'

# --- Functions ---
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

check_os() {
  case "$(uname -s)" in
    Linux*)  OS="linux";  ARCH="$(uname -m)" ;;
    Darwin*) OS="macos";  ARCH="$(uname -m)" ;;
    MINGW*|MSYS*) OS="windows-wsl"; ARCH="x86_64" ;;
    *) error "Unsupported OS: $(uname -s)" ;;
  esac
  info "Detected: ${OS} ${ARCH}"
}

check_prereqs() {
  local missing=()
  command -v python3 >/dev/null || missing+=("python3")
  command -v pip3    >/dev/null || missing+=("pip3")
  command -v node    >/dev/null || missing+=("node")
  command -v npm     >/dev/null || missing+=("npm")
  command -v git     >/dev/null || missing+=("git")
  command -v curl    >/dev/null || missing+=("curl")

  if [ ${#missing[@]} -gt 0 ]; then
    warn "Missing: ${missing[*]}"
    read -rp "Install missing dependencies? [y/N] " answer
    if [[ "$answer" =~ ^[Yy] ]]; then
      install_missing "${missing[@]}"
    else
      error "Cannot continue without: ${missing[*]}"
    fi
  fi
  success "All prerequisites met"
}

install_missing() {
  for pkg in "$@"; do
    case "$pkg" in
      python3|pip3)
        if [ "$OS" = "macos" ]; then brew install python@3.11
        else sudo apt-get install -y python3 python3-pip 2>/dev/null || sudo dnf install -y python3 python3-pip; fi ;;
      node|npm)
        curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
        export NVM_DIR="$HOME/.nvm"; . "$NVM_DIR/nvm.sh"
        nvm install 20 ;;
      git)
        if [ "$OS" = "macos" ]; then xcode-select --install 2>/dev/null || true
        else sudo apt-get install -y git; fi ;;
      curl) sudo apt-get install -y curl ;;
    esac
  done
}

install_hermes() {
  info "Installing Hermes Agent CLI..."
  pip3 install --upgrade hermes-agent 2>/dev/null || pip3 install --upgrade git+https://github.com/NousResearch/hermes-agent.git
  hermes --version >/dev/null 2>&1 || error "Hermes install failed"
  success "Hermes installed: $(hermes --version)"
}

setup_profile() {
  info "Setting up GenTech profile..."
  mkdir -p "${INSTALL_DIR}/profiles"

  if [ -d "$PROFILE_DIR" ]; then
    warn "Profile exists at ${PROFILE_DIR}"
    read -rp "Overwrite? [y/N] " answer
    [[ ! "$answer" =~ ^[Yy] ]] && { info "Skipped profile setup"; return 0; }
    mv "$PROFILE_DIR" "${PROFILE_DIR}.bak.$(date +%s)"
  fi

  # Clone agent kit
  local tmpdir
  tmpdir=$(mktemp -d)
  git clone --depth 1 "$REPO_URL" "$tmpdir/genTech-agent-kit"
  cp -r "$tmpdir/genTech-agent-kit/profiles/gentech/"* "$PROFILE_DIR/"
  rm -rf "$tmpdir"

  success "GenTech profile created"
}

install_skills() {
  info "Installing skills..."
  cd "$PROFILE_DIR/skills"
  if [ -f package.json ]; then
    npm install --production 2>/dev/null || warn "Some npm skills failed"
  fi
  success "Skills installed"
}

install_plugins() {
  info "Installing plugins..."
  if [ -f "${PROFILE_DIR}/plugins/package.json" ]; then
    cd "${PROFILE_DIR}/plugins"
    npm install --production 2>/dev/null || warn "Some plugins failed"
  fi
  success "Plugins installed"
}

config_wizard() {
  info "=== Configuration Wizard ==="
  local config="${PROFILE_DIR}/config.env"

  # API Keys
  echo ""
  read -rp "BlockRun API key (or skip): " blockrun_key
  read -rp "OpenAI API key (or skip): " openai_key

  # Wallet
  echo ""
  echo "Wallet options:"
  echo "  1) Create new wallet"
  echo "  2) Import existing (seed phrase)"
  echo "  3) Skip"
  read -rp "Choice [1-3]: " wallet_choice

  # Dashboards
  echo ""
  echo "Enable dashboards (comma-separated, or 'all'/'none'):"
  read -rp "Dashboards: " dashboards

  # Cron jobs
  echo ""
  read -rp "Enable all cron jobs? [Y/n]: " enable_crons

  # GitHub backup
  echo ""
  read -rp "GitHub backup repo (user/repo) or skip: " github_repo

  # Write config
  cat > "$config" << EOF
# GenTech Agent Kit — Generated $(date -Iseconds)
BLOCKRUN_KEY=${blockrun_key:-}
OPENAI_KEY=${openai_key:-}
WALLET_MODE=${wallet_choice:-skip}
DASHBOARDS=${dashboards:-all}
ENABLE_CRONS=${enable_crons:-y}
GITHUB_BACKUP=${github_repo:-}
EOF

  success "Configuration saved"
}

verify_install() {
  info "Running post-install verification..."
  local pass=0 fail=0

  check() {
    if $1 >/dev/null 2>&1; then
      success "$2"; ((pass++))
    else
      warn "$2 — FAILED"; ((fail++))
    fi
  }

  check "hermes --version" "Hermes CLI"
  check "test -d ${PROFILE_DIR}" "GenTech profile directory"
  check "test -f ${PROFILE_DIR}/skills/package.json" "Skills package.json"
  check "test -f ${PROFILE_DIR}/config.env" "Config file"

  # Write report
  {
    echo "=== GenTech Agent Kit Install Report ==="
    echo "Date: $(date -Iseconds)"
    echo "OS: ${OS} ${ARCH}"
    echo "Hermes: $(hermes --version 2>/dev/null || echo 'N/A')"
    echo "Python: $(python3 --version 2>/dev/null || echo 'N/A')"
    echo "Node: $(node --version 2>/dev/null || echo 'N/A')"
    echo "Checks passed: ${pass}"
    echo "Checks failed: ${fail}"
    echo "Install dir: ${PROFILE_DIR}"
  } > "$LOG_FILE"

  echo ""
  success "Installation complete! (${pass} passed, ${fail} warnings)"
  echo ""
  info "Next steps:"
  echo "  1. Edit ${config:-$PROFILE_DIR/config.env} with your API keys"
  echo "  2. Run: hermes start --profile gentech"
  echo "  3. Dashboard: open http://localhost:3000"
  echo ""
}

# --- Main ---
main() {
  echo -e "${BLUE}"
  echo "╔══════════════════════════════════════════╗"
  echo "║   GenTech Agent Kit Installer v${SCRIPT_VERSION}   ║"
  echo "║   'One command. Full stack.'            ║"
  echo "╚══════════════════════════════════════════╝"
  echo -e "${NC}"

  check_os
  check_prereqs
  install_hermes
  setup_profile
  install_skills
  install_plugins
  config_wizard
  verify_install
}

main "$@"
```

---

## 9. Phase 2: GUI Installer (Future)

### Technology: Tauri (Rust + WebView)
- Small binary size (~5MB vs Electron's ~150MB)
- Native feel on all platforms
- Rust backend for system operations
- React/Svelte frontend for the wizard UI

### GUI screens:
1. **Welcome** — GenTech branding, version, "Start Install"
2. **Prerequisites** — auto-detect + install with progress bars
3. **Configuration** — API keys (masked input), wallet setup (visual)
4. **Dashboard selector** — card grid with previews, toggle on/off
5. **Installation** — real-time log viewer, progress bar, step indicators
6. **Complete** — success screen, quick-start buttons, community links

### Distribution:
- Windows: `.msi` installer via GitHub Releases
- macOS: `.dmg` with notarization
- Linux: AppImage (universal), `.deb`, `.rpm`

---

## 10. Directory Structure (Installed)

```
~/.hermes/
├── agent-kit-install.log          # Install report
├── profiles/
│   └── gentech/
│       ├── skills/
│       │   ├── package.json
│       │   ├── defi-monitor/
│       │   ├── dashboard-builder/
│       │   ├── wallet-ops/
│       │   └── ... (100+ skill dirs)
│       ├── plugins/
│       │   ├── blockrun/
│       │   ├── pay/
│       │   └── mcp/
│       ├── cron/
│       │   └── gentech-jobs.json   # 22 cron definitions
│       ├── memories/
│       │   └── seed-context.md
│       ├── config.env              # User config (API keys, prefs)
│       └── dashboards/
│           ├── cookbook/
│           ├── journal/
│           ├── travel/
│           ├── gaming/
│           └── finance/
```

---

## 11. Uninstall

```bash
./install.sh --uninstall
# Removes ~/.hermes/profiles/gentech/ only
# Does NOT remove Hermes itself or other profiles
```

---

## 12. Update

```bash
./install.sh --update
# Pulls latest skills, cron jobs, dashboards
# Preserves config.env and user memories
# Backs up existing profile before overwriting
```

---

## 13. Success Metrics

| Metric | Target |
|---|---|
| Time to install (clean machine) | < 5 minutes |
| Time to install (existing setup) | < 2 minutes |
| Platforms supported (Phase 1) | Linux + macOS + WSL |
| First-run success rate | > 90% |
| Post-install verification pass | > 95% of checks |

---

## 14. Open Questions

1. **Hermes distribution** — Is hermes-agent on PyPI? If not, what's the canonical install method?
2. **Skill licensing** — Some skills may have dependencies on paid APIs. How to handle gracefully?
3. **Wallet security** — Should we generate a new wallet or let users import? Seed phrase handling?
4. **Auto-update** — Should the Agent Kit self-update on launch?
5. **GenTech branding** — Logo assets, color scheme for installer UI?
