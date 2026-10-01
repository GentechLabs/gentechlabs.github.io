#!/usr/bin/env python3
"""provider_canary.py — is each model provider ACTUALLY usable right now?

WHY THIS EXISTS (Jordan, Sep 13 2026)
    Both inference providers went dead at once and nothing surfaced it:
      * Nous Portal — balance running low; no API exposes remaining balance.
      * Ollama Cloud — key was VALID (GET /v1/models returned 200) but
        POST /v1/chat/completions returned 429 "you (jordanjones0902) have
        reached your weekly usage limit".
    Neither provider ships a usage / quota / billing endpoint (all 404), so the
    ONLY honest probe is a real (tiny) inference call and read the answer.

DESIGN
    For each configured provider: send a MINIMAL chat completion (max_tokens=5)
    and classify the HTTP result:
        200            -> OK
        429            -> CAPPED   (carry the provider's own message)
        401/403        -> AUTH     (credential dead / out of funds)
        other          -> FAIL http<code>
        no answer      -> UNREACHABLE
    Silence doctrine: SILENT while every provider answers. Alert when a provider
    that was OK stops answering, and re-arm on recovery. A standing failure does
    NOT re-alert every run — the state file makes "changed" measurable.

SECRETS
    Values are read from the profile .env / auth.json and used in-flight only.
    Presence is reported (bool); values are NEVER printed, logged or stored.

CRON
    script field takes a FILENAME, not a command line -> wrap in provider-canary.sh.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

PROFILE = "/root/.hermes/profiles/gentech-treasury"
ENV_FILE = os.path.join(PROFILE, ".env")
AUTH_FILE = os.path.join(PROFILE, "auth.json")
STATE_FILE = os.path.join(PROFILE, "scripts", ".provider-canary.json")

# A recorded REAL 429 body from Ollama Cloud (captured live 2026-09-13, also
# mirrored in auth.json credential_pool under last_error_message). Used by
# --verify as a fixture so the CAPPED path is testable after the limit resets.
OLLAMA_429_FIXTURE = json.dumps({
    "error": {
        "message": ("you (jordanjones0902) have reached your weekly usage limit, "
                    "please try again later"),
        "type": "api_error", "param": None, "code": None,
    }
})

PROVIDERS = [
    # ── WATCH THE RAILS WE ACTUALLY RUN, NOT THE ONES WE MERELY HAVE (fixed 2026-09-23) ──
    # This list watched `nous` — configured in config.yaml but absent from both the active
    # provider and the whole fallback chain (fallback_providers: opencode-go,
    # fallback_model: clawrouter) — while NOT watching `opencode-go`, the rail this seat runs on.
    # So it alerted hourly about a dead rail we don't use and would have stayed silent if the
    # primary rail died. Jordan's own words: "we're not using Nous Research Portal. We're using
    # Ollama Cloud and OpenCode Go."
    # Same family as the rest of that day: a monitor aimed at a source that cannot answer the
    # question it exists to answer. A canary must watch the rail that carries the traffic.
    {
        "name": "opencode-go",
        "base": "https://opencode.ai/zen/go/v1",
        "model": "deepseek-v4.1-flash",
        "cred": "env",
        "env_var": "OPENCODE_GO_API_KEY",
        "headers": {"x-opencode-session": "steward-canary"},   # required by the rail
    },
    {
        "name": "ollama-cloud",
        "base": "https://ollama.com/v1",
        "model": "glm-5.3-flash",  # configured default_model
        "cred": "env",
        "env_var": "OLLAMA_API_KEY",
    },
]

EXPIRING_SKEW_S = 600  # if the OAuth token dies within 10 min, don't judge it


# ── secrets (presence only, never values) ────────────────────────────────────

def env_key(name):
    if not os.path.exists(ENV_FILE):
        return None
    for line in open(ENV_FILE):
        s = line.strip()
        if s.startswith(name + "="):
            v = s.split("=", 1)[1].strip().strip('"').strip("'")
            return v or None
    return None


def nous_token():
    """(token, seconds_until_expiry or None) from auth.json. Never printed."""
    try:
        a = json.load(open(AUTH_FILE))
        p = a.get("providers", {}).get("nous", {})
        tok = p.get("access_token")
        exp = p.get("expires_at")
        left = None
        if exp:
            try:
                left = (datetime.fromisoformat(exp) - datetime.now(timezone.utc)).total_seconds()
            except Exception:
                left = None
        return tok, left
    except Exception:
        return None, None


def credential(p):
    """Return (secret_or_None, note). note is safe to print."""
    if p["cred"] == "env":
        k = env_key(p["env_var"])
        return k, ("key present" if k else "key MISSING in .env")
    tok, left = nous_token()
    if not tok:
        return None, "oauth token MISSING in auth.json"
    if left is not None and left < EXPIRING_SKEW_S:
        return tok, f"oauth token expiring ({int(left)}s) — not judged this tick"
    return tok, "oauth token present"


# ── probe / classify ─────────────────────────────────────────────────────────

def extract_message(body):
    try:
        d = json.loads(body)
    except Exception:
        return " ".join(body.split())[:180]
    if isinstance(d, dict):
        err = d.get("error")
        if isinstance(err, dict) and err.get("message"):
            return " ".join(str(err["message"]).split())[:180]
        for k in ("message", "detail", "error"):
            if isinstance(d.get(k), str) and d[k].strip():
                return " ".join(d[k].split())[:180]
        try:
            m = d["choices"][0]["message"]["content"]
            return " ".join((m or "").split())[:120]
        except Exception:
            pass
    return " ".join(body.split())[:180]


def classify(code, body):
    if code == 200:
        return "OK", ""
    msg = extract_message(body)
    if code == 429:
        return "CAPPED", msg
    if code in (401, 403):
        return "AUTH", msg
    if code == 400:
        # The rail answered and did NOT reject our credential — it rejected the probe's request
        # shape (e.g. a required harness header). That is a live rail, not an outage, and for a
        # canary the only question is "is it answering and is the key good". Treating 400 as FAIL
        # would page on a working rail; treating it as OK-with-a-note keeps the signal honest.
        return "OK", f"reachable (rail rejected probe shape: {msg[:80]})"
    if code is None:
        return "UNREACHABLE", msg
    return f"FAIL", f"http{code}: {msg}"


def probe(p, secret_override=None, timeout=45):
    secret, note = (secret_override, "override") if secret_override else credential(p)
    if not secret:
        return {"name": p["name"], "status": "NOCR", "code": None,
                "message": note, "note": note, "secret_present": False}
    body = json.dumps({
        "model": p["model"],
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5,
    }).encode()
    # ── A PROBE MUST LOOK LIKE SOMETHING THE EDGE WILL ANSWER (fixed 2026-09-23) ────────
    # Bare urllib gets Cloudflare-blocked (error 1010) by opencode-go's edge and the canary
    # reported that block as an AUTH failure — a healthy rail reported as dead. And opencode-go
    # requires x-opencode-session on every request, so without it the rail answers 400
    # "MissingSessionID" — also not an outage. Both were probe defects, not rail defects.
    # Proof it was the probe: no key -> 401 (auth IS checked), with key -> 400 (auth PASSED),
    # with key + session header -> 200. The instrument, never the rail.
    hdrs = {"Content-Type": "application/json",
            "Authorization": f"Bearer {secret}",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept": "application/json"}
    hdrs.update(p.get("headers") or {})
    req = urllib.request.Request(
        p["base"] + "/chat/completions", data=body, headers=hdrs)
    code, raw = None, ""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            code, raw = r.status, r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        code = e.code
        try:
            raw = e.read().decode(errors="replace")
        except Exception:
            raw = ""
    except Exception as e:
        return {"name": p["name"], "status": "UNREACHABLE", "code": None,
                "message": f"{type(e).__name__}: {e}"[:180], "note": note,
                "secret_present": True}
    status, msg = classify(code, raw)
    return {"name": p["name"], "status": status, "code": code, "message": msg,
            "note": note, "secret_present": True}


# ── change detection (silence doctrine) ──────────────────────────────────────

def load_state(path):
    try:
        return json.load(open(path)).get("providers", {})
    except Exception:
        return {}


def decide(results, prev):
    """Return (changed, alert_lines). Neutral statuses never alert."""
    lines, changed = [], False
    for r in results:
        n, now = r["name"], r["status"]
        if now in ("NOCR",) or (now == "OK" and "expiring" in (r.get("note") or "")):
            continue  # can't judge this tick: credential gone / about to rotate
        old = (prev.get(n) or {}).get("status") or "UNKNOWN"
        if now == old:
            continue
        if now == "OK" and old == "UNKNOWN":
            # first ever reading for a healthy provider is a baseline, not news
            continue
        changed = True
        if now == "OK":
            lines.append(f"  ✅ {n} — OK (recovered; was {old})")
        else:
            icon = {"CAPPED": "🔴", "AUTH": "🔴", "UNREACHABLE": "🟠"}.get(now, "🟠")
            head = f"  {icon} {n} — {now}" + (f" (HTTP {r['code']})" if r["code"] else "")
            lines.append(head)
            if r.get("message"):
                lines.append(f"      provider said: \"{r['message']}\"")
            if old == "OK":
                lines.append("      ⚠️  was OK last tick — provider just went down.")
    return changed, lines


def save_state(path, results, prev):
    merged = dict(prev)
    now = time.time()
    for r in results:
        if r["status"] == "NOCR" or (r["status"] == "OK" and "expiring" in (r.get("note") or "")):
            continue  # keep last real reading
        merged[r["name"]] = {"status": r["status"], "code": r["code"],
                             "message": r["message"], "ts": now}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    json.dump({"updated": datetime.now(timezone.utc).isoformat(),
               "providers": merged}, open(tmp, "w"), indent=2)
    os.replace(tmp, path)


# ── modes ────────────────────────────────────────────────────────────────────

def run(state_path=STATE_FILE, force=False, out=sys.stdout):
    results = [probe(p) for p in PROVIDERS]
    prev = load_state(state_path)
    changed, lines = decide(results, prev)
    if force and not changed:
        lines = [f"  {'✅' if r['status']=='OK' else '🔴'} {r['name']} — {r['status']}"
                 + (f" ({r['code']})" if r["code"] else "") for r in results]
        changed = True
    if changed:
        print(f"🚦 PROVIDER CANARY — change detected "
              f"({datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC)", file=out)
        print(file=out)
        print("\n".join(lines), file=out)
        print(file=out)
        print("  (silent while all providers answer; re-arms on recovery)", file=out)
    save_state(state_path, results, prev)
    return results


def verify(out=sys.stdout):
    """Prove the check BOTH directions with real HTTP, and the 429 path with a
    recorded real fixture. Returns exit code 0 only if every expectation holds."""
    ok = True
    real = {p["name"]: probe(p) for p in PROVIDERS}
    live_ok = all(r["status"] == "OK" for r in real.values())
    print("── DIRECTION 1: real credentials → expect OK → SILENT", file=out)
    for n, r in real.items():
        print(f"   {n:14} {r['status']:10} http={r['code']} {('secret: ' + r['note']) if r['note'] else ''}", file=out)
    print(f"   verdict: {'SILENT ✅' if live_ok else 'would ALERT ⚠️'}", file=out)
    ok &= live_ok

    print("\n── DIRECTION 2: deliberately invalid credential → expect AUTH → ALERT", file=out)
    for p in PROVIDERS:
        bad = probe(p, secret_override="canary-invalid-credential-000")
        ch, lines = decide([bad], {p["name"]: {"status": "OK"}})
        good = (bad["status"] == "AUTH") and ch and lines
        ok &= bool(good)
        print(f"   {p['name']:14} {bad['status']:10} http={bad['code']} → "
              f"{'ALERT ✅' if good else 'NO ALERT ❌'}", file=out)
        for ln in lines:
            print("   " + ln, file=out)

    print("\n── DIRECTION 3: recorded real 429 body → expect CAPPED + provider message", file=out)
    st, msg = classify(429, OLLAMA_429_FIXTURE)
    good = st == "CAPPED" and "weekly usage limit" in msg
    ok &= good
    print(f"   classify(429) = {st} ✅" if st == "CAPPED" else f"   classify(429) = {st} ❌", file=out)
    print(f"   captured message: \"{msg}\"", file=out)
    print(f"   verdict: {'CAPPED path ✅' if good else 'CAPPED path ❌'}", file=out)

    print("\n── DIRECTION 4: unchanged state → expect SILENT (no re-alert)", file=out)
    same = [{"name": "nous", "status": "OK", "code": 200, "message": "", "note": ""}]
    ch, lines = decide(same, {"nous": {"status": "OK"}})
    ok &= (ch is False)
    print(f"   OK→OK changed={ch} → {'SILENT ✅' if not ch else 'RE-ALERTED ❌'}", file=out)

    print("\n── DIRECTION 5: first-ever reading, healthy → expect SILENT (baseline)", file=out)
    ch, lines = decide(same, {})
    ok &= (ch is False)
    print(f"   UNKNOWN→OK changed={ch} → {'SILENT ✅' if not ch else 'ALERTED ❌'}", file=out)

    print(f"\nRESULT: {'ALL CHECKS PASS ✅' if ok else 'FAILURES ❌'}", file=out)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="machine-readable result")
    ap.add_argument("--force", action="store_true", help="report even if unchanged (manual runs)")
    ap.add_argument("--verify", action="store_true", help="self-test both directions (no state write)")
    a = ap.parse_args()
    if a.verify:
        sys.exit(verify())
    res = run(force=a.force)
    if a.json:
        print(json.dumps([{k: r[k] for k in ("name", "status", "code", "message")} for r in res]))


if __name__ == "__main__":
    main()
