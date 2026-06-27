# Meta Ray-Ban Neural Fighter

Darkest Dungeon-style roguelike fighter for Meta Ray-Ban Display Glasses with neural wristband EMG gesture control.

## Demo Scope
- 3 levels with progressive difficulty
- Undead enemies: Skeleton, Zombie, Ghost
- Death Knight boss (Level 3)
- Permadeath: Die = restart at Level 1

## Controls (Gesture → Action)
| Action | Gesture | Cost |
|--------|---------|------|
| Attack | Fist clench | 0 |
| Guard | Palm open + wrist rotate | 0 |
| Counter | Pinch + upward wrist flick | 1 AP |
| Holy Strike | Double tap + forward wrist | 2 AP |
| Smite | Double tap + backward wrist | 2 AP |
| Potion | Peace sign (V) | Consumes potion |

## Game Mechanics
- **HP/AP:** HP = health, AP = action points (regenerate 1/turn)
- **Potions:** 3 max, no refill between floors
- **Heal between levels:** 20% HP (not full)
- **Undead weakness:** Holy Strike deals 2x damage

## Development
```bash
npm run dev
```
Open `http://localhost:3000` for HUD simulator.

## Testing gestures
Use keyboard shortcuts to simulate neural gestures:
- `A` = Attack (Fist clench)
- `G` = Guard (Palm open)
- `C` = Counter (Pinch + flick)
- `H` = Holy Strike (Double tap forward)
- `S` = Smite (Double tap back)
- `P` = Potion (Peace sign)

## Tech Stack
- HTML/CSS/JS for HUD (Meta Web SDK compatible)
- Turn-based combat engine
- EMG gesture mapping (simulated for demo)