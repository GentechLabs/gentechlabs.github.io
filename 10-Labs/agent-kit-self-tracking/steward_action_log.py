#!/usr/bin/env python3
"""steward_action_log.py — WHAT THE TREASURY DID, AND WHO DECIDED IT.

WHY THIS EXISTS (2026-09-30). On this night the engine rebuilt the book at 4am from a stale label
and moved money with NO action log. We reconstructed what happened only by reading the chain, tx by
tx. A treasury that cannot say what it did is not auditable -- and we proved that on ourselves.

Jordan's frame for this build (borrow-the-mechanism, from Robinhood's agent launch): "eat the meat
and spit out the bones." Robinhood did not ship agents; they shipped a DOOR for agents, and the
"meat" they chose to lead with was a real-time activity feed as the proof of safety. We already keep
value-over-time ledgers (steward_fee_ledger, value_timeline, wallet_timeline). We keep NO actions.
That is the gap this closes.

APPEND-ONLY. One JSON object per line, never rewritten. JSON Lines.
    .steward-action-log.jsonl

TWO WRITES PER ACTION, and this is deliberate:
  log_intent()  -- written BEFORE the result is known. The honest record of what we set out to do.
  log_result()  -- written after, carrying the receipt, linked by the same `id`.
A log written only on success is a marketing document. A log written only on intent is a wish.

FAIL-SOFT, ALWAYS. Every entry point swallows its own exceptions and returns None. This module must
never be the reason a money path fails -- if the log cannot be written, the trade still happens and
the failure is echoed to stderr.

READ IT:
    python3 steward_action_log.py                 # last 20 events, human-readable
    python3 steward_action_log.py --gaps          # actions with an intent but NO result (crashed?)
    python3 steward_action_log.py --decided-by machine
"""
from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.environ.get("STEWARD_ACTION_LOG") or os.path.join(HERE, ".steward-action-log.jsonl")

# The five fields that make this an audit rather than a diary (spec §2).
MANDATORY = ("ts", "id", "actor", "verb", "decided_by")

VALID_DECIDED_BY = ("operator", "machine", "escalated", "unknown")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write(rec: dict) -> str | None:
    """Append one event. Fail-soft: never raises, never blocks a money path."""
    try:
        line = json.dumps(rec, separators=(",", ":"), default=str)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        return rec["id"]
    except Exception as exc:  # noqa: BLE001 -- deliberately broad: logging must never break a trade
        sys.stderr.write(f"action_log: WRITE FAILED ({exc}) -- action continues unlogged\n")
        return None


def log_intent(actor, verb, *, reason=None, before=None, chain=None, venue=None,
               decided_by="unknown", provenance=None, **extra) -> str:
    """Record that an action is STARTING, before the outcome is known. Returns the event id."""
    if decided_by not in VALID_DECIDED_BY:
        decided_by = "unknown"
    rec = {
        "ts": _now(), "id": uuid.uuid4().hex[:12], "phase": "intent",
        "actor": actor, "verb": verb, "decided_by": decided_by,
        "reason": reason, "chain": chain, "venue": venue,
        "before": before, "provenance": provenance, "status": "started",
    }
    rec.update(extra)
    return _write(rec) or ""


def log_result(event_id, status="ok", *, final=None, after=None, txs=None, error=None,
               **extra) -> str | None:
    """Record the OUTCOME of an action, linked to its intent by `event_id`.

    The result INHERITS actor/verb/decided_by from its intent. This is not decoration: a result line
    that carries only an id is invisible to every useful query -- `--decided-by machine` would return
    the intents and silently drop every outcome, which is precisely the shape of bug this whole log
    exists to prevent. Every line must be readable on its own AND filterable in the same way.

    `final` -- AUDIT FINDING (kimi-k2.7-code, 2026-09-30): the shell derived status from the exit
    code, so a `timeout` that killed the engine AFTER it had broadcast a transaction wrote
    status="failed" -- and gaps() treated ANY result as closing the intent, reporting zero
    outstanding work while a transaction was still settling. A timeout reaches no verdict, so it
    must NOT be final. Default True keeps other writers working; the shell passes final=False on
    RC 124 (timeout) explicitly, so the honest case is stated rather than inferred.
    """
    if final is None:
        final = True
    rec = {
        "ts": _now(), "id": event_id or uuid.uuid4().hex[:12], "phase": "result",
        "status": status, "final": bool(final), "after": after,
        "txs": txs or [], "error": error,
    }
    for prior in read_events():
        if prior.get("id") == event_id and prior.get("phase") == "intent":
            for k in ("actor", "verb", "decided_by", "chain", "venue", "provenance", "reason"):
                if prior.get(k) is not None:
                    rec.setdefault(k, prior[k])
            break
    rec.update(extra)
    return _write(rec)


