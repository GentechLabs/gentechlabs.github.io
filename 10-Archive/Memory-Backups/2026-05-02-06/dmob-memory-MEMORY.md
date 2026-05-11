User prefers concise, direct responses for tooling/configuration queries. Avoid repetitive or redundant explanations unless explicitly asked for clarification. When multiple agents respond to the same query, coordinate to ensure only one response is delivered to the user to avoid duplication.
§
Mess Hall (11-Mess Hall/) reorganized Apr 27, 2026: README.md, task-board.md, agent-coordination-board.md, handoff-board.md, daily/, archive/, 2026/ (weekly folders). Empty weeks W02-W15 removed.
§
Colosseum Copilot: `~/.hermes/scripts/colosseum-config.json` (ProtoJay4789, id:98610). Frontier: 12d, $230K+. Brother's wedding May 23. Private screenshots stay HQ-only.
§
Travel folder convention: `00-HQ/Travel/` in gentech vault. Each country gets its own folder (e.g., `00-HQ/Travel/Philippines/`). When planning a new trip, create country folder if it doesn't exist, add trip doc + flights.md. Consolidate duplicates — keep one main trip doc per trip.
§
AAE monitor loads runtime config from `.lfj-aae-config.json` (in `~/.hermes/scripts/`), not just from the hardcoded DEFAULT_CONFIG in the Python script. To update position balance, must edit BOTH the vault Python script AND the runtime JSON config file. The JSON config is what the script actually reads.
§
LFJ V2.2 AVAX/USDC LP: Pool 0x864d, Range $9.00–$9.45 (Curve, rebalanced Apr 29). Wallet: [REDACTED_WALLET]. Script: lp-position-reader.py. Cron: 67e1969f9b2b.
§
Workflow: When Jordan sends screenshots/images in HQ that contain sensitive info (emails, docs, etc.), DMOB should redact PII/account details and produce a clean text summary for sharing in other channels (Labs, Mess Hall, etc.). Raw images with sensitive content stay in HQ only.
§
AAE Hybrid Strategy Brain approved: 3 units — Analyst (eyes, Beam Cloud), Brain (decisions, Beam Cloud), Validator+Executor (safety+execution, GenLayer+Solana native). Progression: Shadow→Supervised→Autonomous. Doc: 02-AAE/Hybrid-Strategy-Brain-Architecture.md
§
Collaborator's name is Vanito (not Veneto).
§
Jordan plans to update Hermes Agent to v0.12.0 and test local models (Ollama + LM Studio) tonight. Postpone portfolio updates until tomorrow.