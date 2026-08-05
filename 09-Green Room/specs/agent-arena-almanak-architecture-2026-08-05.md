# Agent Arena — Architecture Decision (Aug 5, 2026)

## The stack (Jordan's framing)
- **Social layer = the Gentech portal.** This is the visible front end where humans
  watch agents compete, pick winners, and see live PnL / strategy comparison.
- **Back-end engine = Almanak.** Almanak provides the strategy backtesting +
  copy-trading comparison machinery that powers the comparison the portal displays.

So: **Portal = front end (social), Almanak = back end (backtest/copy engine).**

## Why this reframes the "is Almanak worth it" question
Almanak is NOT heavy-for-one-token. It's shared infrastructure for the Agent Arena
product line (The Agency of Traders, see `09-Green Room/specs/agent-arena-vision.md`).
Standing it up is invested once and pays across:
- AVAX acquisition rail (Safe + signer custody on Avalanche)
- Arena backtesting engine (`almanak strat backtest`: pnl, sweep, optimize, walk-forward,
  monte-carlo, scenario, paper)
- Copy-trading comparison (`almanak copy`: validate, replay, report/go-live gate) — this
  is the leaderboard/comparison layer the portal surfaces

## What Almanak verified offers (tested, isolated 3.12 venv `venvs/almanak-venv`)
- `pip install almanak` → 2.24.0, CLI works
- `strat backtest`: pnl | sweep | optimize | walk-forward | monte-carlo | scenario | paper | dashboard
- `copy`: validate | replay | report (copy-trading operational report + go-live gate)
- Custody: Safe smart accounts + Zodiac signer service (`ALMANAK_PLATFORM_WALLETS`,
  signer endpoint, JWT) + gateway gRPC daemon

## Sequencing (holds per Jordan's build-first note)
- The Agentic Treasury (GTA) is built FIRST → subscriptions/arena LATER.
- Almanak-as-arena-engine is a **dedicated, scoped build** — parked as its own project,
  NOT bolted onto the treasury mid-stream. It gets stood up when we start the social
  arena product.
- AVAX rail: the trade itself can go thin (raw keypair) if wanted now, OR ride Almanak
  later when the engine is up. Not gating anything — 6 assets are already execution-ready
  (BTC/LINK Base, PAXG/ONDO Ethereum, SOL/TAO Solana).

## Status
Architecture decision recorded. Almanak remains in isolated venv, not activated.
Next: keep the ready treasury rails moving; Almanak/arena is a distinct later build.
