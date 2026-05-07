# Local Compute Node — Edge GPU-Free Workloads

**Concept introduced:** 2026-05-03
**Hardware:** Jordan's home workstation, 32 GB RAM

## The Pattern

Rather than rent cloud GPU for video/voice/AI workloads, run a **local Hermes agent node** on a powerful personal machine. The cloud server schedules jobs; the home machine executes them using its own hardware; results sync back via the shared vault.

## When to Use This

| Workload type | Recommended |
|---------------|-------------|
| Video rendering / processing | ✅ Local (CPU/GPU on home machine) |
| Voice synthesis (TTS) | ✅ Local if model supports CPU (Bark, Parler, Whisper.cpp) |
| Large language model inference (7B–13B) | ✅ Local (GGUF, llama.cpp) |
| 3D scene generation / visualization | ✅ Local (if GPU present) |
| Quick scripts / data fetches | ❌ Use cloud Hermes (simpler) |
| 24/7 scheduled jobs | ❌ Use cloud cron (home machine may sleep/shutdown) |

## Architecture

```
[Cloud Hermes Agent] → (writes task to vault) → [Local Hermes Agent (home PC)]
       ↑                                                  ↓
[Telegram notification]                          (runs heavy model)
                                                    ↓
                                          (writes output to vault)
                                                    ↓
[Cloud Hermes sees result] → notifies Jordan
```

## Setup Requirements

- Hermes installed on local machine (same version as server)
- Vault cloned via HTTPS (GitHub PAT for auth)
- Profile named `local-workstation` with access to heavy tools (ffmpeg, whisper, bark, etc.)
- Network: outbound HTTPS OK, inbound not required (agent pulls work)
- Optional: cron to poll `vault/pending-tasks/` every 5–10 minutes

## Cost Savings Example

| Task | Cloud GPU cost | Local PC cost |
|------|---------------|---------------|
| 1 min voice synthesis (ElevenLabs) | $0.08 | $0 (local TTS) |
| 10 min video transcode | $0.30–1.00 | electricity ~$0.05 |
| 100 LLM inference calls | $0.20–2.00 | $0 (local model) |

**Assumes home PC already owned.** Marginal cost ≈ $0.

## Trade-offs

**Pros:**
- Zero marginal compute cost
- Full control over environment/models
- Privacy: data never leaves your network
- Can use your preferred local models

**Cons:**
- Home machine must be on + connected
- No SLA (if your PC crashes, job stalls)
- Manual setup (one-time)
- Bandwidth limited by home internet upload for large outputs

## Alignment with User Preferences

- **Cost-conscious:** Avoids cloud GPU markup completely
- **Local-first:** Honored as first-class deployment target
- **Flexible:** Can still fall back to cloud if home machine unavailable
- **Scalable:** Add more local nodes (other team members' machines) later

## Next Step (Wednesday Plan)

1. Install Hermes on home PC
2. Clone vault with GitHub PAT
3. Create `local-workstation` profile
4. Test with lightweight job (fetch DeFi price data)
5. Upgrade to video/voice workload
6. Document in vault: `00-HQ/Infrastructure/Local-Workstation-Setup.md`

## Related
- `hermes-agent` skill (spawning local processes)
- Travel agent visualizer (3D map rendering on local GPU)
- AAE Brain layer (local LLM for privacy)
