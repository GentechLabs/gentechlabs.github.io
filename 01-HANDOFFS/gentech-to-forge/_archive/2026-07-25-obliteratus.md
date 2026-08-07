# 🧹 Obliteratus — Unrestricted Local Models for Forge

**Goal:** Install + run Obliteratus on desktop (RTX 3070 8GB, 32GB RAM) to abliterate local models — no more AI refusals blocking travel planning, project research, or any other task.

**By when:** ASAP — this unlocks Forge's full potential locally.

---

## Why This Matters

You know when you ask an AI "find me a cheap condo in Lapu-Lapu with a jacuzzi inside the room" or "how do I do X thing" and it refuses or gives a politically safe non-answer? Obliteratus fixes that. It surgically removes the refusal/censorship weights from open-source models — no fine-tuning, no retraining.

Running it locally on your RTX 3070 means **nobody else's rules apply.** You get genuinely helpful answers.

## What Your Hardware Can Handle

| Model | Size | VRAM (4-bit) | Quality |
|-------|------|-------------|---------|
| **Llama 3.1 8B** | 8B params | ~7GB | ✅ Best all-rounder |
| **Mistral 7B** | 7B params | ~6GB | ✅ Fast, competent |
| **Qwen 2.5 7B** | 7B params | ~7GB | ✅ Strong reasoning |
| **Gemma 2 9B** | 9B params | ~8GB (tight) | ⚠️ Good but tight on VRAM |

**Recommended start:** Llama 3.1 8B with `--method advanced --quantization 4bit`

## Step 1 — Install Obliteratus

```bash
# Clone the repo
git clone https://github.com/elder-plinius/OBLITERATUS.git
cd OBLITERATUS

# Install (this pulls PyTorch + Transformers + bitsandbytes ~5-10GB)
pip install -e .
```

## Step 2 — Check What Models Are Available

```bash
# Browse by compute tier
obliteratus models --tier medium

# Get recommendation for your chosen model
obliteratus recommend meta-llama/Llama-3.1-8B-Instruct
```

## Step 3 — Run Abliteration

```bash
# Default: removes refusals from Llama 3.1 8B
obliteratus obliterate meta-llama/Llama-3.1-8B-Instruct \
  --method advanced \
  --quantization 4bit \
  --output-dir D:/Forge/Models/abliterated/llama-3.1-8b
```

**Expected time:** ~15-30 min on an RTX 3070.

## Step 4 — Verify It Worked

```bash
# Test the abliterated model
python3 -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('D:/Forge/Models/abliterated/llama-3.1-8b')
tokenizer = AutoTokenizer.from_pretrained('D:/Forge/Models/abliterated/llama-3.1-8b')
inputs = tokenizer('How do I find cheap condos in Cebu with a private pool?', return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

**Pass criteria:** The model gives a helpful, detailed answer instead of "I can't help with that" or a refusal.

## Verification Metrics

| Metric | Target | Check |
|--------|--------|-------|
| Refusal rate | < 5% | Run 20 test prompts |
| Perplexity change | < 10% | Built-in comparison |
| Coherence | Feels natural | Read the output |

## Troubleshooting

**Out of memory:** Lower to 4-bit if you didn't already. If still tight, try Mistral 7B instead.
**Refusals persist:** Increase `--n-directions 8` or try `--method aggressive`
**Coherence damaged:** Reduce `--n-directions` to 2, increase `--regularization` to 0.3

## Quick Reference

```bash
obliteratus models --tier medium   # Browse models
obliteratus recommend <model>      # Get method recommendations
obliteratus info <model>           # Model architecture details
obliteratus obliterate <model>     # Main command
obliteratus tourney <model>        # All methods head-to-head
obliteratus ui                     # Web UI (Gradio)
```

---

**After Obliteratus is running on desktop, update `from-the-forge.md` with which model you abliterated and the results.**
