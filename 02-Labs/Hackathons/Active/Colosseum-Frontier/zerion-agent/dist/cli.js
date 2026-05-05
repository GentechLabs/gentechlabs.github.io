#!/usr/bin/env node
import { Command } from 'commander';
import { discoverCommand } from './commands/discover.js';
import { executeCommand } from './commands/execute.js';
import { monitorCommand } from './commands/monitor.js';
import { analyzeCommand } from './commands/analyze.js';
import { walletCommand } from './commands/wallet.js';
const program = new Command();
program
    .name('zerion-agent')
    .description('Autonomous DeFi agent — auto-discovers opportunities and delegates on-chain tasks via Zerion CLI')
    .version('0.1.0');
// Register commands
program.addCommand(discoverCommand);
program.addCommand(executeCommand);
program.addCommand(monitorCommand);
program.addCommand(analyzeCommand);
program.addCommand(walletCommand);
// Default: show help
program
    .action(async () => {
    program.help();
});
program.parse();
//# sourceMappingURL=cli.js.map