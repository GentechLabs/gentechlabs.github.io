/**
 * Sui x402 Plugin — Main Entry Point
 * 
 * Enables AI agents to send/receive x402 micropayments on Sui.
 * Part of GenTech Agent Kit for Sui Overflow 2026.
 */

import { SuiClient, getFullRpcUrl } from '@mysten/sui.js/client';
import { Ed25519Keypair } from '@mysten/sui.js/keypairs/ed25519';
import { TransactionBlock } from '@mysten/sui.js/transactions';
import { fromB64 } from '@mysten/sui.js/utils';

export interface SuiPluginConfig {
  rpcUrl?: string;
  network?: 'mainnet' | 'testnet' | 'devnet';
  privateKey?: string;
}

export interface PaymentResult {
  digest: string;
  status: 'success' | 'failed';
  amount: string;
  recipient: string;
  timestamp: number;
}

export interface BalanceResult {
  sui: string;
  usdc: string;
  address: string;
}

export class SuiX402Plugin {
  private client: SuiClient;
  private keypair: Ed25519Keypair | null = null;
  private address: string = '';

  constructor(config: SuiPluginConfig = {}) {
    const rpcUrl = config.rpcUrl || getFullRpcUrl(config.network || 'mainnet');
    this.client = new SuiClient({ url: rpcUrl });

    if (config.privateKey) {
      this.keypair = Ed25519Keypair.fromSecretKey(fromB64(config.privateKey));
      this.address = this.keypair.getPublicKey().toSuiAddress();
    }
  }

  getAddress(): string {
    return this.address;
  }

  isConnected(): boolean {
    return this.keypair !== null;
  }

  async getBalance(): Promise<BalanceResult> {
    if (!this.address) throw new Error('Plugin not initialized with keypair');

    const [suiBalance, usdcCoins] = await Promise.all([
      this.client.getBalance({ owner: this.address }),
      this.client.getCoins({
        owner: this.address,
        coinType: '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN', // USDC on Sui
      }),
    ]);

    const usdcTotal = usdcCoins.data.reduce((sum, coin) => sum + BigInt(coin.balance), BigInt(0));

    return {
      sui: (BigInt(suiBalance.totalBalance) / BigInt(10**9)).toString(),
      usdc: (usdcTotal / BigInt(10**6)).toString(),
      address: this.address,
    };
  }

  async sendPayment(recipient: string, amountUsdc: number): Promise<PaymentResult> {
    if (!this.keypair) throw new Error('Plugin not initialized with keypair');

    const amountAtomic = BigInt(Math.floor(amountUsdc * 10**6));
    const tx = new TransactionBlock();

    // Split USDC coin for payment
    const coins = await this.client.getCoins({
      owner: this.address,
      coinType: '0x5d4b302506645c37ff133b98c4b50a5ae14841659738d6d733d59d0d217a93bf::coin::COIN',
    });

    if (coins.data.length === 0) throw new Error('No USDC coins found');

    const paymentCoin = tx.splitCoins(tx.gas, [tx.pure(amountAtomic)]);
    tx.transferObjects([paymentCoin], tx.pure(recipient));

    const result = await this.client.signAndExecuteTransactionBlock({
      transactionBlock: tx,
      signer: this.keypair,
      options: { showEffects: true },
    });

    return {
      digest: result.digest,
      status: result.effects?.status?.status === 'success' ? 'success' : 'failed',
      amount: amountUsdc.toString(),
      recipient,
      timestamp: Date.now(),
    };
  }

  async registerAgent(name: string, metadata: Record<string, any>): Promise<string> {
    if (!this.keypair) throw new Error('Plugin not initialized with keypair');

    const tx = new TransactionBlock();
    // Register agent as a Sui object with metadata
    const agent = tx.moveCall({
      target: '0x2::object::new',
      arguments: [tx.pure(JSON.stringify({ name, ...metadata }))],
    });

    const result = await this.client.signAndExecuteTransactionBlock({
      transactionBlock: tx,
      signer: this.keypair,
      options: { showEffects: true },
    });

    return result.digest;
  }
}
