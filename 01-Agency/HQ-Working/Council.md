# Council — Installed 2026-04-16

Adversarial multi-perspective council MCP server for hermes-agent.

## What It Does
Five personas from distinct intellectual traditions debate questions through structured adversarial deliberation, producing calibrated verdicts with confidence scores, evidence links, and DPO preference pairs for RL training.

## Tools
- `council_query` — Full 5-persona adversarial deliberation
- `council_evaluate` — Evaluate content quality through critique
- `council_gate` — Quick safety review (Skeptic + Oracle + Arbiter)

## Config
- Added to Hermes MCP servers as `council`
- Command: `hermes-council-server`
- Env vars (set as needed): `COUNCIL_API_KEY`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY`
- Default model: `nousresearch/hermes-3-llama-3.1-70b`

## Notes
- Requires API key to function (OpenRouter, Nous, or OpenAI)
- Source: `/tmp/hermes-council/`
- Installed in Hermes venv
