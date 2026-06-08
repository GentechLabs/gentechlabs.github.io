# Local Hermes GPU Setup Guide — RTX 3070

**Target:** Jordan's Windows workstation
**Specs:** RTX 3070 (8GB VRAM), Intel i7, 32GB RAM
**Goal:** Run Hermes locally with GPU acceleration for faster hackathon iteration

---

## Option A: WSL2 + CUDA (Recommended)

Hermes runs natively on Linux. WSL2 with CUDA support gives you full GPU access on Windows.

### Prerequisites
1. **Windows 10/11** with WSL2 enabled
2. **NVIDIA GPU drivers** installed on Windows (not inside WSL)
3. **CUDA toolkit for WSL** (Windows-side)

### Step 1: Enable WSL2
```powershell
# In PowerShell (Admin)
wsl --install
# Restart computer
# Set Ubuntu as default
wsl --set-default Ubuntu
```

### Step 2: Install CUDA in WSL
```bash
# Inside WSL Ubuntu
# CUDA toolkit (WSL-specific package)
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-4
```

### Step 3: Verify GPU Access
```bash
nvidia-smi
# Should show RTX 3070 with CUDA version
```

### Step 4: Install Hermes
```bash
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Step 5: Configure for Local LLM
```bash
# Install Ollama for local inference
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model that fits 8GB VRAM
ollama pull llama3.1:8b        # 4.7GB — fits comfortably
ollama pull codellama:13b      # 7.4GB — tighter but works
ollama pull mistral:7b         # 4.1GB — fast and capable

# Start Ollama server
ollama serve
```

### Step 6: Configure Hermes to Use Local Model
```bash
hermes config set model.default llama3.1:8b
hermes config set model.provider ollama
hermes config set model.base_url http://localhost:11434/v1
```

### Step 7: Connect to Telegram
```bash
# Set up Telegram in Hermes
hermes gateway setup
# Select Telegram, enter bot token

# Start gateway
hermes gateway run
```

---

## Option B: Native Windows (Simpler, Less GPU Control)

### Prerequisites
- Node.js 22+ installed
- Python 3.11+ installed

### Step 1: Install Hermes
```powershell
# In PowerShell
npm install -g hermes-agent
# Or use the install script
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

### Step 2: Install Ollama (Windows native)
```powershell
# Download from https://ollama.com/download/windows
# Or use winget
winget install Ollama.Ollama
```

### Step 3: Pull Model
```powershell
ollama pull llama3.1:8b
```

### Step 4: Configure Hermes
```powershell
hermes config set model.default llama3.1:8b
hermes config set model.provider ollama
hermes config set model.base_url http://localhost:11434/v1
```

---

## GPU Optimization Tips (8GB VRAM)

### Model Selection
| Model | VRAM | Speed | Quality |
|-------|------|-------|---------|
| llama3.1:8b | 4.7GB | Fast | Good |
| mistral:7b | 4.1GB | Fast | Good |
| codellama:13b | 7.4GB | Medium | Great |
| qwen2.5:14b | 8.5GB | Slow | Excellent (tight fit) |

### Quantization
Use Q4_K_M or Q5_K_M quantization for best VRAM/quality balance:
```bash
ollama pull llama3.1:8b-instruct-q4_K_M
```

### Concurrent Usage
- **Don't run** Ollama + Stable Diffusion simultaneously on 8GB
- **Sequential is fine** — use Ollama for text, switch to image gen when needed
- **Hermes + Ollama** = ~6GB VRAM, leaving 2GB for system

### Temperature Settings
```bash
# For coding tasks (deterministic)
hermes config set model.temperature 0.3

# For creative tasks
hermes config set model.temperature 0.7
```

---

## Architecture: Local + VPS Hybrid

```
┌─────────────────────────────┐
│  Jordan's Workstation (Win) │
│  RTX 3070 + 32GB RAM       │
│                             │
│  Hermes Local Profile       │
│  ├── Ollama (llama3.1:8b)  │
│  ├── Telegram Gateway       │
│  └── Local Skills           │
└──────────┬──────────────────┘
           │ Telegram API
           │
┌──────────▼──────────────────┐
│  VPS (Gentech)              │
│                             │
│  Hermes Profiles:           │
│  ├── Gentech (Orchestrator) │
│  ├── YoYo (Strategies)      │
│  ├── DMOB (Labs)            │
│  └── Desmond (Entertainment)│
│                             │
│  Shared Brain: Vault + Git  │
└─────────────────────────────┘
```

### Benefits
- **Local agent** handles GPU-intensive tasks (image gen, local LLM inference)
- **VPS agents** handle coordination, Telegram, cron jobs
- **Shared vault** keeps everyone in sync
- **Faster iteration** — no VPS latency for local development

---

## Quick Start Checklist

- [ ] WSL2 enabled + CUDA installed
- [ ] Hermes installed (`hermes --version`)
- [ ] Ollama installed + model pulled
- [ ] Hermes configured for local model
- [ ] Telegram bot token set
- [ ] Gateway running (`hermes gateway run`)
- [ ] Connected to Gentech groups

---

## Troubleshooting

### GPU not detected in WSL
- Ensure Windows NVIDIA drivers are up to date (not WSL drivers)
- Run `nvidia-smi` inside WSL — if it fails, reinstall CUDA toolkit

### Ollama slow responses
- Check VRAM usage: `nvidia-smi`
- Try smaller model: `ollama pull mistral:7b`
- Increase timeout in Hermes config

### Telegram gateway dies
- Use `hermes gateway install` to run as service
- Check logs: `~/.hermes/logs/gateway.log`

### Token/context issues
- 8GB VRAM limits context to ~4K tokens with 8B models
- Use `hermes config set compression.enabled true` for long sessions

---

*Prepared by Gentech — May 7, 2026*
