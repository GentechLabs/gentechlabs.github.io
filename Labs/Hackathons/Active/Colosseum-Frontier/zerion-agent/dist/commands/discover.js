/**
 * Discover command — scan a wallet and find DeFi opportunities
 *
 * Usage:
 *   zerion-agent discover <wallet-address>
 *   zerion-agent discover vitalik.eth
 *   zerion-agent discover <wallet> --risk high --min-apy 5
 */
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ZerionClient } from '../lib/zerion-client.js';
import { OpportunityScanner } from '../lib/opportunity-scanner.js';
export const discoverCommand = new Command('discover')
    .description('Scan a wallet and discover DeFi opportunities')
    .argument('<wallet>', 'Wallet address or ENS name')
    .option('--risk <level>', 'Risk tolerance: low, medium, high', 'medium')
    .option('--min-apy <percent>', 'Minimum APY threshold', '2')
    .option('--x402', 'Use x402 pay-per-call (no API key needed)')
    .option('--format <type>', 'Output format: table, json, summary', 'table')
    .action(async (wallet, options) => {
    const spinner = ora(`Scanning ${wallet}...`).start();
    try {
        // Initialize client
        const client = new ZerionClient({
            x402: options.x402,
        });
        const scanner = new OpportunityScanner(client);
        const result = await scanner.scan(wallet);
        spinner.succeed(`Scan complete — found ${result.opportunities.length} opportunities`);
        // Output based on format
        if (options.format === 'json') {
            console.log(JSON.stringify(result, null, 2));
        }
        else if (options.format === 'summary') {
            printSummary(result);
        }
        else {
            printTable(result);
        }
    }
    catch (error) {
        spinner.fail(`Scan failed: ${error.message}`);
        process.exit(1);
    }
});
function printSummary(result) {
    console.log('\n' + chalk.bold('📊 Wallet Overview'));
    console.log(chalk.gray(`  Wallet: ${result.wallet}`));
    console.log(chalk.gray(`  Total Value: $${result.totalValue.toFixed(2)}`));
    console.log(chalk.gray(`  Scanned: ${result.scannedAt}`));
    console.log('\n' + chalk.bold('💰 Idle Assets'));
    if (result.idleAssets.length === 0) {
        console.log(chalk.green('  All assets are working!'));
    }
    else {
        for (const asset of result.idleAssets) {
            console.log(`  ${chalk.yellow(asset.symbol)} — $${asset.value.toFixed(2)} (${asset.chain})`);
        }
    }
    console.log('\n' + chalk.bold('🎯 Recommendations'));
    if (result.recommendations.length === 0) {
        console.log(chalk.gray('  No actionable opportunities found'));
    }
    else {
        for (const rec of result.recommendations) {
            const icon = rec.priority === 'high' ? '🔴' : rec.priority === 'medium' ? '🟡' : '🟢';
            console.log(`  ${icon} ${chalk.bold(rec.opportunity.protocol)} — ${rec.reason}`);
            console.log(`     Est. gain: ${chalk.green(`+$${rec.estimatedGain.toFixed(4)}`)} | Cost: ${chalk.red(`-$${rec.estimatedCost.toFixed(4)}`)} | Net: ${chalk.cyan(`$${rec.netBenefit.toFixed(4)}`)}`);
        }
    }
}
function printTable(result) {
    printSummary(result);
    console.log('\n' + chalk.bold('📋 All Opportunities'));
    console.log(chalk.gray('─'.repeat(80)));
    const headers = ['Protocol', 'Type', 'Chain', 'APY', 'Risk', 'Gas Cost'];
    console.log(chalk.bold(headers.map(h => h.padEnd(15)).join('')));
    console.log(chalk.gray('─'.repeat(80)));
    for (const opp of result.opportunities) {
        const row = [
            opp.protocol.padEnd(15),
            opp.type.padEnd(15),
            opp.chain.padEnd(15),
            opp.apy ? `${opp.apy.toFixed(1)}%`.padEnd(15) : 'N/A'.padEnd(15),
            opp.risk.padEnd(15),
            `$${opp.estimatedGas.toFixed(4)}`.padEnd(15),
        ];
        console.log(row.join(''));
    }
}
//# sourceMappingURL=discover.js.map