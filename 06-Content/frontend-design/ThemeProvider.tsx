import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ChainTheme, ThemeTokens } from './tokens';
import { getChainTokens } from './tokens';

interface ThemeContextValue {
  chain: ChainTheme;
  tokens: ThemeTokens;
  setChain: (chain: ChainTheme) => void;
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [chain, setChainState] = useState<ChainTheme>('solana');

  const setChain = useCallback((next: ChainTheme) => {
    setChainState(next);
    document.documentElement.setAttribute('data-theme', next);
  }, []);

  const tokens = getChainTokens(chain);

  return (
    <ThemeContext.Provider value={{ chain, tokens, setChain }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used inside ThemeProvider');
  return ctx;
}
