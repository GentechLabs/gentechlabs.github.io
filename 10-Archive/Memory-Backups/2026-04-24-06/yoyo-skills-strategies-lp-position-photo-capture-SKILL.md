---
name: lp-position-photo-capture
title: LP Position Update via Photo Capture
description: Workflow for extracting LP range/balance data from user screenshots and persisting it to the vault, with dynamic watchlist integration.
trigger: User sends a photo of an LP/management interface with new range, deposits, or balances.
---

## LP Position Update Protocol

### Goal
Extract range, deposit balances, and protocol details from user-uploaded LP screenshots, save the data to the vault immediately, and ensure the watchlist cron reflects the user's actual portfolio.

## Step-by-Step

### 1. Extract Data from Photo
- Use `vision_analyze` with the Ollama Cloud model **GLM 5.1** (set for Strategies group).
- Ask the model to extract:
  - `range_low` and `range_high`
  - `balance_total`
  - `token_a_amount`, `token_a_symbol`
  - `token_b_amount`, `token_b_symbol`
  - `pool_address` (if visible)
  - `protocol_name` (e.g., LFJ, Uniswap V3, Kamino)
  - `bin_width` / `fee_tier` (if visible)

### 2. Cross-Reference with Known State
- Read `03-Strategies/lp-current-status.md` if it exists.
- Ask the user to confirm: *“I see new range X-Y and balance $Z. Correct?”*

### 3. Persist to Vault Immediately
- Write (or append) the extracted data to:
  - `03-Strategies/lp-current-status.md`
  - Include a timestamp and the source (e.g., *“Extracted from LFJ screenshot”*).
- This ensures data survives even if vision tool resets or model errors occur.

### 4. Update Watchlist (if tokens changed)
- Read `03-Strategies/token-watchlist.md`.
- If the LP introduces a new token not on the watchlist, append it.
- Ensure cron job `faed4f588aef` reads tickers from this file dynamically (not hard-coded).

### 5. Report Back
- Confirm: *“Range saved to vault: 9.18–9.40. Balance: $82.8. Tokens synced.”*
- If the vision tool returns a 404 (model missing), fall back to user-provided text and still save to vault.

## Pitfalls
- **Model 404 errors:** Vision tool may fail if the pinned Ollama model is unavailable. Always save data to the vault even if extraction was manual.
- **Session resets:** If the session resets before data is committed, the extracted numbers are lost. The vault file is the only durable store.
- **Hard-coded watchlists:** Never rely on hard-coded symbol arrays in cron jobs. Always read from `token-watchlist.md`.

## Verification
- After update, ask the user: *“Does this match your dashboard?”*
- Re-run the LP cron manually if needed to verify the new range is reflected in the next report.