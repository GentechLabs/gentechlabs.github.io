/**
 * Execute command — run DeFi actions via Zerion CLI
 *
 * Usage:
 *   zerion-agent execute swap usdc eth 100 --chain ethereum
 *   zerion-agent execute bridge sol base 50
 *   zerion-agent execute send usdc 20 --to 0x... --chain base
 *   zerion-agent execute auto <wallet> --approve-high
 */
import { Command } from 'commander';
import ora from 'ora';
import { ZerionClient } from '../lib/zerion-client.js';
import { TaskDelegator } from '../lib/task-delegator.js';
import { OpportunityScanner } from '../lib/opportunity-scanner.js';
export const executeCommand = new Command('execute')
    .description('Execute DeFi actions via Zerion CLI');
// Swap subcommand
executeCommand
    .command('swap')
    .description('Swap tokens')
    .argument('<from>', 'Source token symbol')
    .argument('<to>', 'Destination token symbol')
    .argument('<amount>', 'Amount to swap')
    .option('--chain <chain>', 'Source chain', 'ethereum')
    .option('--to-chain <chain>', 'Destination chain (for cross-chain)')
    .option('--dry-run', 'Preview without executing')
    .action(async (from, to, amount, options) => {
    const spinner = ora(`Swapping ${amount} ${from} → ${to}...`).start();
    try {
        const client = new ZerionClient();
        const delegator = new TaskDelegator(client);
        const result = await delegator.execute({
            id: 'manual-swap',
            type: 'swap',
            protocol: 'Zerion',
            chain: options.chain,
            description: `Swap ${amount} ${from} → ${to}`,
            risk: 'medium',
            estimatedGas: 0.01,
            action: {
                command: 'swap',
                params: { from, to, amount: parseFloat(amount), chain: options.chain, toChain: options.toChain },
                estimatedCost: 0.01,
            },
        }, { dryRun: options.dryRun });
        if (result.status === 'completed') {
            spinner.succeed(options.dryRun ? 'Dry run OK' : `Swap executed: ${result.txHash || 'pending'}`);
        }
        else {
            spinner.fail(`Swap failed: ${result.error}`);
        }
    }
    catch (error) {
        spinner.fail(`Error: ${error.message}`);
    }
});
// Bridge subcommand
executeCommand
    .command('bridge')
    .description('Bridge tokens cross-chain')
    .argument('<token>', 'Token to bridge')
    .argument('<from-chain>', 'Source chain')
    .argument('<amount>', 'Amount to bridge')
    .option('--to-chain <chain>', 'Destination chain')
    .option('--to-token <token>', 'Destination token')
    .option('--dry-run', 'Preview without executing')
    .action(async (token, fromChain, amount, options) => {
    const spinner = ora(`Bridging ${amount} ${token} from ${fromChain}...`).start();
    try {
        const client = new ZerionClient();
        const result = await client.bridge(token, fromChain, parseFloat(amount), options);
        spinner.succeed(`Bridge initiated: ${JSON.stringify(result)}`);
    }
    catch (error) {
        spinner.fail(`Bridge failed: ${error.message}`);
    }
});
// Send subcommand
executeCommand
    .command('send')
    .description('Send tokens to an address')
    .argument('<token>', 'Token to send')
    .argument('<amount>', 'Amount to send')
    .argument('<to>', 'Recipient address')
    .option('--chain <chain>', 'Chain', 'ethereum')
    .option('--dry-run', 'Preview without executing')
    .action(async (token, amount, to, options) => {
    const spinner = ora(`Sending ${amount} ${token} to ${to}...`).start();
    try {
        const client = new ZerionClient();
        const result = await client.send(token, parseFloat(amount), to, options.chain);
        spinner.succeed(`Sent: ${JSON.stringify(result)}`);
    }
    catch (error) {
        spinner.fail(`Send failed: ${error.message}`);
    }
});
// Auto-execute subcommand — scans wallet and executes top recommendations
executeCommand
    .command('auto')
    .description('Auto-execute top recommendations for a wallet')
    .argument('<wallet>', 'Wallet address or ENS')
    .option('--max-ops <n>', 'Maximum operations to execute', '3')
    .option('--approve-high', 'Also execute high-risk opportunities')
    .option('--dry-run', 'Preview all actions without executing')
    .action(async (wallet, options) => {
    const spinner = ora(`Scanning ${wallet} for auto-execution...`).start();
    try {
        const client = new ZerionClient();
        const scanner = new OpportunityScanner(client);
        const delegator = new TaskDelegator(client);
        const scan = await scanner.scan(wallet);
        spinner.text = `Found ${scan.recommendations.length} opportunities, executing top ${options.maxOps}...`;
        // Filter by risk tolerance
        let recs = scan.recommendations;
        if (!options.approveHigh) {
            recs = recs.filter(r => r.opportunity.risk !== 'high');
        }
        const toExecute = recs.slice(0, parseInt(options.maxOps));
        const results = await delegator.executeBatch(toExecute.map(r => r.opportunity), { dryRun: options.dryRun, stopOnFailure: true });
        const succeeded = results.filter(r => r.status === 'completed').length;
        const failed = results.filter(r => r.status === 'failed').length;
        spinner.succeed(`Execution complete: ${succeeded} succeeded, ${failed} failed`);
        for (const result of results) {
            const icon = result.status === 'completed' ? '✅' : '❌';
            console.log(`  ${icon} ${result.taskId}: ${result.txHash || result.error}`);
        }
    }
    catch (error) {
        spinner.fail(`Auto-execute failed: ${error.message}`);
    }
});
//# sourceMappingURL=execute.js.map