# GenTech PWA Template

Reusable, proven PWA boilerplate for any GenTech surface. Modeled directly on the **Steward Command Center** (live at `gentechlabs.net/Treasury/`), which is the working proof-of-concept.

## What you get
- `manifest.json` — installable, standalone, theme `#8b5cf6`
- `sw.js` — offline cache (shell) + network-first `<surface>-state.json`
- `index.html` — dark theme (Inter + JetBrains Mono, purple/cyan), cards grid, **chat bridge FAB**
- `icons/` — 192 + 512 app icons
- `<surface>-state.json` — live-data scaffold (no backend needed)

## One-command scaffold
Copy the template and fill the placeholders:

```bash
SURFACE=cookbook            # lowercase slug
SURFACE_PATH=Cookbook       # path under /var/www/gentechlabs/
SURFACE_TITLE="GenTech Cookbook"
SURFACE_DESCRIPTION="Filipino recipes → Cincinnati subs"
DEPT=strategies             # bridge department to route chat

DEST=/var/www/gentechlabs/$SURFACE_PATH
mkdir -p $DEST/icons
cp /root/vaults/gentech/10-Labs/pwa-template/icons/*.png $DEST/icons/
sed -e "s/{SURFACE}/$SURFACE/g" \
    -e "s|{SURFACE_PATH}|$SURFACE_PATH|g" \
    -e "s/{SURFACE_TITLE}/$SURFACE_TITLE/" \
    -e "s/{SURFACE_DESCRIPTION}/$SURFACE_DESCRIPTION/" \
    -e "s/{DEPT}/$DEPT/" \
    /root/vaults/gentech/10-Labs/pwa-template/manifest.json > $DEST/manifest.json
sed -e "s/{SURFACE}/$SURFACE/g" -e "s|{SURFACE_PATH}|$SURFACE_PATH|g" \
    /root/vaults/gentech/10-Labs/pwa-template/sw.js > $DEST/sw.js
sed -e "s/{SURFACE}/$SURFACE/g" -e "s|{SURFACE_PATH}|$SURFACE_PATH|g" \
    -e "s/{SURFACE_TITLE}/$SURFACE_TITLE/" -e "s/{SURFACE_DESCRIPTION}/$SURFACE_DESCRIPTION/" \
    -e "s/{DEPT}/$DEPT/" \
    /root/vaults/gentech/10-Labs/pwa-template/index.html > $DEST/index.html
touch $DEST/$SURFACE-state.json
chown -R www-data:www-data $DEST
echo "{}" > $DEST/$SURFACE-state.json
```

## Live-data pattern
Each PWA reads `<surface>-state.json`, refreshed by a cron (heartbeat). Network-first SW means the state is always fresh on the page; offline shows the last cached state.

## Chat bridge
The FAB opens a chat panel hitting the same-origin `/bridge/` nginx proxy → Hermes. Route to any department with `?dept=`.

## Verify
```bash
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/$SURFACE_PATH/index.html
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/$SURFACE_PATH/manifest.json
curl -s -o /dev/null -w "%{http_code}" https://gentechlabs.net/$SURFACE_PATH/sw.js
```
All should return 200.
