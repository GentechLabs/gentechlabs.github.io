/**
 * Wallet command — manage agent wallets via Zerion CLI
 *
 * Usage:
 *   zerion-agent wallet list
 *   zerion-agent wallet create
 *   zerion-agent wallet sync
 *   zerion-agent wallet policy set <wallet> --max-transfer 1000
 *   zerion-agent wallet policy show <wallet>
 */
import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ZerionClient } from '../lib/zerion-client.js';
export const walletCommand = new Command('wallet')
    .description('Manage agent wallets');
// List wallets
walletCommand
    .command('list')
    .description('List managed wallets')
    .action(async () => {
    const client = new ZerionClient();
    try {
        const wallets = await client.walletList();
        console.log(chalk.bold('\n👛 Managed Wallets'));
        console.log(JSON.stringify(wallets, null, 2));
    }
    catch (error) {
        console.error(chalk.red(`Error: ${error.message}`));
    }
});
// Create wallet
walletCommand
    .command('create')
    .description('Create a new agent wallet')
    .action(async () => {
    const spinner = ora('Creating wallet...').start();
    try {
        const client = new ZerionClient();
        const result = await client.walletCreate();
        spinner.succeed('Wallet created!');
        console.log(JSON.stringify(result, null, 2));
    }
    catch (error) {
        spinner.fail(`Failed: ${error.message}`);
    }
});
// Sync wallet
walletCommand
    .command('sync')
    .description('Sync wallet with Zerion app (shows QR code)')
    .action(async () => {
    const client = new ZerionClient();
    try {
        await client.walletSync();
    }
    catch (error) {
        console.error(chalk.red(`Error: ${error.message}`));
    }
});
// Policy management
const policyCommand = walletCommand
    .command('policy')
    .description('Manage agent trading policies');
policyCommand
    .command('set')
    .description('Set trading policy for a wallet')
    .argument('<wallet>', 'Wallet address')
    .option('--chains <chains>', 'Comma-separated allowed chains')
    .option('--max-transfer <amount>', 'Maximum transfer amount in USD', '100')
    .option('--tokens <tokens>', 'Comma-separated token allowlist')
    .option('--expiry <date>', 'Policy expiry date')
    .action(async (wallet, options) => {
    const spinner = ora('Setting policy...').start();
    try {
        const client = new ZerionClient();
        const policy = {};
        if (options.chains)
            policy.chains = options.chains.split(',');
        if (options.maxTransfer)
            policy.maxTransfer = parseFloat(options.maxTransfer);
        if (options.tokens)
            policy.tokenAllowlist = options.tokens.split(',');
        if (options.expiry)
            policy.expiry = options.expiry;
        const result = await client.agentCreatePolicy(wallet, policy);
        spinner.succeed('Policy set!');
        console.log(JSON.stringify(result, null, 2));
    }
    catch (error) {
        spinner.fail(`Failed: ${error.message}`);
    }
});
policyCommand
    .command('show')
    .description('Show current policy for a wallet')
    .argument('<wallet>', 'Wallet address')
    .action(async (wallet) => {
    console.log(chalk.gray(`Policy for ${wallet}:`));
    console.log(chalk.gray('  (Policy display requires Zerion API integration)'));
});
// Agent token
walletCommand
    .command('token')
    .description('Manage agent trading tokens')
    .command('create')
    .description('Create agent token for a wallet')
    .argument('<wallet>', 'Wallet address')
    .action(async (wallet) => {
    const spinner = ora('Creating agent token...').start();
    try {
        const client = new ZerionClient();
        const result = await client.agentCreateToken(wallet);
        spinner.succeed('Agent token created!');
        console.log(JSON.stringify(result, null, 2));
    }
    catch (error) {
        spinner.fail(`Failed: ${error.message}`);
    }
});
//# sourceMappingURL=wallet.js.map