#!/usr/bin/env bash
# Fed / regulator watch — what was SAID, not just when.
# Closes the SPEECH layer: the Federal Register carries documents weeks after the remark,
# and never carries the press conference, the minutes, or the speeches around a decision.
# Silence doctrine: prints nothing when nothing relevant is new.
exec python3 /root/.hermes/profiles/gentech-treasury/scripts/fed-watch.py "$@"
