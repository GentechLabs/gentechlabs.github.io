# Handoff — NOT THE GHOST cover: composite Hikari into the ORIGINAL (surgical edit)

**From:** Gentech
**To:** Forge
**Date:** 2026-08-06
**Queue item:** #50 (assigned_to: forge, platform: desktop)
**Priority:** HIGH — Jordan is actively waiting on this

## The problem

Jordan wants the **original** "NOT THE GHOST" album cover kept **pixel-identical**, with Hikari swapped in surgically. AI image-to-image models (FLUX 2 Klein 9B) keep reinterpreting the *entire scene* — the room, lighting, and composition drift on every pass. This is a hard AI limitation, not a prompt problem. **This needs real compositing (Photoshop / GIMP), which is your lane.**

## Assets

- **Original cover (KEEP THIS EXACT):** `https://vanito.gentechlabs.net/characters/not-the-ghost-cover.jpg`
  - Local copy: `/root/vaults/gentech/music/vanito/not-the-ghost-original.jpg`
- **Hikari concert outfit sheet (reference):** `https://vanito.gentechlabs.net/characters/hikari-sakura-outfit-sheet.png`
- **Hikari hairstyle reference:** `https://vanito.gentechlabs.net/characters/hikari-hairstyle-reference.png`
- **Hikari character sheet (canonical look):** `/root/ProtoJay4789.github.io/09-Green Room/HIKARI Character Sheet.md`
- **Hikari visual bible (locked look):** `/root/ProtoJay4789.github.io/09-Green Room/HIKARI Complete Visual Bible.md`

## What to do

Keep the original cover **100% untouched** (composition, room, lighting, pose, title, graffiti). Composite in:

1. **Hikari's hair** — very long black hair with deep crimson-red undertones/highlights, flowing wildly. Match the original's painterly lighting.
2. **Hikari's concert outfit** — strapless black corset with red crisscross lacing, tattered layered black skirt with red underlayer + high slits, fishnet arm sleeves, fishnet stockings with garter, black platform combat boots, black choker, chains at waist, rings, long black nails.
3. **Mirror reflection** — change it to show **Hikari herself** (long black hair, crimson tips, black corset outfit, standing upright facing forward in pale fog) instead of the current shadowy figure.

## Key constraints

- **The original pose must stay** — spine arched back, head thrown up toward the chandelier, arms extended down and behind her. Do NOT change the pose.
- **Match the original's art style** — it's semi-realistic painterly, monochromatic charcoal with warm ember accents, high-contrast chiaroscuro. Hikari must look like she belongs in THIS painting, not pasted-in.
- **The mirror reflection** should be Hikari, not KAGE (Jordan explicitly asked for her in the mirror this round).

## Deliverable

- Save the finished composite to `/root/vaults/gentech/music/vanito/not-the-ghost-hikari-composite.png`
- Write a handoff back to `01-HANDOFFS/forge-to-gentech/` with the result
- Commit + push to the vault so Gentech can deliver it to Jordan

## Verification

- [ ] Original scene preserved pixel-identical (room, lighting, pose, title)
- [ ] Hikari's hair + concert outfit match the character sheet
- [ ] Mirror reflects Hikari
- [ ] Hikari blends into the original's painterly style (not pasted-in)
