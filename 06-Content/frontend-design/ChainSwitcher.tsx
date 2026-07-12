import { useTheme } from '../styles/ThemeProvider';
import type { ChainTheme } from '../styles/tokens';

const chains: { id: ChainTheme; label: string }[] = [
  { id: 'solana', label: 'Solana' },
  { id: 'avalanche', label: 'Avalanche' },
];

export function ChainSwitcher() {
  const { chain, setChain } = useTheme();

  return (
    <div className="gt-surface" style={{ padding: '12px', display: 'inline-flex', gap: '8px' }}>
      {chains.map((c) => (
        <button
          key={c.id}
          onClick={() => setChain(c.id)}
          className={chain === c.id ? 'gt-btn-primary' : 'gt-btn-secondary'}
        >
          {c.label}
        </button>
      ))}
    </div>
  );
}
