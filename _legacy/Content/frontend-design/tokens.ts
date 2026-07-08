export type ChainTheme = 'solana' | 'avalanche';

export interface ThemeTokens {
  name: string;
  colors: {
    bg: string;
    surface: string;
    surfaceElevated: string;
    primary: string;
    secondary: string;
    accent: string;
    glow: string;
  };
  gradients: {
    accent: string;
  };
  shadows: {
    glowSm: string;
    glowMd: string;
    glowLg: string;
  };
  borders: {
    subtle: string;
    badgeBg: string;
  };
}

export const sharedTokens = {
  colors: {
    ink: '#0A0B0D',
    charcoal: '#13151A',
    slate: '#1E212B',
    mist: '#94A3B8',
    frost: '#E2E8F0',
    snow: '#F8FAFC',
  },
  fonts: {
    display: "'Space Grotesk', sans-serif",
    body: "'Inter', sans-serif",
  },
  spacing: {
    1: '4px',
    2: '8px',
    3: '12px',
    4: '16px',
    5: '24px',
    6: '32px',
    7: '48px',
    8: '64px',
    9: '96px',
  },
  radii: {
    sm: '6px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    full: '9999px',
  },
} as const;

export const chainTokens: Record<ChainTheme, ThemeTokens> = {
  solana: {
    name: 'Solana',
    colors: {
      bg: '#05081A',
      surface: '#0B1029',
      surfaceElevated: '#111A3E',
      primary: '#8B5CF6',
      secondary: '#06B6D4',
      accent: '#A855F7',
      glow: '#3B82F6',
    },
    gradients: {
      accent: 'linear-gradient(135deg, #8B5CF6 0%, #06B6D4 100%)',
    },
    shadows: {
      glowSm: '0 0 12px rgba(139, 92, 246, 0.25)',
      glowMd: '0 0 24px rgba(139, 92, 246, 0.35)',
      glowLg: '0 0 48px rgba(59, 130, 246, 0.3)',
    },
    borders: {
      subtle: 'rgba(139, 92, 246, 0.08)',
      badgeBg: 'rgba(139, 92, 246, 0.12)',
    },
  },
  avalanche: {
    name: 'Avalanche',
    colors: {
      bg: '#080808',
      surface: '#141414',
      surfaceElevated: '#1F1F1F',
      primary: '#E84142',
      secondary: '#B91C1C',
      accent: '#F87171',
      glow: '#EF4444',
    },
    gradients: {
      accent: 'linear-gradient(135deg, #E84142 0%, #991B1B 100%)',
    },
    shadows: {
      glowSm: '0 0 12px rgba(232, 65, 66, 0.25)',
      glowMd: '0 0 24px rgba(232, 65, 66, 0.35)',
      glowLg: '0 0 48px rgba(239, 68, 68, 0.3)',
    },
    borders: {
      subtle: 'rgba(232, 65, 66, 0.08)',
      badgeBg: 'rgba(232, 65, 66, 0.12)',
    },
  },
};

export function getChainTokens(chain: ChainTheme): ThemeTokens {
  return chainTokens[chain];
}
