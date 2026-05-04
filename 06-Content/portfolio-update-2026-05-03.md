# Portfolio Update — May 3, 2026

## Changes Made

- **Color scheme**: Black (#0a0a0a), Silver (#9ca3af), Green (#22c55e), Red (#ef4444)
  - Primary accent: green (headers, links, borders, hero border)
  - Highlight: red (badge-building, project-card hover)
  - Background: black
  - Text: silver/gray
- **Hackathon list**: Removed ETHGlobal Open Agents (no longer participating); Solana Frontier now "BUILDING"
- **Timeline**: Updated full-time crypto goal to 2027–2028 (from Q4 2026)
- **Project rename**: AAE LP Dashboard → AAE Defi Milestones
- **Header identity**: Changed to "Jordan the ProtoJay"
- **About section**: Added GenTech HQ delegation layer context
- **Navigation**: Added smooth scrolling and scroll-margin for anchor links
- **Roadmap**: Added new Roadmap section with Research/Prototype/Dev/Production phases
- **Avatar**: Placeholder removed; header now uses text identity (Jordan the ProtoJay)

## Files Modified

- `06-Content/portfolio-updated-May4.html` (committed to vault git) — contains all May 4 updates including roadmap, project rename, header identity, and navigation fixes

## Deploy to GitHub Pages

The live site at `https://protojay4789.github.io/` is a separate repo.

**Steps:**
1. Open the `ProtoJay4789/ProtoJay4789.github.io` repo
2. Replace `index.html` (or create one if using a different structure) with the updated `portfolio-updated-May4.html`
   - If the Pages repo uses a different template, merge the CSS changes (colors) and avatar markup
3. Ensure `assets/jordan-avatar.png` exists in the repo (your JinTech photo)
4. GitHub Pages will auto-deploy

## Avatar Instructions

- Image specs: 120×120 px recommended (CSS will circular-crop and border it)
- File location in Pages repo: `assets/jordan-avatar.png`
- If image missing, the emoji `👤` will still show (fallback via `onerror` handler)

## Color Reference

| Purpose | Hex | Variable |
|---|---|---|
| Background | `#0a0a0a` | near-black |
| Surface | `#111` / `#1a1a1a` | dark gray |
| Text primary | `#9ca3af` | silver |
| Text secondary | `#e0e0e0` | light gray |
| Accent (primary) | `#22c55e` | green |
| Accent (highlight) | `#ef4444` | red |
| Badge-building | `#f87171` (red-orange) |
| Badge-queued | `#a855f7` (purple) |
| Status-live | `#22c55e` (green) |
