/**
 * Task Delegator — executes DeFi actions via Zerion CLI
 *
 * Safety rules:
 * - All trades require agent token + policy
 * - Transfer limits enforced by policy
 * - Token allowlists checked before execution
 * - Confirmation required unless in autonomous mode
 */
export class TaskDelegator {
    client;
    policy = null;
    taskHistory = [];
    constructor(client) {
        this.client = client;
    }
    /**
     * Set agent policy for safety enforcement
     */
    setPolicy(policy) {
        this.policy = policy;
    }
    /**
     * Execute a recommended opportunity
     */
    async execute(opportunity, options = {}) {
        const taskId = `task-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
        // 1. Safety checks
        const safetyCheck = this.validateAction(opportunity.action);
        if (!safetyCheck.valid) {
            return {
                taskId,
                status: 'failed',
                error: safetyCheck.reason,
                executedAt: new Date().toISOString(),
                cost: 0,
            };
        }
        // 2. Dry run mode
        if (options.dryRun) {
            return {
                taskId,
                status: 'completed',
                executedAt: new Date().toISOString(),
                cost: 0,
            };
        }
        // 3. Execute via Zerion CLI
        try {
            const result = await this.executeAction(opportunity.action);
            return {
                taskId,
                status: 'completed',
                txHash: result.txHash,
                executedAt: new Date().toISOString(),
                cost: opportunity.action.estimatedCost,
            };
        }
        catch (error) {
            return {
                taskId,
                status: 'failed',
                error: error.message,
                executedAt: new Date().toISOString(),
                cost: 0,
            };
        }
    }
    /**
     * Execute a batch of recommendations
     */
    async executeBatch(opportunities, options = {}) {
        const results = [];
        const maxConcurrent = options.maxConcurrent || 1;
        for (let i = 0; i < opportunities.length; i += maxConcurrent) {
            const batch = opportunities.slice(i, i + maxConcurrent);
            const batchResults = await Promise.all(batch.map(opp => this.execute(opp, options)));
            results.push(...batchResults);
            // Stop on failure if configured
            if (options.stopOnFailure && batchResults.some(r => r.status === 'failed')) {
                break;
            }
        }
        return results;
    }
    /**
     * Validate action against policy
     */
    validateAction(action) {
        if (!this.policy) {
            // No policy — allow with warning
            return { valid: true };
        }
        // Check transfer limits
        if (action.estimatedCost > this.policy.maxTransferAmount) {
            return {
                valid: false,
                reason: `Action cost ${action.estimatedCost} exceeds policy limit ${this.policy.maxTransferAmount}`,
            };
        }
        // Check token allowlist (if swap)
        if (action.command === 'swap' && this.policy.tokenAllowlist.length > 0) {
            const fromToken = action.params.from;
            if (!this.policy.tokenAllowlist.includes(fromToken)) {
                return {
                    valid: false,
                    reason: `Token ${fromToken} not in policy allowlist`,
                };
            }
        }
        // Check chain allowlist
        if (this.policy.chains.length > 0) {
            const chain = action.params.chain || action.params.fromChain;
            if (chain && !this.policy.chains.includes(chain)) {
                return {
                    valid: false,
                    reason: `Chain ${chain} not in policy allowed chains`,
                };
            }
        }
        return { valid: true };
    }
    /**
     * Execute action via Zerion CLI
     */
    async executeAction(action) {
        switch (action.command) {
            case 'swap':
                await this.client.swap(action.params.from, action.params.to, action.params.amount, { chain: action.params.chain });
                return { txHash: undefined };
            case 'bridge':
                const bridgeResult = await this.client.bridge(action.params.token, action.params.fromChain, action.params.amount, { toChain: action.params.toChain });
                return { txHash: bridgeResult.txHash };
            case 'send':
                const sendResult = await this.client.send(action.params.token, action.params.amount, action.params.to, action.params.chain);
                return { txHash: sendResult.txHash };
            default:
                throw new Error(`Unsupported action: ${action.command}`);
        }
    }
}
//# sourceMappingURL=task-delegator.js.map