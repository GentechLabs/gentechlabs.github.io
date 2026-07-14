/**
 * Monitor command — watch wallet activity and price changes
 * 
 * Usage:
 *   zerion-agent monitor <wallet>
 *   zerion-agent monitor <wallet> --events price_alert,position_change
 */

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import { ZerionClient } from '../lib/zerion-client.js';

export const monitorCommand = new Command('monitor')
  .description('Watch wallet activity and changes in real-time')
  .argument('<wallet>', 'Wallet address or ENS')
  .option('--events <types>', 'Comma-separated event types to watch', 'price_alert,position_change,new_opportunity')
  .option('--interval <seconds>', 'Poll interval in seconds', '30')
  .action(async (wallet: string, options: any) => {
    console.log(chalk.bold(`\n👁️  Monitoring ${wallet}`));
    console.log(chalk.gray(`Events: ${options.events}`));
    console.log(chalk.gray(`Interval: ${options.interval}s`));
    console.log(chalk.gray('Press Ctrl+C to stop\n'));

    const client = new ZerionClient();
    let lastState: any = null;

    const poll = async () => {
      try {
        const analysis = await client.analyze(wallet);
        const currentState = JSON.stringify(analysis);

        if (lastState && currentState !== lastState) {
          console.log(chalk.yellow(`[${new Date().toISOString()}] Change detected!`));
          // In production, we'd diff and report specific changes
          console.log(chalk.gray('  Portfolio updated'));
        }

        lastState = currentState;
      } catch (error: any) {
        console.error(chalk.red(`[Error] ${error.message}`));
      }
    };

    // Initial poll
    await poll();

    // Set up interval
    const interval = setInterval(poll, parseInt(options.interval) * 1000);

    // Graceful shutdown
    process.on('SIGINT', () => {
      clearInterval(interval);
      console.log(chalk.gray('\nMonitoring stopped'));
      process.exit(0);
    });
  });
