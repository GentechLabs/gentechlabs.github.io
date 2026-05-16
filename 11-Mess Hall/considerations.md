
## Circle Gateway Webhooks (May 14, 2026)
- Circle Gateway now supports real-time webhooks for deposits, forwarded messages, and mints
- Eliminates polling for cross-chain USDC flows
- Useful for: agent payment settlement, multi-chain payment routing, x402 auto-delivery
- Flow: agent pays on one chain → webhook fires on receiving end → service auto-delivers
- Cleaner architecture than RPC polling for payment confirmation
- [ ] Evaluate integration with x402 agent payment stack

## Portfolio Health Issues (May 14, 2026)
- [ ] **Fix data drift:** `index.html` inline JS has 14 projects, `projects.json` has 15. Missing: multi-agent-voice, personal-finance. Descriptions are stale in inline version. Need to regenerate index.html from projects.json or sync the arrays.
- [ ] **Add `.filter-btn` CSS:** Filter buttons (All/Live/Building/Research/Audit) have no styling — renders as unstyled HTML buttons on the live site.
- [ ] **Add `.status-research` CSS:** Research status badge has no background/border color defined.
- [ ] **Wire up avatar image:** `assets/jordan-avatar.png` exists but is never referenced in HTML. CSS `.avatar` class exists but no `<img>` tag uses it.
- [ ] **Sync vault:** 396 uncommitted files in vault. Local diverged from remote — local has new CSS additions (recycle bin, methodology) not on remote. Run `git add -A && git commit && git push`.

## x402B Testnet Experiment (May 16, 2026)
- x402B = escrow, disputes, high-value, deferred delivery (Boson protocol handles this)
- Our move: experiment with x402B on testnet, adopt as escrow standard for agent commerce
- Focus energy on application layer — not reinventing escrow contracts the protocol now provides natively
- [ ] Start testnet experiment with x402B for Kite AI agent commerce escrow

## Personal Milestone Reward (May 2026)
- Xiaomi 15 Ultra — $829 via Giztop
- Snapdragon 8 Elite, Leica Summilux optics, 1" sensor, 6000mAh, 90W charging
- [ ] Track as milestone reward — pull the trigger when a project goal is hit
