/**
 * Type definitions for Zerion API responses and agent internals
 */

export interface WalletAnalysis {
  portfolio: Portfolio;
  positions: Position[];
  history: Transaction[];
  pnl: PnL;
}

export interface Portfolio {
  totalValue: number;
  chainBreakdown: ChainValue[];
  topPositions: Position[];
}

export interface ChainValue {
  chain: string;
  value: number;
  percentage: number;
}

export interface Position {
  type: 'token' | 'defi' | 'nft';
  name: string;
  symbol: string;
  balance: string;
  value: number;
  chain: string;
  protocol?: string;
  apy?: number;
  // DeFi-specific
  poolAddress?: string;
  token0?: string;
  token1?: string;
  // Opportunity metadata (added by scanner)
  opportunity?: DeFiOpportunity;
}

export interface Transaction {
  hash: string;
  chain: string;
  timestamp: string;
  type: 'swap' | 'send' | 'receive' | 'approve' | 'bridge' | 'defi' | 'unknown';
  status: 'success' | 'pending' | 'failed';
  from: string;
  to: string;
  value: number;
  token?: string;
}

export interface PnL {
  totalPnl: number;
  realizedPnl: number;
  unrealizedPnl: number;
  fees: number;
  period: string;
}

export interface Chain {
  id: string;
  name: string;
  shortName: string;
  nativeCurrency: string;
  explorerUrl: string;
}

export interface SwapQuote {
  fromToken: string;
  toToken: string;
  fromAmount: string;
  toAmount: string;
  rate: number;
  priceImpact: number;
  route: string[];
  chain: string;
}

// ── Agent-specific types ──────────────────────────────────────────

export interface DeFiOpportunity {
  id: string;
  type: 'yield' | 'swap' | 'bridge' | 'stake' | 'lp' | 'lend';
  protocol: string;
  chain: string;
  description: string;
  apy?: number;
  tvl?: number;
  risk: 'low' | 'medium' | 'high';
  estimatedGas: number;
  action: TaskAction;
}

export interface TaskAction {
  command: 'swap' | 'bridge' | 'send' | 'stake' | 'lp';
  params: Record<string, any>;
  estimatedCost: number;
  estimatedReturn?: number;
}

export interface AgentTask {
  id: string;
  type: string;
  status: 'pending' | 'approved' | 'executing' | 'completed' | 'failed' | 'rejected';
  opportunity: DeFiOpportunity;
  createdAt: string;
  executedAt?: string;
  result?: any;
  error?: string;
}

export interface AgentPolicy {
  walletAddress: string;
  chains: string[];
  maxTransferAmount: number;
  tokenAllowlist: string[];
  requireApproval: boolean;
  expiry?: string;
}

export interface MonitorEvent {
  type: 'price_alert' | 'position_change' | 'new_opportunity' | 'gas_spike' | 'risk_alert';
  severity: 'info' | 'warning' | 'critical';
  message: string;
  data: any;
  timestamp: string;
}
