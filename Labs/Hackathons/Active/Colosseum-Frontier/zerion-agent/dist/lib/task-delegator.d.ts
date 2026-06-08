/**
 * Task Delegator — executes DeFi actions via Zerion CLI
 *
 * Safety rules:
 * - All trades require agent token + policy
 * - Transfer limits enforced by policy
 * - Token allowlists checked before execution
 * - Confirmation required unless in autonomous mode
 */
import { ZerionClient } from './zerion-client.js';
import type { AgentPolicy, DeFiOpportunity } from './types.js';
export interface ExecutionResult {
    taskId: string;
    status: 'completed' | 'failed';
    txHash?: string;
    error?: string;
    executedAt: string;
    cost: number;
}
export declare class TaskDelegator {
    private client;
    private policy;
    private taskHistory;
    constructor(client: ZerionClient);
    /**
     * Set agent policy for safety enforcement
     */
    setPolicy(policy: AgentPolicy): void;
    /**
     * Execute a recommended opportunity
     */
    execute(opportunity: DeFiOpportunity, options?: {
        dryRun?: boolean;
        autoApprove?: boolean;
    }): Promise<ExecutionResult>;
    /**
     * Execute a batch of recommendations
     */
    executeBatch(opportunities: DeFiOpportunity[], options?: {
        dryRun?: boolean;
        autoApprove?: boolean;
        maxConcurrent?: number;
        stopOnFailure?: boolean;
    }): Promise<ExecutionResult[]>;
    /**
     * Validate action against policy
     */
    private validateAction;
    /**
     * Execute action via Zerion CLI
     */
    private executeAction;
}
//# sourceMappingURL=task-delegator.d.ts.map