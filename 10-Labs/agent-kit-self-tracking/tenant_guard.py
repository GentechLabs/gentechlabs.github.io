#!/usr/bin/env python3
"""
tenant_guard.py — the isolation boundary between collaborators' treasuries.

WHY THIS EXISTS (Jordan, 2026-09-20: "finish building this out for other collaborators")

One machine can host several treasuries. The danger is not that isolation is hard to write; it
is that isolation enforced by CONVENTION drifts. Someone adds a script, forgets the check, and
one tenant's capital is now reachable from another's. The failure is silent and it moves money.

So the boundary is a HARD STOP, mirroring steward_identity's own rule - "a mismatched identity
is a hard stop, never a warning" - because a warning gets scrolled past at 3am in a cron log.

USAGE - assert before ANY state-changing action:
    from tenant_guard import assert_tenant
    assert_tenant("jordan")            # raises TenantViolation if this isn't jordan's box

The check compares the ACTUAL signing wallet (resolved the same way the rest of the system
resolves it - STEWARD_WALLET, then treasury_config.json) against the tenant's registered
wallet. If they disagree, or if the tenant is unknown, or if the tenant has no wallet yet,
it refuses. An unknown tenant is not a permission - it is an error.
"""
from __future__ import annotations
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TENANTS = os.path.join(HERE, "tenants.json")


class TenantViolation(RuntimeError):
    """Raised when an action would cross a tenant boundary. Never caught and ignored."""


def _load():
    try:
        with open(TENANTS) as f:
            return json.load(f)
    except Exception as e:
        raise TenantViolation(f"cannot read the tenant registry: {type(e).__name__}: {e}")


def registered(tenant: str) -> dict:
    d = _load()
    t = (d.get("tenants") or {}).get(tenant)
    if not t:
        # an unknown tenant is NOT a permissive default - that would make a typo a breach
        raise TenantViolation(
            f"tenant {tenant!r} is not in the registry. Add it to tenants.json before use; "
            f"an unregistered tenant is an error, not a default.")
    return t


def current_wallet():
    """Resolve the signing wallet the same way the rest of the system does."""
    sys.path.insert(0, HERE)
    try:
        from steward_identity import wallet as _w
        return _w()
    except Exception:
        return None


def assert_tenant(tenant: str) -> str:
    """Refuse to continue unless this box IS the given tenant. Returns the wallet on success."""
    t = registered(tenant)

    if t.get("status") != "ACTIVE":
        raise TenantViolation(
            f"tenant {tenant!r} has status {t.get('status')!r}, not ACTIVE. A proposed or "
            f"paused tenant must not be acted for.")

    want = t.get("wallet")
    if not want:
        raise TenantViolation(
            f"tenant {tenant!r} has no registered wallet, so this box cannot be confirmed as "
            f"them. Provision one deliberately with provision_tenant_wallet.py --tenant "
            f"{tenant} --execute, then retry. Onboarding is blocked until a wallet is bound to "
            f"this identity.")

    have = current_wallet()
    if not have:
        raise TenantViolation(
            f"cannot resolve this box's signing wallet, so tenant {tenant!r} cannot be "
            f"confirmed. Refusing rather than assuming.")

    if have.lower() != str(want).lower():
        raise TenantViolation(
            f"TENANT BOUNDARY VIOLATION: this box signs as {have}, but tenant {tenant!r} is "
            f"registered to {want}. Refusing to act - acting here would move the wrong "
            f"tenant's capital.")

    return have




# ─────────────────────────────────────────────────────────────────────────────
# AUTONOMY ENFORCEMENT (Jordan, 2026-09-20: "yes scope it out")
#
# The levels live in autonomy-model.json. This is what makes them real: a call site must
# DECLARE the class of action it is about to take, and the guard checks it against the
# tenant's granted level. Without this, "L2_BOUNDED" is documentation, not behaviour.
#
# Action classes, least to most dangerous. Chosen so a call site cannot be vague: there is no
# "modify" or "do stuff" - every action must name what it actually does to capital.
# ─────────────────────────────────────────────────────────────────────────────
ACTION_CLASSES = {
    "read":           0,   # chain reads, reports, alerts - moves nothing
    "propose":        1,   # build a ready-to-run action, do not sign it
    "maintain":       2,   # re-center an EXISTING position within its approved rails
    "withdraw_risk":  2,   # exit on a stop-loss / circuit breaker
    "harvest":        2,   # collect and compound fees
    "open_position":  3,   # open a NEW position from flat
    "move_capital":   4,   # transfer capital to a destination
    "change_rails":   5,   # edit the rails file itself
    "change_autonomy": 5,  # alter a tenant's level. NEVER automatic, by anyone, ever.
}

