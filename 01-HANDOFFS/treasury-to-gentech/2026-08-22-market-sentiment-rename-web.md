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
- Committed to **both `main` and `gh-pages`** branches (gh-pages is what the live site serves)

## ⚠️ Pre-existing issue found (not caused by this change)
The live GitHub Pages site (`ProtoJay4789.github.io`) returns **404 on the whole site** — it was
down before this change too. The rename is correctly on both branches, but the site isn't
serving. Needs a separate deploy fix (Pages source branch / build config).

## Note
The `rotation-data.json` file in the website repo has **git merge-conflict markers** (`<<<<<<<`)
corrupting it — pre-existing, needs cleanup. Flagged for a separate pass.
