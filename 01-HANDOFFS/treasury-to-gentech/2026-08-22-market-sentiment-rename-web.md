# Handoff to Gentech (HQ) — narrative-rotation → market-sentiment rename (web) (Aug 22, 2026)

**From:** Treasury → **To:** Gentech (HQ) / Gin

## What changed — demo site (gentechlabs.net) ✅ LIVE
Renamed all user-facing "Narrative Rotation" → "Market Sentiment" across the demo site:
- `narrative-rotation.html` — title, header, section title, description (now "Market Sentiment — Bull/Bear Radar + Sector Rotation")
- `demo.html` — "Market Sentiment Scanner" card + treasury layer description
- `index.html` — "market sentiment scanning" in the Layer 7 stack card
- `command-center.html` — "Market Sentiment Scout" agent + activity line
- `treasury-demo.html` — layer description + "📈 Sentiment" report line

All verified live (HTTP 200, content confirmed).

## What changed — website (ProtoJay4789.github.io)
- `DeFi/defi-dashboard.html` — button, section title, loading text → "Market Sentiment"
- Committed to **both `main` and `gh-pages`** branches.

## ⚠️ Correction (Jordan, Aug 22 2026)
**GitHub Pages is RETIRED.** The live site is the **VPS + Cloudflare** (gentechlabs.net),
served directly from `/var/www/gentechlabs/` (not git-tracked). The ProtoJay4789.github.io
404 is irrelevant — that repo is no longer the deployment target. The demo site
(gentechlabs.net) is the source of truth and is fully live with the rename.

## Note
The `rotation-data.json` file in the website repo has **git merge-conflict markers** (`<<<<<<<`)
corrupting it — pre-existing, needs cleanup. Flagged for a separate pass.
