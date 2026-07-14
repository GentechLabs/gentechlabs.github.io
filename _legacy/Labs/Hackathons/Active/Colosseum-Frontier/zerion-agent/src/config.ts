/**
 * Configuration — loads from environment variables + .env file
 */

import dotenv from 'dotenv';
dotenv.config();

export interface Config {
  // Zerion API
  zerionApiKey?: string;
  zerionX402: boolean;
  zerionMpp: boolean;

  // Agent defaults
  defaultChain: string;
  maxTransferUsd: number;
  riskTolerance: 'low' | 'medium' | 'high';
  autoApprove: boolean;

  // Monitor
  pollIntervalSeconds: number;
}

export function loadConfig(): Config {
  return {
    zerionApiKey: process.env.ZERION_API_KEY,
    zerionX402: process.env.ZERION_X402 === 'true',
    zerionMpp: process.env.ZERION_MPP === 'true',
    
    defaultChain: process.env.DEFAULT_CHAIN || 'solana',
    maxTransferUsd: parseFloat(process.env.MAX_TRANSFER_USD || '100'),
    riskTolerance: (process.env.RISK_TOLERANCE as Config['riskTolerance']) || 'medium',
    autoApprove: process.env.AUTO_APPROVE === 'true',
    
    pollIntervalSeconds: parseInt(process.env.POLL_INTERVAL || '30'),
  };
}

export const CHAIN_MAP: Record<string, string> = {
  ethereum: 'ethereum',
  eth: 'ethereum',
  base: 'base',
  solana: 'solana',
  sol: 'solana',
  arbitrum: 'arbitrum',
  arb: 'arbitrum',
  optimism: 'optimism',
  op: 'optimism',
  polygon: 'polygon',
  poly: 'polygon',
  avalanche: 'avalanche',
  avax: 'avalanche',
};
