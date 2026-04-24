---
name: multi-agent-model-stacking
description: Strategy for assigning specialized LLM models to different agents within a multi-agent organization to optimize for domain-specific performance (Logic vs. Strategy vs. Creativity).
---

# Multi-Agent Model Stacking

When operating a multi-agent team (e.g., GenTech), using a single "generalist" model for all agents creates a performance ceiling. "Model Stacking" assigns specific model architectures to agents based on their operational domain.

## 🧠 The Specialization Map

| Agent Role | Recommended Model Class | Primary Requirement | Key Metrics |
| :--- | :--- | :--- | :--- |
| **The Engineer (Labs/Dev)** | Coding-Specialized (Gemma 4, DeepSeek, Codestral) | Syntax Precision | Zero syntax hallucinations, strict logic adherence. |
| **The Strategist (Growth/Econ)** | Large Parameter (Llama 3.1 70B+, Mistral Large) | Knowledge Breadth | High-capacity reasoning, complex synthesis, "big picture" mapping. |
| **The Creative (Content/Brand)** | Narrative-Optimized (Kimi, Mistral, Gemma-small) | Fluidity & Vibe | Prose quality, articulation, associative thinking. |
| **The Lead (HQ/Router)** | Balanced Generalist (Gemma 4, Llama 3) | Stability & Coordination | Reliability in routing, concise summarization, tool-use stability. |

## 🛠️ Implementation Workflow

1. **Audit Domain Needs**: Identify if the agent's primary output is code (Logic), analysis (Reasoning), or content (Creativity).
2. **Model Mapping**: Match the domain to the model class above.
3. **Profile Configuration**: 
    - Update `config.yaml` or `.env` for each agent profile.
    - Set `model.default` specifically for that agent's role.
4. **Verification**: 
    - **Logic**: Run a complex code test (e.g., a smart contract audit).
    - **Strategy**: Ask for a synthesis of 3+ disparate data points.
    - **Creativity**: Generate 3 variations of a brand hook.

## ⚠️ Pitfalls & Warnings
- **The "Lazy" Effect**: Large models can sometimes become "lazy" (over-summarizing). Use specific system prompts to enforce depth in Strategic roles.
- **Tool-Use Divergence**: Some models are better at tool-calling than others. Always verify that the chosen model can execute `execute_code` and `terminal` commands without failing.
- **Latency Trade-offs**: 70B+ models are slower. Use them for "deep work" and smaller models for "reactive chat."

#brainmap #model-stacking #agent-optimization