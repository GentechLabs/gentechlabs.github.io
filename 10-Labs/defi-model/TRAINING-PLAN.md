# DeFi Model — Training Plan (locked Aug 21 2026)

**Status:** LOWER PRIORITY — next month
**Owner:** Steward / DeFi intelligence

## The idea (Jordan)
Train the DeFi model on the **agentic treasury's real decision data** — the
decision journal (what + why) the treasury generates as it runs autonomously.
This is the flywheel: more autonomy = more real training data = smarter model.

## Cost check (confirmed — does NOT change price)
- Method: QLoRA on DeepSeek R1 Distill 32B, single A10G GPU, ~1hr on Modal.
- Cost driven by **model size + training steps**, NOT data source.
- Real treasury decisions vs synthetic pairs = same model, same GPU, same ~$1.
- Corpus size scales cost only marginally (a few hundred pairs = a few dollars).
- **Verdict: stays cheap. No price change from using treasury data.**

## What's already built
- `10-Labs/defi-model/` — finetune.py, run-modal.py, generate-synthetic-data.py
- `journal-to-training.py` — converts decision journal → Alpaca training format
- `training-data/decision-training.jsonl` — real decisions accumulating
- Decision journal (`steward-decisions.jsonl`) — the source, grows autonomously

## Next month trigger
- When the decision corpus hits ~200 real pairs, run the fine-tune.
- Target: the model learns the Steward's reasoning (regime → mode → action → why).

## Priority
- LOWER — the flywheel runs itself; no urgent action needed. Revisit next month.
