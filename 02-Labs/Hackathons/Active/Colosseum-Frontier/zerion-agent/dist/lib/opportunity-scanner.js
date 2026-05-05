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
// Minimum threshold to consider an opportunity worth the gas
const MIN_APY = 2.0;
const MIN_VALUE_USD = 10.0;
const MAX_RISK_TOLERANCE = 'medium'; // low, medium, high
export class OpportunityScanner {
    client;
    constructor(client) {
        this.client = client;
    }
    /**
     * Full scan — analyze wallet and discover opportunities
     */
    async scan(walletAddress) {
        // 1. Fetch portfolio analysis
        const analysis = await this.client.analyze(walletAddress);
        // 2. Identify idle assets (tokens with value but no yield)
        const positions = analysis.positions || [];
        const idleAssets = this.findIdleAssets(positions);
        // 3. Discover opportunities for idle assets
        const opportunities = await this.discoverOpportunities(idleAssets, positions);
        // 4. Score and rank
        const recommendations = this.rankOpportunities(opportunities);
        return {
            wallet: walletAddress,
            scannedAt: new Date().toISOString(),
            totalValue: analysis.portfolio?.totalValue || 0,
            idleAssets,
            opportunities,
            recommendations,
        };
    }
    /**
     * Find tokens sitting idle (not in any DeFi position)
     */
    findIdleAssets(positions) {
        return positions.filter(p => {
            // Token holdings with value above minimum
            if (p.type === 'token' && p.value >= MIN_VALUE_USD) {
                return true;
            }
            return false;
        });
    }
    /**
     * Discover yield opportunities for idle assets
     */
    async discoverOpportunities(idleAssets, allPositions) {
        const opportunities = [];
        for (const asset of idleAssets) {
            // Yield farming opportunities
            if (asset.chain === 'solana') {
                opportunities.push(...this.solanaYieldOpportunities(asset));
            }
            else {
                opportunities.push(...this.evmYieldOpportunities(asset));
            }
        }
        // Cross-chain bridge opportunities (if holdings are split across chains)
        const chainBreakdown = this.analyzeChainSplit(allPositions);
        if (chainBreakdown.length > 1) {
            opportunities.push(...this.bridgeOpportunities(chainBreakdown));
        }
        return opportunities;
    }
    /**
     * Generate Solana yield opportunities for an asset
     */
    solanaYieldOpportunities(asset) {
        const opportunities = [];
        const symbol = asset.symbol?.toLowerCase();
        const chain = 'solana';
        // Raydium LP
        if (['sol', 'usdc', 'usdt'].includes(symbol)) {
            opportunities.push({
                id: `raydium-lp-${symbol}`,
                type: 'lp',
                protocol: 'Raydium',
                chain,
                description: `Provide liquidity on Raydium for ${asset.symbol}/USDC pair`,
                apy: 15 + Math.random() * 20, // Estimated — real version pulls from API
                risk: 'medium',
                estimatedGas: 0.005,
                action: {
                    command: 'swap',
                    params: { from: symbol, to: 'raydium-lp', amount: asset.balance },
                    estimatedCost: 0.005,
                },
            });
        }
        // Marinade staking
        if (symbol === 'sol') {
            opportunities.push({
                id: 'marinade-stake',
                type: 'stake',
                protocol: 'Marinade',
                chain,
                description: 'Stake SOL via Marinade for ~7% APY',
                apy: 7.0,
                risk: 'low',
                estimatedGas: 0.003,
                action: {
                    command: 'stake',
                    params: { token: 'sol', amount: asset.balance },
                    estimatedCost: 0.003,
                },
            });
        }
        // Jupiter yield
        if (['usdc', 'usdt'].includes(symbol)) {
            opportunities.push({
                id: `jupiter-lend-${symbol}`,
                type: 'lend',
                protocol: 'Jupiter',
                chain,
                description: `Lend ${asset.symbol} on Jupiter for yield`,
                apy: 5.0 + Math.random() * 3,
                risk: 'low',
                estimatedGas: 0.004,
                action: {
                    command: 'stake',
                    params: { token: symbol, amount: asset.balance },
                    estimatedCost: 0.004,
                },
            });
        }
        return opportunities;
    }
    /**
     * Generate EVM yield opportunities for an asset
     */
    evmYieldOpportunities(asset) {
        const opportunities = [];
        const symbol = asset.symbol?.toLowerCase();
        // Aave lending
        if (['usdc', 'usdt', 'dai', 'eth', 'weth'].includes(symbol)) {
            opportunities.push({
                id: `aave-lend-${symbol}`,
                type: 'lend',
                protocol: 'Aave',
                chain: asset.chain,
                description: `Lend ${asset.symbol} on Aave V3`,
                apy: 3.0 + Math.random() * 5,
                risk: 'low',
                estimatedGas: 0.01,
                action: {
                    command: 'stake',
                    params: { token: symbol, amount: asset.balance },
                    estimatedCost: 0.01,
                },
            });
        }
        // Uniswap LP
        if (['eth', 'usdc', 'usdt', 'dai'].includes(symbol)) {
            opportunities.push({
                id: `uniswap-lp-${symbol}`,
                type: 'lp',
                protocol: 'Uniswap',
                chain: asset.chain,
                description: `Provide liquidity on Uniswap for ${asset.symbol}/USDC`,
                apy: 10 + Math.random() * 15,
                risk: 'medium',
                estimatedGas: 0.02,
                action: {
                    command: 'lp',
                    params: { token0: symbol, token1: 'usdc', amount: asset.balance },
                    estimatedCost: 0.02,
                },
            });
        }
        return opportunities;
    }
    /**
     * Analyze how holdings are split across chains
     */
    analyzeChainSplit(positions) {
        const chainMap = new Map();
        for (const p of positions) {
            const current = chainMap.get(p.chain) || 0;
            chainMap.set(p.chain, current + p.value);
        }
        return Array.from(chainMap.entries())
            .map(([chain, value]) => ({ chain, value }))
            .sort((a, b) => b.value - a.value);
    }
    /**
     * Bridge opportunities — consolidate assets on a single chain
     */
    bridgeOpportunities(chainSplit) {
        const primaryChain = chainSplit[0].chain;
        const opportunities = [];
        for (let i = 1; i < chainSplit.length; i++) {
            const secondary = chainSplit[i];
            if (secondary.value < MIN_VALUE_USD)
                continue;
            opportunities.push({
                id: `bridge-${secondary.chain}-to-${primaryChain}`,
                type: 'bridge',
                protocol: 'Jupiter Bridge',
                chain: secondary.chain,
                description: `Bridge ${secondary.value.toFixed(0)} USD from ${secondary.chain} to ${primaryChain} for consolidated yield`,
                risk: 'medium',
                estimatedGas: 0.01,
                action: {
                    command: 'bridge',
                    params: { fromChain: secondary.chain, toChain: primaryChain, amount: secondary.value },
                    estimatedCost: 0.01,
                },
            });
        }
        return opportunities;
    }
    /**
     * Rank opportunities by net benefit (estimated gain - gas cost)
     */
    rankOpportunities(opportunities) {
        const recommendations = [];
        for (const opp of opportunities) {
            const estimatedGain = (opp.apy || 0) * 0.01; // Simplified — real version calculates annualized
            const netBenefit = estimatedGain - opp.estimatedGas;
            if (netBenefit <= 0)
                continue;
            const riskLevels = { low: 0, medium: 1, high: 2 };
            const maxRisk = riskLevels[MAX_RISK_TOLERANCE] ?? 1;
            if ((riskLevels[opp.risk] ?? 0) > maxRisk)
                continue;
            let priority = 'low';
            if (netBenefit > 0.05)
                priority = 'high';
            else if (netBenefit > 0.02)
                priority = 'medium';
            recommendations.push({
                priority,
                opportunity: opp,
                reason: this.generateReason(opp),
                estimatedGain,
                estimatedCost: opp.estimatedGas,
                netBenefit,
            });
        }
        return recommendations.sort((a, b) => b.netBenefit - a.netBenefit);
    }
    /**
     * Generate human-readable reason for a recommendation
     */
    generateReason(opp) {
        switch (opp.type) {
            case 'yield':
                return `${opp.protocol} offers ${opp.apy?.toFixed(1)}% APY on ${opp.chain}`;
            case 'lp':
                return `LP position on ${opp.protocol} — estimated ${opp.apy?.toFixed(1)}% APY with impermanent loss risk`;
            case 'stake':
                return `Stake via ${opp.protocol} for steady ${opp.apy?.toFixed(1)}% APY`;
            case 'lend':
                return `Lend on ${opp.protocol} — low-risk yield at ${opp.apy?.toFixed(1)}% APY`;
            case 'bridge':
                return `Consolidate assets to ${opp.chain} for better yield opportunities`;
            default:
                return opp.description;
        }
    }
}
//# sourceMappingURL=opportunity-scanner.js.map