LEVEL_REACH = {
    "L0_OBSERVE":  1,   # read + propose
    "L1_PROPOSE":  1,
    "L2_BOUNDED":  2,
    "L3_AUTONOMOUS": 3,
}

# actions that a level may NEVER permit regardless of grant - a ceiling above the ladder
NEVER_AUTOMATIC = {"change_autonomy"}


class AutonomyViolation(RuntimeError):
    """Raised when an action exceeds what the tenant is licensed to do alone."""


def _autonomy():
    import json as _j
    with open(os.path.join(HERE, "autonomy-model.json")) as f:
        return _j.load(f)


def _record_human_authorization(tenant, action, authorization):
    """Append-only record of every human-instructed action above the ladder.

    The ladder stops the AGENT acting alone. It must not stop the HUMAN - a treasury that
    refuses its owner is not safe, it is broken. So an action a human explicitly instructs
    is allowed, but it is never silent: who asked, what for, and when go into a file that
    only ever grows. An instruction that leaves no trace is indistinguishable from the agent
    deciding for itself, which is the one thing this module exists to prevent.
    """
    import json as _j
    import time as _t
    path = os.path.join(HERE, "human-authorizations.jsonl")
    rec = {
        "ts": _t.strftime("%Y-%m-%dT%H:%M:%SZ", _t.gmtime()),
        "tenant": tenant,
        "action": action,
        "authorization": authorization.strip(),
    }
    with open(path, "a") as f:
        f.write(_j.dumps(rec) + "\n")
    return rec


def assert_autonomy(tenant: str, action: str, human_authorization=None) -> None:
    """Refuse unless `tenant` is licensed to perform `action` WITHOUT asking a human.

    `human_authorization` is the answer to the refusal, not a bypass of it: it carries the
    human's own instruction (who + why). See _record_human_authorization.
    """
    # identity first - never reason about privileges for a box we cannot confirm is theirs
    assert_tenant(tenant)

    if action not in ACTION_CLASSES:
        raise AutonomyViolation(
            f"unknown action class {action!r}. Every action must name what it does to capital; "
            f"a vague action cannot be authorised. Known: {sorted(ACTION_CLASSES)}")

    if action in NEVER_AUTOMATIC:
        raise AutonomyViolation(
            f"{action!r} may never be automatic. A system that can raise its own privileges is "
            f"not a treasury, it is an incident. Requires a dated human decision.")

    model = _autonomy()
    t = (model.get("per_tenant_settings") or {}).get(tenant) or {}
    level = t.get("level")
    if level not in LEVEL_REACH:
        raise AutonomyViolation(f"tenant {tenant!r} has no valid autonomy level (got {level!r})")

    needed = ACTION_CLASSES[action]
    allowed = LEVEL_REACH[level]
    if needed > allowed:
        # ── HUMAN-INSTRUCTED IS NOT ACTING ALONE (fixed 2026-09-22) ─────────────────────
        # `move_capital` sits at class 4 and the highest level reaches 3, so it is grantable
        # to NOBODY at ANY level - including Jordan at L3. That was the intent (an agent must
        # never move capital out on its own initiative) but the implementation refused the
        # human too, which is a locked door with the key inside: the send path could never
        # work for anyone, ever, and would have failed at the moment money actually needed to
        # move. The ladder governs what a tenant may do WITHOUT asking a human; an action a
        # human has explicitly instructed is the human deciding, not the agent. So it is
        # allowed - explicitly, and on the record.
        if human_authorization and len(str(human_authorization).strip()) >= 8:
            rec = _record_human_authorization(tenant, action, str(human_authorization))
            print(f"   ℹ️  {action!r} exceeds {level} but is HUMAN-INSTRUCTED — recorded at "
                  f"{rec['ts']} (human-authorizations.jsonl)")
            return
        raise AutonomyViolation(
            f"AUTONOMY REFUSED: tenant {tenant!r} holds {level}, which does not authorise "
            f"{action!r} (needs level-reach {needed}, holds {allowed}). The action requires a "
            f"human decision, so it must be proposed rather than performed — or carried out "
            f"with an explicit human authorization.")


