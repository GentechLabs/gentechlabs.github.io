---
title: "RunPod GPU Cloud Setup"
date: 2026-04-28
type: setup
tags: [gpu, cloud, runpod, video-agent, infrastructure]
---

# RunPod Pay-As-You-Go Setup

## Account
- **Provider:** RunPod (https://runpod.io)
- **Model:** Pay-as-you-go, no commitment
- **Storage:** Persistent volume at $0.07/GB/mo

## Recommended Instance Types

### For VideoAgent (8GB+ VRAM needed)
| Use Case | GPU | VRAM | $/hr | Why |
|----------|-----|------|------|-----|
| **Dev/Test** | RTX A5000 | 24GB | $0.27 | Cheapest 24GB option |
| **Full Pipeline** | L4 | 24GB | $0.39 | Better perf, still cheap |
| **Heavy Workloads** | RTX 4090 | 24GB | $0.69 | Fastest consumer GPU |
| **Big Models** | A40 | 48GB | $0.44 | 48GB for large models |

### Cost Estimates
| Scenario | GPU | Hours | Cost |
|----------|-----|-------|------|
| Quick test | A5000 | 1hr | $0.27 |
| Dev session (4hr) | A5000 | 4hr | $1.08 |
| Full pipeline run | L4 | 2hr | $0.78 |
| Hackathon sprint (8hr/day × 5 days) | L4 | 40hr | $15.60 |

## Setup Workflow

### 1. Create Account
```
https://runpod.io → Sign Up → Add Credits
```

### 2. Launch Instance
```bash
# Via web UI:
# 1. Go to Pods → Deploy
# 2. Select GPU (RTX A5000 for dev, L4 for prod)
# 3. Choose template: "RunPod PyTorch 2.3" or "CUDA 12.1"
# 4. Set disk size: 50GB (models are ~10GB, leave room)
# 5. Deploy → Wait for instance to start
# 6. Connect via SSH or Jupyter
```

### 3. Connect via SSH
```bash
# RunPod provides SSH command like:
ssh root@<instance-ip> -p <port> -i ~/.ssh/runpod_key

# Or use their CLI:
pip install runpod
runpod pods list
runpod pods ssh <pod-id>
```

### 4. Setup VideoAgent on GPU Instance
```bash
# Once connected:
git clone https://github.com/HKUDS/VideoAgent.git
cd VideoAgent

# Install conda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b
source ~/miniconda3/etc/profile.d/conda.sh

# Create environment
conda create --name videoagent python=3.10 -y
conda activate videoagent
conda install -y -c conda-forge pynini==2.1.5 ffmpeg
pip install -r requirements.txt

# Download models (selective - start with what you need)
cd tools
huggingface-cli download openai/whisper-large-v3-turbo --local-dir whisper-large-v3-turbo
# Add more models as needed
```

### 5. Persistent Storage
```bash
# Create a persistent volume for models (avoids re-downloading)
# RunPod UI: Storage → New Volume
# Mount at /workspace

# Models persist across pod restarts
# Cost: $0.07/GB/mo (~$0.70/mo for 10GB of models)
```

## Cost Optimization Tips

1. **Use spot instances** — RunPod community cloud is cheaper
2. **Stop when idle** — Pause pod when not actively using
3. **Persistent storage** — Don't re-download models each time
4. **Start small** — RTX A5000 ($0.27/hr) for dev, scale up only when needed
5. **Batch work** — Queue tasks, run them in one session

## Emergency Shutdown
```bash
# Always stop your pod when done!
# RunPod UI: Pods → Stop/Pause
# Or CLI:
runpod pods stop <pod-id>
```

## Integration with Hostinger
- **Hostinger:** Main server, Telegram bot, vault sync
- **RunPod:** GPU workloads only (VideoAgent, model inference)
- **Data flow:** Hostinger sends tasks → RunPod processes → returns results
