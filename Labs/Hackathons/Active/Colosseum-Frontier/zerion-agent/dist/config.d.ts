/**
 * Configuration — loads from environment variables + .env file
 */
export interface Config {
    zerionApiKey?: string;
    zerionX402: boolean;
    zerionMpp: boolean;
    defaultChain: string;
    maxTransferUsd: number;
    riskTolerance: 'low' | 'medium' | 'high';
    autoApprove: boolean;
    pollIntervalSeconds: number;
}
export declare function loadConfig(): Config;
export declare const CHAIN_MAP: Record<string, string>;
//# sourceMappingURL=config.d.ts.map