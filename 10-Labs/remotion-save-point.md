# Remotion Video Pipeline — Save Point
# Created: 2026-07-21
# Status: Scaffolded, needs build

## What's done
- ✅ Remotion project created at `gentech-video-pipeline/`
- ✅ Node v24.15.0, npm 11.12.1
- ✅ RTX 3070 available for GPU-accelerated rendering

## What's next
1. **Build video template components** — React components for social media videos
   - Text overlay template (title, subtitle, CTA)
   - Data visualization template (charts, metrics)
   - Branded intro/outro with GenTech branding
2. **Wire into Social Media Engine cron** — pick up text drafts, render MP4
3. **Set up cron job** — 7pm on Forge's desktop, Wed/Sat
4. **Test render** — `npx remotion render` with RTX 3070

## Files
- `gentech-video-pipeline/` — Remotion project root
- `gentech-video-pipeline/src/Root.tsx` — Entry point
- `gentech-video-pipeline/src/Composition.tsx` — Default composition
