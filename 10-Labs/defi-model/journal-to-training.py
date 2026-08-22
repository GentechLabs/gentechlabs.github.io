#!/usr/bin/env python3
"""
D5 DeFi Model — Decision Journal → Training Data Bridge (Aug 21 2026)

The Steward's decision journal (steward-decisions.jsonl) is REAL, grounded
decision data: every autonomous action the treasury takes, with its rationale
(the "why" — regime, narrative, data). This is exactly the training signal the
D5 DeFi model was missing (the old corpus was 26 synthetic/vault pairs).

This script converts journal entries into the same Alpaca instruction/output
format the existing finetune.py consumes, so the corpus grows with real
decisions as the treasury runs autonomously.

Output: appends to defi-model/training-data/decision-training.jsonl
        (Alpaca format: {instruction, input, output, type})
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

JOURNAL = os.environ.get(
    "STEWARD_DECISIONS_FILE",
    "/root/ProtoJay4789.github.io/10-Labs/agent-kit-self-tracking/steward-decisions.jsonl")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "training-data", "decision-training.jsonl")

# Map journal action -> a natural-language instruction the model can learn from.
_INSTRUCTION = {
    "MODE_HOLD": "Given the current regime and deployed capital, what mode should the treasury be in and why?",
    "MODE_CHANGE": "The regime has shifted. What mode should the treasury switch to and what is the reasoning?",
    "REBALANCE": "The LP position is out of range. Should the treasury re-center it, and how wide should the new curve be?",
    "DEPLOY": "The treasury has deployable capital and no position. How should it deploy, and why?",
    "WITHDRAW": "The treasury needs to exit the position. What is the reasoning and how should it be done?",
    "CLOSE": "A position should be closed. What is the rationale?",
    "HOLD": "A trade signal fired but the treasury is not in trade mode. What should happen and why?",
    "ENTER": "A trade opportunity is present. Should the treasury enter, and why?",
}


def _to_alpaca(entry: dict) -> dict:
    action = entry.get("action", "ACTION").upper()
    instruction = _INSTRUCTION.get(action, f"Given this treasury situation, what should be done and why? ({action})")
    # Build a compact input: the data + regime context the decision was based on.
    data = entry.get("data") or entry.get("detail") or {}
    if isinstance(data, dict):
        data_str = json.dumps(data)
    else:
        data_str = str(data)
    input_ctx = f"Regime/context: {data_str}"
    output = entry.get("rationale") or entry.get("why") or ""
    return {
        "instruction": instruction,
        "input": input_ctx,
        "output": output,
        "type": "decision",
        "source": "steward-journal",
        "ts": entry.get("ts", ""),
    }


def main() -> int:
    try:
        with open(JOURNAL) as f:
            entries = [json.loads(l) for l in f if l.strip()]
    except FileNotFoundError:
        print("no journal yet — nothing to convert")
        return 0
    except Exception as e:
        print(f"journal read error: {e}", file=sys.stderr)
        return 1

    if not entries:
        print("journal empty")
        return 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # Load existing converted entries to avoid duplicates (by ts).
    seen = set()
    try:
        with open(OUT) as f:
            for line in f:
                if line.strip():
                    seen.add(json.loads(line).get("ts", ""))
    except FileNotFoundError:
        pass

    added = 0
    with open(OUT, "a") as f:
        for e in entries:
            ts = e.get("ts", "")
            if ts in seen:
                continue
            f.write(json.dumps(_to_alpaca(e)) + "\n")
            seen.add(ts)
            added += 1

    print(f"converted {added} new decision(s) -> {OUT} (total {len(seen)})")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
