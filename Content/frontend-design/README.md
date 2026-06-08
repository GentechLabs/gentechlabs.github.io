# GenTech Agent Vault — Frontend

Multi-chain React frontend with per-chain visual theming.

## Theming Architecture

The UI uses **CSS custom properties** for instant theme swaps — no JS re-render needed for color changes. The `data-theme` attribute on `<html>` drives the entire palette.

```tsx
import { ThemeProvider, useTheme } from './styles/ThemeProvider';

// Wrap app
<ThemeProvider>
  <App />
</ThemeProvider>

// Use in components
const { chain, setChain, tokens } = useTheme();
setChain('avalanche'); // Instantly turns the UI red
```

## Files

| File | Purpose |
|------|---------|
| `DESIGN.md` | Full design spec (Google spec format) with palettes, typography, components |
| `src/styles/themes.css` | CSS custom properties + utility classes for both chains |
| `src/styles/tokens.ts` | TypeScript token definitions — programmatic access to colors/shadows |
| `src/styles/ThemeProvider.tsx` | React context for switching chains and reading tokens in JS |

## Color Philosophy

- **Solana**: Deep-ocean midnight (`#05081A`) with electric violet (`#8B5CF6`) and cyan (`#06B6D4`) accents. Glow effects are blue/purple.
- **Avalanche**: Volcanic obsidian (`#080808`) with ember red (`#E84142`) and molten highlights. Glow effects are red.

Both share identical layout, spacing, and typography. Only color, glow, and gradient tokens change.

## Recommended Stack

- React 18+ (Vite or Next.js)
- Tailwind CSS (optional — can map tokens to `tailwind.config.js`)
- `@solana/wallet-adapter-react` for Solana
- `wagmi` + `viem` for EVM/Avalanche

## Next Steps

1. `npm create vite@latest . -- --template react-ts`
2. Add Tailwind if desired, import `themes.css` in `main.tsx`
3. Wire wallet adapters per chain
4. Build vault dashboard using `gt-*` utility classes
