#!/usr/bin/env python3
"""
GenTech Stateful Production Harness (borrowed from HyCreator spec, 2026-08-21)

Per-production state file that the film agent writes + reads on every clip, so
continuity is STATEFUL instead of re-deriving the 6-part prompt + locked
character + end-state on every call. Fewer re-rolls, budget saved.

The human gate stays: Vanito reviews one clip at a time. This harness does NOT
automate the whole film — it makes the agent's continuity stateful.

State file layout (productions/{name}/state.json):
  locked_character  {coating, seed, palette, refs}
  style_anchor      single director/anime anchor
  sequence          [{clip, shot, end_state, prompt_used, url, cost}]
  last_end_state    feeds next clip's start
  rejected          [{clip, reason, cost}]
  wallet_state      {balance, currency, budget_guardrail}
"""

import json
import os
import sys
from datetime import datetime

# The harness lives inside the productions/ folder, so the root IS this dir.
PRODUCTIONS_ROOT = os.path.dirname(os.path.abspath(__file__))


def _state_path(name):
    return os.path.join(PRODUCTIONS_ROOT, name, "state.json")


def _default_state():
    return {
        "production": "",
        "created": "",
        "updated": "",
        "locked_character": {},
        "style_anchor": "",
        "sequence": [],
        "last_end_state": "",
        "rejected": [],
        "wallet_state": {},
    }


def init(name, locked_character=None, style_anchor="", wallet_state=None):
    """Create a new production state file. Fails if it already exists."""
    path = _state_path(name)
    if os.path.exists(path):
        raise FileExistsError(f"Production '{name}' already exists: {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    state = _default_state()
    state["production"] = name
    state["created"] = datetime.utcnow().isoformat() + "Z"
    state["updated"] = state["created"]
    if locked_character:
        state["locked_character"] = locked_character
    state["style_anchor"] = style_anchor
    if wallet_state:
        state["wallet_state"] = wallet_state
    _write(name, state)
    return state


def load(name):
    """Load a production's state. Raises if not initialized."""
    path = _state_path(name)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Production '{name}' not initialized. Run init() first."
        )
    with open(path) as f:
        return json.load(f)


def _write(name, state):
    state["updated"] = datetime.utcnow().isoformat() + "Z"
    path = _state_path(name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    return path


def add_clip(name, clip, shot, end_state, prompt_used, url="", cost=0.0):
    """Record an APPROVED clip. Sets last_end_state to this clip's end_state."""
    state = load(name)
    state["sequence"].append(
        {
            "clip": clip,
            "shot": shot,
            "end_state": end_state,
            "prompt_used": prompt_used,
            "url": url,
            "cost": cost,
            "approved_at": datetime.utcnow().isoformat() + "Z",
        }
    )
    state["last_end_state"] = end_state
    _write(name, state)
    return state


def reject_clip(name, clip, reason, cost=0.0):
    """Record a REJECTED clip (for cut-in / skip decisions)."""
    state = load(name)
    state["rejected"].append(
        {
            "clip": clip,
            "reason": reason,
            "cost": cost,
            "rejected_at": datetime.utcnow().isoformat() + "Z",
        }
    )
    _write(name, state)
    return state


def next_start_state(name):
    """Return the end_state of the last approved clip (feeds next clip's start)."""
    state = load(name)
    return state.get("last_end_state", "")


def set_wallet(name, balance, currency="USDC", budget_guardrail=None):
    state = load(name)
    state["wallet_state"] = {
        "balance": balance,
        "currency": currency,
        "budget_guardrail": budget_guardrail,
        "updated": datetime.utcnow().isoformat() + "Z",
    }
    _write(name, state)
    return state


def summary(name):
    """Human-readable status for the Vanito review loop."""
    state = load(name)
    seq = state["sequence"]
    rej = state["rejected"]
    total_cost = sum(c.get("cost", 0) for c in seq) + sum(
        c.get("cost", 0) for c in rej
    )
    lines = [
        f"🎬 Production: {name}",
        f"   Style anchor: {state.get('style_anchor') or '(none)'}",
        f"   Approved clips: {len(seq)}",
        f"   Rejected clips: {len(rej)}",
        f"   Total spend: ${total_cost:.2f}",
        f"   Wallet: {state.get('wallet_state', {}).get('balance', 'n/a')} "
        f"{state.get('wallet_state', {}).get('currency', '')}",
        f"   Next clip starts from: {state.get('last_end_state') or '(none yet)'}",
    ]
    if seq:
        lines.append("   Sequence:")
        for c in seq:
            lines.append(
                f"     - {c['clip']} ({c['shot']}) — ${c.get('cost', 0):.2f}"
            )
    if rej:
        lines.append("   Rejected:")
        for c in rej:
            lines.append(f"     - {c['clip']}: {c['reason']} (${c.get('cost', 0):.2f})")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: harness.py <init|summary|add|reject|next|wallet> ...")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "init":
        name = sys.argv[2]
        state = init(name)
        print(f"Initialized {name} -> {_state_path(name)}")
    elif cmd == "summary":
        print(summary(sys.argv[2]))
    elif cmd == "add":
        # add <name> <clip> <shot> <end_state> <prompt_used> [url] [cost]
        name, clip, shot, end_state, prompt_used = sys.argv[2:7]
        url = sys.argv[7] if len(sys.argv) > 7 else ""
        cost = float(sys.argv[8]) if len(sys.argv) > 8 else 0.0
        add_clip(name, clip, shot, end_state, prompt_used, url, cost)
        print(f"Added approved clip '{clip}' to {name}")
    elif cmd == "reject":
        name, clip, reason = sys.argv[2:5]
        cost = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
        reject_clip(name, clip, reason, cost)
        print(f"Recorded rejection of '{clip}' in {name}")
    elif cmd == "next":
        print(next_start_state(sys.argv[2]))
    elif cmd == "wallet":
        name, balance = sys.argv[2], float(sys.argv[3])
        set_wallet(name, balance)
        print(f"Set wallet for {name} to {balance}")
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
