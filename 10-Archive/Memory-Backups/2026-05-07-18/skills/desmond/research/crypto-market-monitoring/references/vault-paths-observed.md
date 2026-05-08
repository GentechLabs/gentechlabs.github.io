# Vault Config Paths — LP & Watchlist State

**Confirmed paths used in 2026-05-04 session:**

## CMC Configuration
| File | Purpose | Checked? |
|------|---------|----------|
| `/root/.hermes/profiles/yoyo/secrets/cmc_api_key.txt` | CMC Pro API key (plaintext) | ✅ Exists |
| `/root/.hermes/scripts/cmc_config.json` | CMC watchlist_id, API key (JSON) | ✅ Exists |
| `/root/vaults/gentech/03-Strategies/cron-watchlist-config.md` | Canonical source for active watchlist coins | ✅ Source of truth |

## LP Position Configuration
| File | Purpose | Checked? |
|------|---------|----------|
| `/root/vaults/gentech/00-HQ/config/defi-lp-config.env` | Position range, pool address, wallet, shape | ✅ Read |
| `/root/vaults/gentech/03-Strategies/LFJ-AVAX-USDC-5bps-Analysis.md` | Position history, analysis notes, entry data | ✅ Read |

## Expected State Files (for future cron jobs)
| File | Purpose |
|------|---------|
| `~/.hermes/scripts/.lfj-position-state.json` | LP position state: last_price, efficiency, timestamp |
| `~/.hermes/scripts/.cmc-watchlist-state.json` | Watchlist price history for smart-skip logic |

## Watchlist Coins Source
- **Primary config:** `03-Strategies/cron-watchlist-config.md` (FALSE earlier — dead link; now verified at `/root/vaults/gentech/03-Strategies/cron-watchlist-config.md`)
- **Coins tracked:** BTC, SOL, LINK, AVAX, TAO, XAUt, BEAM, LAND, PROPS (9 active; removed COQ, ARENA, WIF, JUP per config notes)
- **CMC Watchlist URL:** `https://coinmarketcap.com/watchlist/67453707ad745f0bbd4ad54f` (Bullish)

## Notes
- The `cmc-watchlist-scraper` skill was missing → direct CMC API used as fallback (still works with API key)
- DexScreener pool API returned Cloudflare challenge and empty responses → fallback to CMC spot price successful
- Always verify file paths exist before reading; use `test -f` checks in shell scripts