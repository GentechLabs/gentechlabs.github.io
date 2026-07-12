/**
 * Zerion CLI Client — wraps zerion-cli commands with structured output
 * 
 * All analysis commands support --x402 (pay-per-call) mode:
 *   ZERION_X402=true zerion-agent discover <wallet>
 * 
 * Trading commands require an API key + agent token:
 *   ZERION_API_KEY=zk_... zerion-agent execute swap usdc eth 100
 */

import { execSync, exec as execAsync } from 'child_process';
import { promisify } from 'util';
import type { 
  WalletAnalysis, 
  Portfolio, 
  Position, 
  Transaction, 
  PnL,
  SwapQuote,
  Chain 
} from './types.js';

const exec = promisify(execAsync);

export interface ZerionConfig {
  apiKey?: string;
  x402?: boolean;
  mpp?: boolean;
  chain?: string;
}

export class ZerionClient {
  private config: ZerionConfig;

  constructor(config: ZerionConfig = {}) {
    this.config = config;
  }

  /**
   * Run a zerion CLI command and parse JSON output
   */
  private async run(command: string): Promise<any> {
    const env: Record<string, string | undefined> = { ...process.env };
    if (this.config.apiKey) env.ZERION_API_KEY = this.config.apiKey;
    if (this.config.x402) env.ZERION_X402 = 'true';
    if (this.config.mpp) env.ZERION_MPP = 'true';

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
    } catch (error: any) {
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
  async analyze(addressOrEns: string): Promise<WalletAnalysis> {
    return this.run(`analyze ${addressOrEns}`);
  }

  /**
   * Portfolio value and top positions
   */
  async portfolio(addressOrEns: string): Promise<Portfolio> {
    return this.run(`portfolio ${addressOrEns}`);
  }

  /**
   * Token + DeFi positions
   */
  async positions(
    addressOrEns: string, 
    filter: 'all' | 'simple' | 'defi' = 'all'
  ): Promise<Position[]> {
    return this.run(`positions ${addressOrEns} --positions ${filter}`);
  }

  /**
   * Transaction history
   */
  async history(
    addressOrEns: string, 
    options: { limit?: number; chain?: string } = {}
  ): Promise<Transaction[]> {
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
  async pnl(addressOrEns: string): Promise<PnL> {
    return this.run(`pnl ${addressOrEns}`);
  }

  /**
   * Search tokens
   */
  async search(query: string): Promise<any> {
    return this.run(`search ${query}`);
  }

  /**
   * List supported chains
   */
  async chains(): Promise<Chain[]> {
    return this.run('chains');
  }

  // ── Trading Commands (require API key + agent token) ───────────────

  /**
   * Swap tokens
   */
  async swap(
    from: string, 
    to: string, 
    amount: number,
    options: { chain?: string; toChain?: string } = {}
  ): Promise<SwapQuote> {
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
  async bridge(
    token: string,
    chain: string,
    amount: number,
    options: { toChain?: string; toToken?: string } = {}
  ): Promise<any> {
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
  async send(
    token: string,
    amount: number,
    to: string,
    chain: string
  ): Promise<any> {
    return this.run(`send ${token} ${amount} --to ${to} --chain ${chain}`);
  }

  // ── Wallet Management ──────────────────────────────────────────────

  async walletList(): Promise<any> {
    return this.run('wallet list');
  }

  async walletCreate(): Promise<any> {
    return this.run('wallet create');
  }

  async walletSync(): Promise<any> {
    return this.run('wallet sync');
  }

  // ── Agent Management ───────────────────────────────────────────────

  async agentCreateToken(wallet: string): Promise<any> {
    return this.run(`agent create-token --wallet ${wallet}`);
  }

  async agentCreatePolicy(
    wallet: string,
    policy: {
      chains?: string[];
      expiry?: string;
      maxTransfer?: number;
      tokenAllowlist?: string[];
    }
  ): Promise<any> {
    const args = [`agent create-policy --wallet ${wallet}`];
    if (policy.chains) args.push(`--chains ${policy.chains.join(',')}`);
    if (policy.expiry) args.push(`--expiry ${policy.expiry}`);
    if (policy.maxTransfer) args.push(`--max-transfer ${policy.maxTransfer}`);
    if (policy.tokenAllowlist) args.push(`--tokens ${policy.tokenAllowlist.join(',')}`);
    return this.run(args.join(' '));
  }

  // ── Watch ──────────────────────────────────────────────────────────

  async watch(
    addressOrEns: string,
    options: { events?: string[] } = {}
  ): Promise<any> {
    const args = [`watch ${addressOrEns}`];
    if (options.events) args.push(`--events ${options.events.join(',')}`);
    return this.run(args.join(' '));
  }
}
