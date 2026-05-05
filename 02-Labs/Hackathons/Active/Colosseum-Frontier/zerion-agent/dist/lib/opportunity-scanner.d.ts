/**
 * Opportunity Scanner — analyzes wallet positions and discovers DeFi opportunities
 *
 * The scanner:
 * 1. Fetches current portfolio + positions via Zerion CLI
 * 2. Identifies idle assets (tokens not earning yield)
 * 3. Evaluates yield opportunities across supported protocols
 * 4. Scores opportunities by risk-adjusted return
 * 5. Returns ranked task recommendations
 */
import { ZerionClient } from './zerion-client.js';
import type { Position, DeFiOpportunity } from './types.js';
export interface ScanResult {
    wallet: string;
    scannedAt: string;
    totalValue: number;
    idleAssets: Position[];
    opportunities: DeFiOpportunity[];
    recommendations: Recommendation[];
}
export interface Recommendation {
    priority: 'high' | 'medium' | 'low';
    opportunity: DeFiOpportunity;
    reason: string;
    estimatedGain: number;
    estimatedCost: number;
    netBenefit: number;
}
export declare class OpportunityScanner {
    private client;
    constructor(client: ZerionClient);
    /**
     * Full scan — analyze wallet and discover opportunities
     */
    scan(walletAddress: string): Promise<ScanResult>;
    /**
     * Find tokens sitting idle (not in any DeFi position)
     */
    private findIdleAssets;
    /**
     * Discover yield opportunities for idle assets
     */
    private discoverOpportunities;
    /**
     * Generate Solana yield opportunities for an asset
     */
    private solanaYieldOpportunities;
    /**
     * Generate EVM yield opportunities for an asset
     */
    private evmYieldOpportunities;
    /**
     * Analyze how holdings are split across chains
     */
    private analyzeChainSplit;
    /**
     * Bridge opportunities — consolidate assets on a single chain
     */
    private bridgeOpportunities;
    /**
     * Rank opportunities by net benefit (estimated gain - gas cost)
     */
    private rankOpportunities;
    /**
     * Generate human-readable reason for a recommendation
     */
    private generateReason;
}
//# sourceMappingURL=opportunity-scanner.d.ts.map