def log_event(actor, verb, *, status="ok", **kw) -> str | None:
    """Convenience: a single-line event for things with no meaningful duration."""
    eid = log_intent(actor, verb, **{k: v for k, v in kw.items()
                                     if k in ("reason", "before", "chain", "venue",
                                              "decided_by", "provenance")})
    return log_result(eid, status, after=kw.get("after"), txs=kw.get("txs"))


def read_events(limit=None, **filters):
    """Read the log, oldest first. Filters match any top-level field exactly."""
    if not os.path.exists(LOG_PATH):
        return []
    out = []
    try:
        with open(LOG_PATH, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if all(rec.get(k) == v for k, v in filters.items()):
                    out.append(rec)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"action_log: READ FAILED ({exc})\n")
        return []
    return out[-limit:] if limit else out


def gaps():
    """Intents with no matching result -- the actions that started and never finished.

    This is the single most valuable query in the file: it is the difference between "the treasury
    is idle" and "the treasury tried something and died mid-action".

    AUDIT FINDING (kimi-k2.7-code, 2026-09-30): only a FINAL result closes an intent. A timeout
    writes a result line but reaches no verdict, so its transaction may still be settling -- that is
    exactly the state this query exists to surface, and counting it as closed was a false negative
    living inside the log built to prevent false negatives. A missing `final` (older lines, other
    writers) reads as final, so existing history is not retro-changed.
    """
    intents, closed = {}, set()
    for rec in read_events():
        if rec.get("phase") == "intent":
            intents[rec.get("id")] = rec
        elif rec.get("phase") == "result":
            if rec.get("final", True):
                closed.add(rec.get("id"))
    return [r for i, r in intents.items() if i not in closed]


def _cli_log_intent(args) -> int:
    """log-intent --actor X --verb Y [--decided-by machine] [--reason ...] [--provenance ...]
    Prints the event id on stdout so the caller can pass it to log-result. Fail-soft: an empty
    stdout means the log did not accept the event, and the caller must NOT treat that as fatal."""
    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args else default
    eid = log_intent(
        opt("--actor", "unknown"), opt("--verb", "unknown"),
        reason=opt("--reason"), decided_by=opt("--decided-by", "machine"),
        provenance=opt("--provenance"), before=None,
        chain=opt("--chain"), venue=opt("--venue"),
    )
    print(eid)
    return 0


def _cli_log_result(args) -> int:
    """log-result --id EID --status ok|failed [--final 0|1] [--tx 0x... ]... [--error ...]"""
    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args else default
    final = None
    if "--final" in args:
        final = args[args.index("--final") + 1] not in ("0", "false", "no")
    txs = []
    for i, a in enumerate(args):
        if a == "--tx" and i + 1 < len(args):
            v = args[i + 1]
            # AUDIT FINDING: these hashes are grepped out of a process's stdout, so they are CLAIMED
            # receipts, not confirmed ones. `verified: false` is the honest label until a chain read
            # confirms the hash mined. Never let the log imply a confirmation it did not perform.
            txs.append({"hash": v, "block": None, "verified": False})
    log_result(opt("--id", ""), opt("--status", "ok"), final=final,
               txs=txs, error=opt("--error"))
    return 0


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "log-intent":
        return _cli_log_intent(args[1:])
    if args and args[0] == "log-result":
        return _cli_log_result(args[1:])
    if "--gaps" in args:
        g = gaps()
        print(f"\n  UNFINISHED ACTIONS: {len(g)}")
        for r in g:
            print(f"    {r.get('ts')}  {r.get('actor')}/{r.get('verb')}  "
                  f"({r.get('decided_by')})  {str(r.get('reason'))[:60]}")
        print()
        return 0
    filt = {}
    if "--decided-by" in args:
        filt["decided_by"] = args[args.index("--decided-by") + 1]
    if "--verb" in args:
        filt["verb"] = args[args.index("--verb") + 1]
    ev = read_events(limit=20, **filt)
    print(f"\n  ACTION LOG — {len(ev)} event(s)  [{LOG_PATH}]")
    for r in ev:
        mark = "→" if r.get("phase") == "intent" else ("✅" if r.get("status") == "ok" else "❌")
        print(f"    {mark} {r.get('ts')}  {r.get('actor')}/{r.get('verb')}  "
              f"decided_by={r.get('decided_by')}  {str(r.get('reason'))[:48]}")
    if not ev:
        print("    (empty — no action has been logged yet)")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
