# GenTech Stateful Production Harness

Borrowed from the **HyCreator spec** (`09-Green Room/specs/hycreator-borrow-2026-08-21.md`).
Makes film continuity STATEFUL so the agent stops re-deriving the 6-part prompt +
locked character + end-state on every clip. Fewer re-rolls, budget saved.

**The human gate stays:** Vanito reviews one clip at a time. This does NOT automate
the whole film — it makes the agent's continuity stateful.

## Usage

```bash
# Start a new production (locked character + style anchor)
python3 harness.py init <name> '{"coating":"anime","seed":42,"palette":"dark-blue-crimson"}' "Makoto Shinkai rain aesthetic"

# Record wallet state (budget guardrail)
python3 harness.py wallet <name> 8.59

# Record an APPROVED clip (sets last_end_state -> feeds next clip's start)
python3 harness.py add <name> <clip> <shot> <end_state> <prompt_used> [url] [cost]

# Record a REJECTED clip (for cut-in / skip decisions)
python3 harness.py reject <name> <clip> <reason> [cost]

# Get the next clip's start state (last approved end_state)
python3 harness.py next <name>

# Human-readable status for the Vanito review loop
python3 harness.py summary <name>
```

## State file (`productions/{name}/state.json`)

```json
{
  "locked_character": {"coating": "anime", "seed": 42, "palette": "dark-blue-crimson"},
  "style_anchor": "Makoto Shinkai rain aesthetic",
  "sequence": [{"clip": "1a", "shot": "Wide", "end_state": "...", "prompt_used": "...", "url": "...", "cost": 3.19}],
  "last_end_state": "feeds next clip's start",
  "rejected": [{"clip": "1c", "reason": "guitar morphed into blade", "cost": 2.55}],
  "wallet_state": {"balance": 8.59, "currency": "USDC"}
}
```

## Rules
- One production = one folder under `productions/`.
- `add` always overwrites `last_end_state` with the new clip's end_state.
- `reject` records failures for cut-in/skip decisions — never silently drops a clip.
- Wire into `seedance-cinematic-film-workflow` on the next Vanito film.
