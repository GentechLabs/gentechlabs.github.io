# Hermes Config Hierarchy

## Layer Diagram

```
Brain Repo Template (source of truth)
  └─→ Live Global Config (fallback defaults)
       └─→ Live Profile Config (per-agent override)
            └─→ Vault Backup (disaster recovery copy)
```

## Exact Paths

| Layer | Path | Used When |
|-------|------|-----------|
| Brain repo | `/root/repos/hermes-brain/config.yaml` | New deploys, restores from backup |
| Live global | `~/.hermes/config.yaml` | Profile doesn't override a key |
| Live profile | `~/.hermes/profiles/{agent}/config.yaml` | Agent is running (this is what executes) |
| Vault backup | `/root/vaults/gentech/00-System/agent-profiles/{agent}/config.yaml` | Disaster recovery, config archaeology |

## Key Sections

```yaml
# Main model config
model:
  provider: openrouter          # or nous, custom, xiaomi, etc.
  model: stepfun/step-3.5-flash # the LLM for text responses
  base_url: ''
  api_key: ''

# Vision (image analysis)
auxiliary:
  vision:
    provider: openrouter
    model: google/gemini-2.0-flash-001
    base_url: ''
    api_key: ''
  web_extract:
    provider: auto
    model: ''
  compression:
    provider: auto
    model: ''
```

## Audit One-Liner

```bash
for f in /root/repos/hermes-brain/config.yaml /root/.hermes/config.yaml \
  /root/.hermes/profiles/*/config.yaml \
  /root/vaults/gentech/00-System/agent-profiles/*/config.yaml; do
  echo "=== $(echo $f | sed 's|.*/hermes/|hermes/|; s|.*/brain/|brain/|; s|.*/profiles/|profiles/|; s|.*/agent-profiles/|vault:/|') ==="
  grep -A 4 "auxiliary:" "$f" | head -5
done
```

## Common Drift Scenarios

1. **Brain repo still has old provider** → next deploy overwrites all profiles
2. **Vault backup not updated** → restore from backup reintroduces stale config
3. **Stale base_url** → leftover from provider migration, forces custom endpoint routing
4. **Missing model field** → provider auto-detection may pick wrong model (e.g., Nous picks gemini-3-flash-preview which doesn't work on OpenRouter)

## Provider-Specific Notes

| Provider | base_url | api_key | Notes |
|----------|----------|---------|-------|
| `openrouter` | blank (uses pool) | blank (uses pool) | Credential pool in auth.json |
| `nous` | blank | blank | OAuth via portal, auto-selects vision model |
| `custom` | REQUIRED | REQUIRED | Must also have `custom_providers` section |
| `xiaomi` | REQUIRED | REQUIRED | Uses Xiaomi API endpoint |
| `ollama-cloud` | blank | blank | Uses OLLAMA_API_KEY env var |
