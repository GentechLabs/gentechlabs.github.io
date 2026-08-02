# AirLLM — Big Model Inference on Consumer GPUs

**Source:** [lyogavin/airllm](https://github.com/lyogavin/airllm)
**Date:** 2026-08-01
**Author:** Gavin Li (lyogavin)
**Tags:** #llm #inference #moe #self-hosting #kimi-k3 #deepseek

---

## TL;DR
Layer-by-layer (and per-expert, for MoE) streaming inference that lets huge LLMs run on tiny VRAM — 70B on 4GB, DeepSeek-V3 671B on ~12GB, Kimi K3 2.8T on 3.72GB. Apache 2.0, 24.5k⭐, actively maintained (v3.0 Jun 2026, Kimi K3 Jul 2026). Tradeoff: disk/bandwidth-bound → slower than native inference. Not for high-throughput serving.

---

## Key Sections

### How it works
- Loads ONE transformer layer at a time from disk → GPU → compute → next layer
- MoE models (DeepSeek-V3, Kimi K3): streams only the experts a token routes to
- No quantization required by default; 4bit/8bit block-wise quantization optional (3x speedup)
- CPU inference supported (v2.10.1+), Apple Silicon via mlx

### Capability numbers (from README, Jul 2026)
| Model | Size | VRAM needed |
|---|---|---|
| Llama 3.1 | 405B | ~8GB |
| DeepSeek-V3 | 671B | ~12GB (FP8) |
| Qwen3 | 235B-A22B | ~3GB |
| Kimi K3 | 2.8T | 3.72GB |

### Features
- `pip install airllm`, single `AutoModel.from_pretrained(...)` line
- Model compression (block-wise quantization) — 3x inference speedup
- Prefetching to overlap loading + compute (~10% faster)
- `delete_original` to halve disk usage
- Supports Llama, Qwen, DeepSeek, Phi-4, Gemma, ChatGLM, Baichuan, Mistral, InternLM, Mixtral

## GenTech Relevance
- **Provider leverage play**: if we ever rent/own a GPU box (even a single RTX 4090-class), AirLLM lets us self-host DeepSeek-V3-class models and expose them as an x402-gated API — a monetizable endpoint with no per-token vendor margin. Directly relevant to Jordan's provider evaluation (Zyloo, Ollama Cloud) as a "self-host vs rent tokens" data point.
- **Kimi K3 thread**: we track K3 (2.8T MoE, 1M ctx) in the arcade thesis. AirLLM is one of the few practical ways to run it on consumer hardware.
- **NOT actionable on current VPS**: no GPU, 15GB RAM, 4 cores, 45GB free disk. CPU inference exists but is painfully slow above ~7B. Disk streaming 70B+ on this box = hours per response.

## Verdict: **Watch**
Interesting for the next hardware decision; a real build candidate only if we get GPU capacity. No action needed on current infra.

## Open Questions
- Real-world tokens/sec for DeepSeek-V3 on a single 4090-class card via AirLLM?
- Does v3.0 FP8 path require CUDA 12 build of torch (README says yes for K3)?
- HF disk cache requirement — how much disk for sharded 671B?

## Sources
- https://github.com/lyogavin/airllm
- https://pypi.org/project/airllm/
