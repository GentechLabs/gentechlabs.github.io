#!/usr/bin/env python3
"""Overnight model-health re-probe for Gentech Treasury.

Jordan Sep 7: glm-5.2/kimi audit models (and most of ollama-cloud) are
returning EMPTY (finish_reason: length) on substantive prompts — likely a
temporary backend degradation. This job re-probes the key audit + execution
models on a schedule and reports which models actually return content, so we
know when the independent-audit lever is back.

Exit codes:
  0 = probe ran (models may or may not be healthy)
Cron reports the per-model table to the treasury group; only alerts on CHANGE
per silence doctrine where it applies.
"""
import os, json, sys, time, urllib.request, urllib.error

API = "https://ollama.com/v1"
ENV_KEY = "/root/.hermes/profiles/gentech/.env"

# Models to probe: (label, model_id)
PROBE = [
    ("main/exec",   "deepseek-v4-flash:0731"),
    ("audit/glm",   "glm-5.2"),
    ("audit/glm53", "glm-5.3"),
    ("audit/glmF",  "glm-5.3-flash"),
    ("audit/kimi",  "kimi-k2.7-code"),
    ("audit/k3",    "kimi-k3"),
    ("audit/dsv4p", "deepseek-v4-pro:0813"),
]

# Simple substantive prompt (audit-style). Trivial test alone is not enough —
# every model passed the trivial test Sep 7; only flash ones passed substantive.
SUBSTANTIVE = (
    "Audit one DeFi bug risk. LFJ AVAX/USDC LP. After a withdraw the wallet is "
    "WAVAX-heavy, then the redeploy swaps WAVAX->USDC then addLiquidity. We added "
    "+1.5% swap headroom and settled post-tx verification. Could addLiquidity still "
    "revert, or funds get stuck in the router? Two short sentences."
)


def _key():
    if not os.path.exists(ENV_KEY):
        return None
    for line in open(ENV_KEY):
        if line.strip().startswith("OLLAMA_API_KEY="):
            return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _chat(model, content, max_tokens=300, timeout=90):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": max_tokens,
    }).encode()
    req = urllib.request.Request(
        API + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            d = json.loads(resp.read())
        c = d["choices"][0]["message"]["content"]
        fr = d["choices"][0].get("finish_reason")
        return c, fr
    except urllib.error.HTTPError as e:
        return "", f"HTTP{e.code}"
    except Exception as e:
        return "", f"ERR:{str(e)[:40]}"


def main():
    global key
    key = _key()
    healthy = []
    degraded = []
    results = []
    for label, model in PROBE:
        # Trivial test: does it connect+auth+emit at all?
        c0, fr0 = _chat(model, "What is 2+2? Answer with just the number.", 10, 30)
        trivial = (fr0 == "stop" and c0.strip() != "")
        # Substantive test: the real bar (empty on load = degraded)
        if trivial:
            c1, fr1 = _chat(model, SUBSTANTIVE, 250, 90)
            sub = (fr1 == "stop" and len(c1.strip()) > 20)
        else:
            c1, fr1, sub = "", "", False
        status = "OK" if (trivial and sub) else ("TRIVIAL-ONLY" if trivial else "DEGRADED")
        results.append((label, model, trivial, sub, status, fr0, fr1))
        if sub:
            healthy.append(model)
        else:
            degraded.append(model)
        time.sleep(0.5)

    # State file for change-detection (silence doctrine: report on CHANGE)
    state_path = "/root/.hermes/profiles/gentech-treasury/scripts/.model-health.json"
    prev = {}
    if os.path.exists(state_path):
        try:
            prev = json.load(open(state_path))
        except Exception:
            prev = {}
    now = {}
    for label, model, trivial, sub, status, fr0, fr1 in results:
        now[model] = status

    changed = any(prev.get(m) != s for m, s in now.items())

    # SILENCE DOCTRINE: only emit on CHANGE (e.g. degraded -> OK). With the
    # cron set to no_agent, empty stdout sends nothing — so the group hears
    # about this exactly when the audit models recover (or newly break).
    if not changed:
        json.dump(now, open(state_path, "w"), indent=2)
        return  # empty stdout = silent tick

    print("=== Model health re-probe", time.strftime("%Y-%m-%d %H:%M UTC"), "===")
    for label, model, trivial, sub, status, fr0, fr1 in results:
        print(f"  {label:12} {model:22} {status}")
    print(f"\n  Healthy (substantive): {healthy or 'none'}")
    print(f"  Degraded: {degraded or 'none'}")
    print(f"  Changed since last probe: {changed}")

    json.dump(now, open(state_path, "w"), indent=2)
    sys.exit(0)


if __name__ == "__main__":
    main()
