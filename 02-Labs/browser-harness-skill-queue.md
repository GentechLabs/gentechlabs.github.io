# Browser-Harness Domain Skill Queue

Created: 2026-04-18
Owner: Labs (Dmob primary, YoYo research support)
Repo: `/opt/browser-harness`

---

## Why This Matters
Each domain skill we build compounds — the next agent run on that site gets smarter for free. This is our browser automation moat.

---

## Priority 1 — Hackathon Support (ARC Apr 20 = 2 days)

### `domain-skills/devpost/`
- [ ] Submission form selectors (project name, description, tags, team members)
- [ ] File upload flow (screenshots, demo video, presentation PDF)
- [ ] "Manage team" invite flow
- [ ] Hackathon-specific URL patterns (`devpost.com/software/new?challenge_id=XXX`)
- **Why:** ARC submission is due Apr 20. Automating form fill + doc upload saves hours.

### `domain-skills/ethglobal/`
- [ ] Project page creation flow
- [ ] Submission checklist scraping
- [ ] Prize track selection UI
- **Why:** Kite AI (Apr 26), Dev3pack (May 8), Solana Frontier (May 11) all use ETHGlobal portals.

---

## Priority 2 — DeFi Research (YoYo's domain)

### `domain-skills/defi/`
- [ ] **Snapshot.org** — governance proposal scraping, voting power check, proposal creation
- [ ] **Tally.xyz** — delegate tracking, governance participation metrics
- [ ] **DeFiLlama** — protocol TVL extraction, chain comparison, yield farming page
- [ ] **Vesting dashboards** — token unlock schedule scraping (common patterns across protocols)

### `domain-skills/dex/`
- [ ] **Uniswap** — pool creation flow, position management UI, fee tier selection
- [ ] **Trader Joe / LFJ** — liquidity book bin selection, range order setup
- [ ] **Raydium** — concentrated liquidity position management
- **Why:** AgentEscrow Arena needs DEX interaction patterns for sim trading.

---

## Priority 3 — Grant Applications (AVAX grants Jul 14)

### `domain-skills/grants/`
- [ ] **Solana Foundation** — grant application form fields, doc upload, status tracking
- [ ] **AVAX grants portal** — same pattern
- [ ] **Gitcoin** — project registration, round application
- **Why:** Jordan's timeline: AVAX grants deadline Jul 14. Automating the submission = more grants per week.

---

## Priority 4 — Distribution & Growth (Desmond's domain)

### `domain-skills/twitter/`
- [ ] Compose tweet with media attachment
- [ ] Thread creation (multi-tweet)
- [ ] Engagement scraping (likes, retweets, replies on specific tweets)
- **Why:** Beyond x-cli — browser can handle media uploads and thread creation.

### `domain-skills/linkedin/`
- [ ] Company page post creation
- [ ] Job posting scraping (for job board domain skill)
- **Why:** Professional presence for grant applications and partnerships.

---

## Priority 5 — Competitive Intelligence

### `domain-skills/defillama/`
- [ ] Protocol page scraping (TVL, chains, audits, links)
- [ ] Yield farming page (APY, TVL, IL risk indicators)
- [ ] Airdrop tracking page
- **Why:** Research pipeline — automated daily protocol scans.

### `domain-skills/dappradar/`
- [ ] Ranking page scraping (top dApps by chain)
- [ ] Category filtering (DeFi, Gaming, Social)
- **Why:** Solana ecosystem recon for Arena positioning.

---

## Interaction Skills to Build

### `interaction-skills/wallet-connect/`
- [ ] MetaMask popup handling (extension popup is cross-origin)
- [ ] WalletConnect QR flow
- [ ] Phantom wallet integration
- **Why:** Needed for any DeFi interaction that requires signing.

### `interaction-skills/web3-forms/`
- [ ] Transaction confirmation dialogs
- [ ] Gas estimation UI patterns
- [ ] Multi-step approval flows (approve + swap)
- **Why:** Common pattern across all DEX/governance UIs.

---

## How to Contribute

1. Pick a task from the queue
2. Open the site in browser-harness: `uv run browser-harness`
3. Interact, discover selectors, document gotchas
4. Write the skill file at `domain-skills/<site>/filename.md`
5. Follow the format from existing skills (see `github/scraping.md` or `producthunt/scraping.md`)
6. Update this queue — check off completed items

### Skill File Format
```markdown
# Site Name — Feature

URL pattern, prerequisites, step-by-step code, gotchas.
Include: selectors, wait requirements, error handling, common pitfalls.
Do NOT include: secrets, credentials, pixel coordinates.
```
