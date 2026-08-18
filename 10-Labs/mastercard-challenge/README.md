# Mastercard Innovation Challenge 2026 — Pre-Execution Governance Guard

**Red team / blue team demo** on GenAI-powered payment fraud for the Mastercard
Innovation Challenge at GFF 2026 (Mumbai).

**The GenTech thesis:** don't just *detect* fraud after it happens — **stop it
at the boundary before the agent can act.** Deterministic pre-execution
governance, the counter-position to stochastic post-hoc fraud detection.

## The demo
- 🔴 **Red team** (`red_team.py`) — a fraud simulator that generates 7 classes
  of GenAI payment-fraud attack at scale: phishing prompts, velocity spikes,
  amount anomalies, identity spoofing, out-of-policy beneficiaries, chain
  shifts, and prompt-injection payment requests.
- 🔵 **Blue team** (`blue_team.py`) — a pre-execution governance guard that
  evaluates each payment intent and returns **BLOCK** (hard policy violation,
  refused before execution), **FLAG** (anomaly, needs principal confirmation),
  or **ALLOW** (all checks pass). Every block carries the exact rule that
  fired — a concrete ERC-8004 / x402 audit trail.
- 🖥️ **Web UI** (`index.html` + `demo_server.py`) — attack → verdict dashboard.
- 🛡️ **Live stack** (`live_stack.py`) — pulls **real output from the deployed
  fraud/security layer** (RugCheck v2 OWASP Agentic Top 10 agent scan + Treasury
  Defender token classification) so the demo is backed by live tooling, not just
  simulation. Degrades gracefully to a labelled "simulated" fallback if a
  service is down.

## Run
```bash
# 1. Tests (no server needed)
python3 test_mastercard.py          # 13/13 pass

# 2. CLI
python3 red_team.py --count 5 --seed 42
python3 blue_team.py --count 5 --seed 42
python3 live_stack.py --self-test   # verify live services reachable

# 3. Web prototype
python3 demo_server.py --port 8080
# open http://localhost:8080
```

## API
```
GET /api/attack            → one simulated attack intent
GET /api/attack/batch?n=5  → batch of attack intents
GET /api/evaluate          → blue-team verdicts
GET /api/live-stack        → real data from RugCheck v2 + Treasury Defender
GET /api/health
```

## Files
| File | Purpose |
|------|---------|
| `red_team.py` | Attack simulator (7 attack types) |
| `blue_team.py` | Pre-execution governance guard (BLOCK/FLAG/ALLOW) |
| `live_stack.py` | Live-data integration (RugCheck v2 + Treasury Defender) |
| `index.html` | Presentable web UI |
| `demo_server.py` | Local server wiring red+blue+live to the UI |
| `test_mastercard.py` | 13-test suite |

## Fit / rationale
The AAE stack is **deterministic pre-execution governance** — policy-bound
execution, ERC-8004 identity, audit trail, x402 rails. This challenge is the
stage to prove that governance-first beats detection-only for agentic fraud.

## Status
- ✅ Build scaffolded + verified (2026-08-18): tests 13/13, server works
- ✅ **Live stack wired** (2026-08-18): demo now pulls real data from RugCheck v2
  (OWASP Agentic Top 10 agent scan) + Treasury Defender (token classification)
- ⏸ **Jordan must register by Aug 20**: https://luma.com/kyz978xv
- 📅 Submission deadline Aug 31 · GFF presentation Sept 8-11 Mumbai
