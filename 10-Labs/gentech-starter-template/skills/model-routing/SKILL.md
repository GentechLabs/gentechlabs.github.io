# Model Routing Skill

> Task-aware model selection. Use the right model for the right job.
> Auto-switch to GLM-5.2 for audits, deepseek for daily work.

## Routing Rules

| Trigger | Model | Use Case |
|---------|-------|----------|
| `default` | deepseek-v4-flash | Daily work, coding, research |
| `audit`, `security`, `vulnerability` | GLM-5.2 (Z.AI) | Smart contract audits, security review |
| `vision`, `image`, `screenshot` | qwen3-vl:235b-instruct | Image analysis, visual tasks |
| `complex`, `analysis`, `refactor` | GLM-5.2 (Z.AI) | Complex architecture, deep dives |
| Fallback | llama3.1:70b (Ollama Cloud) | When primary models are down |

## Configuration

```yaml
model:
  default: deepseek-v4-flash
  provider: opencode-go
```

For audit tasks, the skill triggers a model switch to Z.AI GLM-5.2.

## Provider Setup

### OpenCode (daily driver)
```
Provider: opencode-go
Model: deepseek-v4-flash
Cost: ~$0.08/M tokens
Free tier: yes, with rate limits
```

### Z.AI (audits)
```
Provider: zai
Model: glm-5.2
Requires: GLM Coding Plan subscription
Key: ZHIPU_API_KEY in .env
```

### Ollama Cloud (backup)
```
Provider: ollama-cloud
Model: llama3.1:70b or qwen3-vl:235b-instruct
Cost: ~$0.50/M tokens (70B), $0.15/M (vision)
Key: OLLAMA_CLOUD_API_KEY in .env
```

## How to trigger

Just use keywords naturally — the skill detects them:

- "audit this contract" → GLM-5.2
- "analyze this image" → qwen3-vl
- "refactor the architecture" → GLM-5.2
- "build a quick tool" → deepseek

No manual switching needed.
