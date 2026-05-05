/**
 * Zerion CLI Client — wraps zerion-cli commands with structured output
 *
 * All analysis commands support --x402 (pay-per-call) mode:
 *   ZERION_X402=true zerion-agent discover <wallet>
 *
 * Trading commands require an API key + agent token:
 *   ZERION_API_KEY=zk_... zerion-agent execute swap usdc eth 100
 */
import type { WalletAnalysis, Portfolio, Position, Transaction, PnL, SwapQuote, Chain } from './types.js';
export interface ZerionConfig {
    apiKey?: string;
    x402?: boolean;
    mpp?: boolean;
    chain?: string;
}
export declare class ZerionClient {
    private config;
    constructor(config?: ZerionConfig);
    /**
     * Run a zerion CLI command and parse JSON output
     */
    private run;
    /**
     * Full analysis — portfolio, positions, transactions, PnL in parallel
     */
    analyze(addressOrEns: string): Promise<WalletAnalysis>;
    /**
     * Portfolio value and top positions
     */
    portfolio(addressOrEns: string): Promise<Portfolio>;
    /**
     * Token + DeFi positions
     */
    positions(addressOrEns: string, filter?: 'all' | 'simple' | 'defi'): Promise<Position[]>;
    /**
     * Transaction history
     */
    history(addressOrEns: string, options?: {
        limit?: number;
        chain?: string;
    }): Promise<Transaction[]>;
    /**
     * Profit & loss
     */
    pnl(addressOrEns: string): Promise<PnL>;
    /**
     * Search tokens
     */
    search(query: string): Promise<any>;
    /**
     * List supported chains
     */
    chains(): Promise<Chain[]>;
    /**
     * Swap tokens
     */
    swap(from: string, to: string, amount: number, options?: {
        chain?: string;
        toChain?: string;
    }): Promise<SwapQuote>;
    /**
     * Bridge tokens cross-chain
     */
    bridge(token: string, chain: string, amount: number, options?: {
        toChain?: string;
        toToken?: string;
    }): Promise<any>;
    /**
     * Send tokens
     */
    send(token: string, amount: number, to: string, chain: string): Promise<any>;
    walletList(): Promise<any>;
    walletCreate(): Promise<any>;
    walletSync(): Promise<any>;
    agentCreateToken(wallet: string): Promise<any>;
    agentCreatePolicy(wallet: string, policy: {
        chains?: string[];
        expiry?: string;
        maxTransfer?: number;
        tokenAllowlist?: string[];
    }): Promise<any>;
    watch(addressOrEns: string, options?: {
        events?: string[];
    }): Promise<any>;
}
//# sourceMappingURL=zerion-client.d.ts.map