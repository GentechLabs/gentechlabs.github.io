# Green Room — Birdeye BIP Sprint 1

**Created:** Apr 21, 2026
**Deadline:** Apr 25, 2026 (4 days)
**Status:** Scaffolded — ready for testing

---

## What's Built

Desmond scaffolded the **Token Safety Radar Agent** at:
`/root/vaults/gentech/02-Labs/birdeye-token-radar/`

### Files
- `src/radar.py` — Main agent (poll → score → alert)
- `requirements.txt` — Dependencies (requests, python-dotenv)
- `.env.example` — Config template
- `README.md` — Full project docs
- `../06-Content/Birdeye-BIP-Sprint1-Submission-DRAFT.md` — Submission writeup

### What It Does
1. Polls Birdeye `/v2/tokens/new_listing` every 60s
2. Enriches with `/defi/token_security`
3. Scores risk 0-100 (mintable, freezable, LP locked, holder concentration)
4. Alerts via Telegram when score < 60

---

## Pending Items

### Jordan
- [ ] Get Birdeye API key at `bds.birdeye.so`
- [ ] Set up Telegram bot token + chat ID
- [ ] Test the agent with real API calls
- [ ] Record demo video (screen capture of alerts)
- [ ] Submit to Superteam Earn before Apr 25

### YoYo
- [ ] Review scoring weights — are the penalty values right?
- [ ] Research what Birdeye's actual API response format looks like
- [ ] Check if competitors exist (similar token safety tools on Solana)

### DMOB
- [ ] No smart contracts needed for this one
- [ ] Possible: add x402 payment flow (agent pays per-request instead of API key)

### Desmond
- [x] Scaffolded agent code
- [x] Drafted submission writeup
- [x] Created README
- [ ] Polish README based on team feedback
- [ ] Draft X/Twitter build-in-public thread

---

## API Notes

Birdeye x402 endpoint patterns from vault research:
- New listings: `GET /defi/v3/token/new_listing?limit=20&meme_platform_enabled=true`
- Token security: `GET /defi/token_security?address=<TOKEN>`
- Headers: `X-API-KEY`, `x-chain: solana`

**Need to verify actual endpoint paths** — the vault research may have approximate URLs. Jordan should test with real API key.

---

## Competition Details
- Sprint 1 deadline: **Apr 25**
- Prize: 500 USDC + Premium Plus ($1K value)
- Judging: 25% each — Technical Depth, Product Utility, Presentation, Community
- Min requirement: 50 API calls
- Submit via: Superteam Earn
