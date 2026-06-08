/**
 * Zerion CLI Client — wraps zerion-cli commands with structured output
 *
 * All analysis commands support --x402 (pay-per-call) mode:
 *   ZERION_X402=true zerion-agent discover <wallet>
 *
 * Trading commands require an API key + agent token:
 *   ZERION_API_KEY=zk_... zerion-agent execute swap usdc eth 100
 */
import { exec as execAsync } from 'child_process';
import { promisify } from 'util';
const exec = promisify(execAsync);
export class ZerionClient {
    config;
    constructor(config = {}) {
        this.config = config;
    }
    /**
     * Run a zerion CLI command and parse JSON output
     */
    async run(command) {
        const env = { ...process.env };
        if (this.config.apiKey)
            env.ZERION_API_KEY = this.config.apiKey;
        if (this.config.x402)
            env.ZERION_X402 = 'true';
        if (this.config.mpp)
            env.ZERION_MPP = 'true';
        try {
            const { stdout, stderr } = await exec(`zerion ${command}`, {
                env,
                maxBuffer: 1024 * 1024, // 1MB buffer
                timeout: 30000,
            });
            if (stderr && !stderr.includes('Warning')) {
                console.error(`[zerion stderr] ${stderr}`);
            }
            return JSON.parse(stdout.trim());
        }
        catch (error) {
            if (error.message?.includes('JSON')) {
                // Some commands return plain text
                return { raw: error.stdout || error.message };
            }
            throw new Error(`Zerion CLI error: ${error.message}`);
        }
    }
    // ── Analysis Commands ──────────────────────────────────────────────
    /**
     * Full analysis — portfolio, positions, transactions, PnL in parallel
     */
    async analyze(addressOrEns) {
        return this.run(`analyze ${addressOrEns}`);
    }
    /**
     * Portfolio value and top positions
     */
    async portfolio(addressOrEns) {
        return this.run(`portfolio ${addressOrEns}`);
    }
    /**
     * Token + DeFi positions
     */
    async positions(addressOrEns, filter = 'all') {
        return this.run(`positions ${addressOrEns} --positions ${filter}`);
    }
    /**
     * Transaction history
     */
    async history(addressOrEns, options = {}) {
        const args = [
            `history ${addressOrEns}`,
            options.limit ? `--limit ${options.limit}` : '',
            options.chain ? `--chain ${options.chain}` : '',
        ].filter(Boolean).join(' ');
        return this.run(args);
    }
    /**
     * Profit & loss
     */
    async pnl(addressOrEns) {
        return this.run(`pnl ${addressOrEns}`);
    }
    /**
     * Search tokens
     */
    async search(query) {
        return this.run(`search ${query}`);
    }
    /**
     * List supported chains
     */
    async chains() {
        return this.run('chains');
    }
    // ── Trading Commands (require API key + agent token) ───────────────
    /**
     * Swap tokens
     */
    async swap(from, to, amount, options = {}) {
        const args = [
            `swap ${from} ${to} ${amount}`,
            options.chain ? `--chain ${options.chain}` : '',
            options.toChain ? `--to-chain ${options.toChain}` : '',
        ].filter(Boolean).join(' ');
        return this.run(args);
    }
    /**
     * Bridge tokens cross-chain
     */
    async bridge(token, chain, amount, options = {}) {
        const args = [
            `bridge ${token} ${chain} ${amount}`,
            options.toChain ? `--to-chain ${options.toChain}` : '',
            options.toToken ? `--to-token ${options.toToken}` : '',
        ].filter(Boolean).join(' ');
        return this.run(args);
    }
    /**
     * Send tokens
     */
    async send(token, amount, to, chain) {
        return this.run(`send ${token} ${amount} --to ${to} --chain ${chain}`);
    }
    // ── Wallet Management ──────────────────────────────────────────────
    async walletList() {
        return this.run('wallet list');
    }
    async walletCreate() {
        return this.run('wallet create');
    }
    async walletSync() {
        return this.run('wallet sync');
    }
    // ── Agent Management ───────────────────────────────────────────────
    async agentCreateToken(wallet) {
        return this.run(`agent create-token --wallet ${wallet}`);
    }
    async agentCreatePolicy(wallet, policy) {
        const args = [`agent create-policy --wallet ${wallet}`];
        if (policy.chains)
            args.push(`--chains ${policy.chains.join(',')}`);
        if (policy.expiry)
            args.push(`--expiry ${policy.expiry}`);
        if (policy.maxTransfer)
            args.push(`--max-transfer ${policy.maxTransfer}`);
        if (policy.tokenAllowlist)
            args.push(`--tokens ${policy.tokenAllowlist.join(',')}`);
        return this.run(args.join(' '));
    }
    // ── Watch ──────────────────────────────────────────────────────────
    async watch(addressOrEns, options = {}) {
        const args = [`watch ${addressOrEns}`];
        if (options.events)
            args.push(`--events ${options.events.join(',')}`);
        return this.run(args.join(' '));
    }
}
//# sourceMappingURL=zerion-client.js.map