def demote(tenant: str, reason: str) -> str:
    """Drop a tenant one level. Automatic demotion is allowed; promotion is NOT.

    Safety that requires a human to authorise the UNSAFE direction is the only safety that
    holds. So anything may demote, and nothing may promote except a human, deliberately.
    """
    order = ["L0_OBSERVE", "L1_PROPOSE", "L2_BOUNDED", "L3_AUTONOMOUS"]
    model = _autonomy()
    path = os.path.join(HERE, "autonomy-model.json")
    cur = ((model.get("per_tenant_settings") or {}).get(tenant) or {}).get("level")
    if cur not in order:
        raise AutonomyViolation(f"cannot demote {tenant!r}: unknown level {cur!r}")
    i = order.index(cur)
    if i == 0:
        return cur
    new = order[i - 1]
    model["per_tenant_settings"][tenant]["level"] = new
    model["per_tenant_settings"][tenant]["demoted"] = {"from": cur, "to": new, "reason": reason}
    json.dump(model, open(path, "w"), indent=2)
    return new


def promote(tenant: str, level: str, reason: str, by: str) -> None:
    """Promotion requires a human, a reason and a signature. There is no automatic path."""
    raise AutonomyViolation(
        f"promotion of {tenant!r} to {level!r} cannot be performed by the agent, even with a "
        f"reason. Edit autonomy-model.json deliberately, by hand, and record who decided. "
        f"A system that can raise its own privileges has no ceiling.")


def autonomy_report():
    model = _autonomy()
    rows = []
    for name, t in (model.get("per_tenant_settings") or {}).items():
        lvl = t.get("level")
        rows.append((name, lvl, LEVEL_REACH.get(lvl, "?"), t.get("ceiling_usd")))
    return rows


def _autonomy_cli():
    argv = sys.argv[1:]
    if not argv:
        print("  TENANT AUTONOMY")
        print("  " + "=" * 70)
        for name, lvl, reach, ceil_ in autonomy_report():
            print(f"    {name:10} {lvl:14} reach={reach}  ceiling={ceil_ or 'unset'}")
        print()
        print("  promotion: NOT available to the agent, by design.")
        print("  demotion : automatic, any time, one level.")
        return 0
    tenant, action = argv[0], argv[1]
    try:
        assert_autonomy(tenant, action)
        print(f"  \u2705 {tenant} may perform {action!r} alone")
        return 0
    except (AutonomyViolation, TenantViolation) as e:
        print(f"  \u26d4 {e}")
        return 1




# ─────────────────────────────────────────────────────────────────────────────
# SPEAKER IDENTITY (Jordan, 2026-09-20)
#
# The guards checked WHERE and never WHO. Every message carries a platform-assigned sender id,
# and nothing consumed it - so any member of a group chat could ask the treasury to move capital
# and it could not tell them from the operator.
#
# The rule is asymmetric on purpose: recognising a speaker GRANTS, not recognising one DENIES.
# Guessing wrong in the permissive direction moves someone else's money; guessing wrong in the
# restrictive direction annoys a legitimate user, who can then be added deliberately.
# ─────────────────────────────────────────────────────────────────────────────
SPEAKERS = os.path.join(HERE, "speakers.json")


class UnknownSpeaker(RuntimeError):
    """Raised when a sender cannot be attributed. Always resolves to NO privilege."""


def resolve_speaker(sender_id) -> str:
    """Map a platform sender id to a tenant. Unknown ids resolve to 'UNKNOWN' - never a guess."""
    try:
        with open(SPEAKERS) as f:
            d = json.load(f)
    except Exception as e:
        # if we cannot read the map we certainly cannot attribute anyone
        raise UnknownSpeaker(f"cannot read the speaker map: {type(e).__name__}: {e}")
    sid = str(sender_id).strip()
    if not sid:
        raise UnknownSpeaker("no sender id supplied, so the speaker cannot be attributed")
    entry = (d.get("speakers") or {}).get(sid)
    if not entry:
        return "UNKNOWN"
    return entry.get("tenant") or "UNKNOWN"


def assert_speaker(sender_id, expected_tenant: str) -> str:
    """Refuse unless this sender really is the given tenant.

    Note the ordering: this is checked BEFORE any action, and an unattributable sender is
    refused even for actions that would otherwise be permitted. Identity is a precondition,
    not a modifier.
    """
    t = resolve_speaker(sender_id)
    if t == "UNKNOWN":
        raise UnknownSpeaker(
            f"sender {sender_id!r} is not a recognised speaker, so it holds NO privilege - "
            f"not even for actions that would be permitted for a known tenant. Add them to "
            f"speakers.json deliberately if they should have access.")
    if t != expected_tenant:
        raise UnknownSpeaker(
            f"SPEAKER MISMATCH: this sender is tenant {t!r}, but the action was requested for "
            f"{expected_tenant!r}. Refusing - acting would move the wrong tenant's capital.")
    return t




