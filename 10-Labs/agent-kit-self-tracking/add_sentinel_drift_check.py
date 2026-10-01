#!/usr/bin/env python3
"""Add CHECK 10 (sentinel-config-drift) to the treasury self-audit.

WHY (self-caught, Sep 11 2026): the security sentinel matches incidents against
a HAND-MAINTAINED exposure surface (OUR_PROTOCOLS / OUR_CHAINS). I flagged the
risk in the handoff myself: "it must be updated whenever the treasury changes
rails, or relevance decays."

That is the same failure mode as everything else found today — a component that
quietly stops looking in the right place while reporting success. A security
layer that silently misses the rail we actually use is worse than none.

This check asserts: every pool/protocol named in treasury_config.json appears in
the sentinel's OUR_PROTOCOLS. Idempotent.
"""
import pathlib

V = pathlib.Path('/root/vaults/gentech/10-Labs/agent-kit-self-tracking')
A = V / 'treasury_self_audit.py'
s = A.read_text()

if 'check_sentinel_drift' in s:
    print('already present'); raise SystemExit

CHECK = '''

# ── CHECK 10: security-sentinel exposure drift ──────────────────────────
# The sentinel only reports incidents matching OUR_PROTOCOLS / OUR_CHAINS.
# If the treasury moves rails and that list is not updated, the sentinel keeps
# running, keeps reporting "ok", and silently stops covering us. Same class as
# every other bug found on Sep 11: a component that stops looking in the right
# place without failing.
def check_sentinel_drift():
    try:
        cfg = json.load(open(os.path.join(SCRIPTS, "treasury_config.json")))
    except Exception as e:
        add("LOW", "sentinel-drift", "treasury_config.json",
            f"could not read config to cross-check the sentinel ({e})")
        return

    # collect every protocol/type named in the live config
    live = set()
    for _chain, pools in (cfg.get("pools") or {}).items():
        for p in (pools or []):
            for k in ("name", "type", "protocol", "dex"):
                v = str(p.get(k) or "").lower()
                if v:
                    live.add(v)
    if not live:
        return

    # pull the sentinel's declared coverage
    try:
        src = read("security_sentinel.py")
    except Exception:
        add("MED", "sentinel-drift", "security_sentinel.py",
            "sentinel script missing — the attack monitor cannot run",
            "restore security_sentinel.py")
        return

    declared = src.lower()
    for name in sorted(live):
        # a config rail is covered if any meaningful token of its name appears
        toks = [t for t in re.split(r"[^a-z0-9]+", name) if len(t) > 3]
        if not toks:
            continue
        if not any(t in declared for t in toks):
            add("MED", "sentinel-drift", "security_sentinel.py",
                f"live rail '{name}' is NOT in the sentinel's coverage list "
                f"(OUR_PROTOCOLS) — attacks on it would be missed silently",
                "add the protocol to OUR_PROTOCOLS in security_sentinel.py")

    # the sentinel must actually be scheduled, or coverage is theoretical
    try:
        jobs = json.load(open(os.path.expanduser(
            "~/.hermes/profiles/gentech-treasury/cron/jobs.json")))
    except Exception:
        jobs = None
    if jobs is not None:
        jl = jobs if isinstance(jobs, list) else jobs.get("jobs", [])
        sent = [j for j in jl if "sentinel" in str(j.get("name", "")).lower()]
        if not sent:
            add("MED", "sentinel-drift", "cron/jobs.json",
                "security sentinel is not scheduled — no attack monitoring runs",
                "re-create the Security Sentinel cron")
        elif not any(j.get("enabled") for j in sent):
            add("HIGH", "sentinel-drift", "cron/jobs.json",
                "security sentinel cron EXISTS BUT IS DISABLED — monitoring is off",
                "resume the Security Sentinel cron")

'''

s = s.replace("def main():", CHECK + "\ndef main():", 1)
s = s.replace("    check_approvals()", "    check_approvals()\n    check_sentinel_drift()", 1)
A.write_text(s)
print('added check_sentinel_drift + registered in main()')
