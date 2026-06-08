/**
 * Configuration — loads from environment variables + .env file
 */
import dotenv from 'dotenv';
dotenv.config();
export function loadConfig() {
    return {
        zerionApiKey: process.env.ZERION_API_KEY,
        zerionX402: process.env.ZERION_X402 === 'true',
        zerionMpp: process.env.ZERION_MPP === 'true',
        defaultChain: process.env.DEFAULT_CHAIN || 'solana',
        maxTransferUsd: parseFloat(process.env.MAX_TRANSFER_USD || '100'),
        riskTolerance: process.env.RISK_TOLERANCE || 'medium',
        autoApprove: process.env.AUTO_APPROVE === 'true',
        pollIntervalSeconds: parseInt(process.env.POLL_INTERVAL || '30'),
    };
}
export const CHAIN_MAP = {
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
//# sourceMappingURL=config.js.map