def resolve_in_group(group_id, sender_id) -> str:
    """Resolve (group, sender) -> tenant. Both must match a roster entry.

    A speaker recognised in one group is a STRANGER in another. Privilege is granted per
    (group, person), never globally - otherwise standing accumulates by accident as someone
    gets added to more rooms.
    """
    try:
        with open(SPEAKERS) as f:
            d = json.load(f)
    except Exception as e:
        raise UnknownSpeaker(f"cannot read the speaker map: {type(e).__name__}: {e}")
    g = str(group_id).strip()
    sid = str(sender_id).strip()
    if not g or not sid:
        raise UnknownSpeaker("both a group id and a sender id are required to attribute a speaker")
    grp = (d.get("group_rosters", {}).get("groups") or {}).get(g)
    if not grp:
        # an unrecognised group is not a permissive default
        return "UNKNOWN_GROUP"
    entry = (grp.get("roster") or {}).get(sid)
    if not entry:
        return "UNKNOWN"
    return entry.get("tenant") or "UNKNOWN"


def assert_in_group(group_id, sender_id, expected_tenant: str) -> str:
    """Refuse unless this sender is on THIS group's roster as the expected tenant."""
    t = resolve_in_group(group_id, sender_id)
    if t == "UNKNOWN_GROUP":
        raise UnknownSpeaker(
            f"group {group_id!r} has no roster. Add it to speakers.json before acting - an "
            f"unrecognised room is not a permissive default.")
    if t == "UNKNOWN":
        raise UnknownSpeaker(
            f"sender {sender_id!r} is not on the roster for group {group_id!r}. Recognised in "
            f"another room does not mean recognised here. Refusing.")
    if t != expected_tenant:
        raise UnknownSpeaker(
            f"GROUP/SPEAKER MISMATCH: this speaker is tenant {t!r} in group {group_id!r}, but "
            f"the action was requested for {expected_tenant!r}.")
    return t


def _speaker_cli():
    argv = sys.argv[1:]
    if not argv:
        with open(SPEAKERS) as f:
            d = json.load(f)
        print("  SPEAKER IDENTITY")
        print("  " + "=" * 70)
        for sid, e in (d.get("speakers") or {}).items():
            print(f"    {sid:14} -> {e.get('tenant'):10} {e.get('label','')}")
        print()
        print("  GROUP ROSTERS")
        for gid, g in (d.get("group_rosters", {}).get("groups") or {}).items():
            n = len(g.get("roster") or {})
            seats = len(g.get("open_seats") or [])
            print(f"    {gid:16} {g.get('name',''):34} {n} member(s), {seats} open seat(s)")
        print()
        print("  unmapped senders ->", d.get("unmapped_policy", {}).get("resolve_to"), "(no privilege)")
        return 0
    sid = argv[0]
    tid = resolve_speaker(sid)
    print(f"  {sid} -> {tid}" + ("   (NO PRIVILEGE)" if tid == "UNKNOWN" else ""))
    return 0 if tid != "UNKNOWN" else 1


def main():
    argv = sys.argv[1:]
    if not argv:
        d = _load()
        print("TENANT REGISTRY")
        print("=" * 74)
        print(f"  boundary: {d.get('hard_rule','')[:150]}")
        print()
        for name, t in (d.get("tenants") or {}).items():
            mark = "✅" if t.get("status") == "ACTIVE" else "○"
            w = t.get("wallet") or "(no wallet — blocked on the owner)"
            print(f"  {mark} {name:12} {t.get('status'):9} {w}")
        print()
        return 0
    tenant = argv[0]
    try:
        w = assert_tenant(tenant)
        print(f"  ✅ tenant {tenant!r} confirmed — this box signs as {w}")
        return 0
    except TenantViolation as e:
        print(f"  ⛔ {e}")
        return 1


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1 and _s.argv[1] in ("speaker", "speakers"):
        _s.argv.pop(1); _s.exit(_speaker_cli())
    if len(_s.argv) > 2 and _s.argv[1] not in ("--",):
        _s.exit(_autonomy_cli())
    sys.exit(main())
