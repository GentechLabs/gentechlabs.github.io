/**
 * Analyze command — read-only wallet analysis via Zerion CLI
 *
 * Usage:
 *   zerion-agent analyze <wallet>
 *   zerion-agent analyze <wallet> --portfolio
 *   zerion-agent analyze <wallet> --positions defi
 *   zerion-agent analyze <wallet> --pnl
 */
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ZerionClient } from '../lib/zerion-client.js';
export const analyzeCommand = new Command('analyze')
    .description('Analyze wallet portfolio, positions, and history')
    .argument('<wallet>', 'Wallet address or ENS name')
    .option('--portfolio', 'Show portfolio overview')
    .option('--positions [filter]', 'Show positions (all, simple, defi)')
    .option('--history', 'Show transaction history')
    .option('--pnl', 'Show profit & loss')
    .option('--chains', 'List supported chains')
    .option('--x402', 'Use x402 pay-per-call')
    .option('--format <type>', 'Output format: table, json', 'table')
    .action(async (wallet, options) => {
    const spinner = ora(`Analyzing ${wallet}...`).start();
    try {
        const client = new ZerionClient({ x402: options.x402 });
        // If no specific option, do full analysis
        const fullAnalysis = !options.portfolio && !options.positions &&
            !options.history && !options.pnl && !options.chains;
        if (options.chains) {
            const chains = await client.chains();
            spinner.succeed('Supported chains:');
            for (const chain of chains) {
                console.log(`  ${chalk.cyan(chain.shortName)} — ${chain.name} (${chain.nativeCurrency})`);
            }
            return;
        }
        if (fullAnalysis || options.portfolio) {
            const portfolio = await client.portfolio(wallet);
            spinner.succeed('Portfolio:');
            if (options.format === 'json') {
                console.log(JSON.stringify(portfolio, null, 2));
            }
            else {
                console.log(chalk.bold('\n📊 Portfolio'));
                console.log(JSON.stringify(portfolio, null, 2));
            }
        }
        if (options.positions !== undefined) {
            const filter = typeof options.positions === 'string' ? options.positions : 'all';
            const positions = await client.positions(wallet, filter);
            spinner.succeed(`Positions (${filter}):`);
            if (options.format === 'json') {
                console.log(JSON.stringify(positions, null, 2));
            }
            else {
                console.log(chalk.bold('\n💼 Positions'));
                console.log(JSON.stringify(positions, null, 2));
            }
        }
        if (options.history) {
            const history = await client.history(wallet, { limit: 20 });
            spinner.succeed('Recent transactions:');
            console.log(JSON.stringify(history, null, 2));
        }
        if (options.pnl) {
            const pnl = await client.pnl(wallet);
            spinner.succeed('Profit & Loss:');
            console.log(chalk.bold('\n📈 PnL'));
            console.log(JSON.stringify(pnl, null, 2));
        }
        if (fullAnalysis) {
            const analysis = await client.analyze(wallet);
            spinner.succeed('Full analysis:');
            console.log(JSON.stringify(analysis, null, 2));
        }
    }
    catch (error) {
        spinner.fail(`Analysis failed: ${error.message}`);
        process.exit(1);
    }
});
//# sourceMappingURL=analyze.js.map