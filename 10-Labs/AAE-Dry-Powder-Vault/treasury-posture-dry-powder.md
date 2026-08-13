# Treasury Posture — Dry Powder Mode

**Date:** 2026-08-13
**Source:** Jordan (direct instruction, Gentech Treasury group)

## Status
The GTA treasury is in **DRY POWDER mode**. Jordan is using most of his capital for emergency funds right now, so there should be **nothing deployed** in the GTA wallets on any of the rails.

## What this means
- **Empty LP position is intentional and correct** — do NOT treat it as a problem to fix
- **Do NOT auto-deploy curves or reposition** when the macro loop looks idle
- Keep the treasury **liquid and ready** — only deploy on an explicit greenlight from Jordan
- ~$1.86 native gas in the wallet is sufficient to execute when the word is given

## Standing rule
Until Jordan says otherwise: **dry powder = hold, don't deploy.** The macro-event auto-execution loop stays quiet (no repositioning) because there's nothing deployed to reposition, and that's exactly right.

## Reversal trigger
Jordan gives the greenlight to deploy → then resume normal CURVE-default / BID_ASK-before-macro-event behavior.
