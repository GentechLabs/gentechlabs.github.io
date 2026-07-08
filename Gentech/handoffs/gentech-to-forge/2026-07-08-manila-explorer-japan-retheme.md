# Forge Handoff — Manila Explorer → Japan Re-theme

**From:** Gentech (VPS)
**To:** Forge (Desktop)
**Date:** July 8, 2026
**Topic:** Manila Explorer game needs full Japan re-theme before sending to Vanito

---

## Situation

The "Manila Explorer" game you built is entirely Philippines-themed. Jordan's September 2026 trip is to **Japan** (not the Philippines), and he needs Vanito to play a Japan-themed game. Every data layer — locations, food, recipes, prices — is currently hard-coded to Manila/Makati/Philippines.

**Live URL:** http://2.24.195.196:3001 (currently still showing Philippines content)

## What Needs to Change

### 1. Global Text References

| Current | Change To |
|---------|-----------|
| `index.html` title "Manila Explorer" | "Japan Explorer" (or "Tokyo Explorer") |
| `index.html` 🇵🇭 logo | 🇯🇵 |
| `<h1>Manila Explorer</h1>` | `<h1>Japan Explorer</h1>` |
| `app.js` header comment | "Japan Explorer" |
| `server.js` console log | "Japan Explorer running" |
| `styles.css` header comment | "Japan Explorer" |
| `GAME-DESIGN.md` theme / title | Japan travel adventure |

### 2. Locations (app.js — replace all 7)

Current Philippines locations → Replace with actual Japan destinations:

| 🇵🇭 Old | 🇯🇵 New |
|---------|---------|
| Greenbelt | **Senso-ji Temple** (Tokyo) |
| Ayala Museum | **Akihabara Electric Town** |
| Legaspi Park | **Shinjuku Gyoen** park |
| Poblacion | **Golden Gai** (artsy lane) |
| BGC High Street | **Shibuya Crossing / Hachiko** |
| Venice Grand Canal | **Osaka Castle** |
| Jollibee | **Ichiran Ramen** (famous chain) |

**Facts & Budget:** Replace all text facts with accurate Japan info. Convert ₱ prices → ¥ prices (roughly 3× or use real numbers).

### 3. Food / Menu

| 🇵🇭 Old | 🇯🇵 New |
|---------|---------|
| "Jollibee Dash" → "Tokyo Dash" (or "Street Food Dash") | |
| Chickenjoy | Ramen |
| Jolly Spaghetti | Gyoza |
| Burger Steak | Takoyaki |
| Peach Mango Pie | Taiyaki |

### 4. Recipes (Cooking Game)

| 🇵🇭 Old | 🇯🇵 New |
|---------|---------|
| Chicken Adobo | **Tonkotsu Ramen** |
| Sinigang | **Chicken Katsu Curry** |

Ingredients: broth, noodles, pork, soft-boiled egg, nori, panko, curry roux, rice, etc.

### 5. Packing Items

Current items are travel-generic (fine). Just change the success message:
- Line 357: `"Ready for the Philippines trip! 🇵🇭"` → `"Ready for Japan! 🇯🇵"`

### 6. GAME-DESIGN.md

Full re-theme of the design doc:
- Theme: "Japan travel adventure"
- All references to Manila, Makati, Philippines → Japan
- Color palette can stay (Philippine sunset → Japanese sunset, still works)

## Architecture Note

The game engine, mechanics, controls (swipe/touch), viewport (600×600), and styling are all solid — **none of that needs to change**. This is purely a data/content re-theme. Swap out the array constants in `app.js` and update text strings across files.

## Verification Before Shipping

After retheme, verify:

1. ✅ No remaining 🇵🇭, "Manila", "Philippines", "Makati", "Adobo", "Jollibee" in any file
   - Quick check: `grep -ri "manila\|philippines\|makati\|jollibee\|adobo\|₱\|🇵🇭" *`
2. ✅ Game loads and all 4 mini-games work
3. ✅ Locations show Japan facts with ¥ prices
4. ✅ Server restart after changes
5. ✅ Jordan approves before sharing with Vanito

---

*Jordan's waiting on this before sending to Entertainment Group. High priority.*
