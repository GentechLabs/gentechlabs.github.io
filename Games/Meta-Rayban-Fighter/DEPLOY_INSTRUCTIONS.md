To deploy Meta Ray-Ban Neural Fighter, we need either:

1. **Cloudflare Pages** (preferred, needs API token setup)
   - Go to https://dash.cloudflare.com/profile/api-tokens
   - Create token with "Account → Cloudflare Pages" permissions
   - Run: `export CLOUDFLARE_API_TOKEN=your_token_here && wrangler pages deploy . --project-name meta-rayban-fighter`

2. **GitHub Pages** (easiest, no auth)
   - Push this repo to GitHub
   - Settings → Pages → Enable from `main` branch
   - URL: `https://yourusername.github.io/meta-rayban-fighter/`

3. **Netlify** (free, simple)
   - Install: `npm install -g netlify-cli`
   - Run: `netlify deploy --prod`
   - URL provided after deploy

## For Meta Ray-Ban Glasses Setup

**On the glasses Meta View app:**
1. Open Meta View on phone
2. Navigate to Apps / Web
3. Add URL: `<deployed-url-from-above>`
4. The HUD will load on glasses display

**Important for Glasses:**
- Game optimized for one-eye HUD (380x600px)
- Dark theme for OLED displays
- High contrast text
- Quick gesture responses (<200ms latency target)

---

**Current Local URL:** `http://localhost:3000` (working on this machine)
**Server Status:** Running (PID 1509165)