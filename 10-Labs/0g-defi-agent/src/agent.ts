#!/usr/bin/env node
/**
 * GenTech AI DeFi Agent — "The Agency of Traders"
 *
 * One agent, one coherent stack, feeding four builds:
 *   • Kite AI  → agentic-payment + settlement layer (Agent Passport, stablecoin rails)
 *   • 0G       → decentralized AI compute (LLM inference) + storage (agent memory/trade log)
 *   • Goldsky  → pay-per-call multi-chain JSON-RPC (via Circle for Agents)
 *   • Circle   → USDC rail / machine-money loop (Circle Agentic Economy prize)
 *
 * The loop: 0G Compute analyzes markets → Goldsky reads on-chain state →
 * Kite AI settles the agent's decision → 0G Storage persists the trade log.
 */
import { ethers } from 'ethers';
import { createZGComputeNetworkBroker } from '@0glabs/0g-serving-broker';
import 'dotenv/config';

// ── Config (from .env — NEVER commit) ──────────────────────────────────────
const RPC_URL = process.env.RPC_URL;                    // 0G Chain RPC
const PRIVATE_KEY = process.env.PRIVATE_KEY;            // agent wallet
const PROVIDER_ADDRESS = process.env.PROVIDER_ADDRESS;  // 0G compute provider
const GOLDSKY_URL = process.env.GOLDSKY_URL || 'https://edge.goldsky.com';
const GOLDSKY_CHAIN = process.env.GOLDSKY_CHAIN || '/standard/evm/8453'; // Base

// ── 1. 0G Compute: decentralized LLM inference for market analysis ─────────
async function analyzeMarket(broker, providerAddress, prompt) {
  const { endpoint, model } = await broker.inference.getServiceMetadata(providerAddress);
  const headers = await broker.inference.getRequestHeaders(providerAddress);
  const messages = [{ role: 'user', content: prompt }];

  const response = await fetch(`${endpoint}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ messages, model }),
  });
  const data = await response.json();
  const answer = data.choices?.[0]?.message?.content ?? '';

  // CRITICAL: processResponse for fee settlement
  let chatID = response.headers.get('ZG-Res-Key') || response.headers.get('zg-res-key');
  if (!chatID) chatID = data.id;
  await broker.inference.processResponse(providerAddress, chatID, JSON.stringify(data.usage ?? {}));

  return answer;
}

// ── 2. Goldsky: pay-per-call JSON-RPC (multi-chain on-chain reads) ─────────
async function readOnChain(chainPath, method, params) {
  const res = await fetch(`${GOLDSKY_URL}${chainPath}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
  });
  const data = await res.json();
  if (data.error) throw new Error(`Goldsky RPC error: ${data.error.message}`);
  return data.result;
}

// ── 3. Kite AI: settle the agent's decision (agentic payment) ──────────────
// Kite Chain is EVM-compatible; the agent holds a Passport wallet and pays
// for services in stablecoins. This is the machine-money loop.
async function settleDecision(wallet, to, amountWei) {
  const tx = await wallet.sendTransaction({ to, value: amountWei });
  return tx.hash;
}

// ── Main loop ──────────────────────────────────────────────────────────────
async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const broker = await createZGComputeNetworkBroker(wallet);

  console.log('🤖 GenTech AI DeFi Agent — Agency of Traders');
  console.log(`   Agent wallet: ${wallet.address}`);
  console.log(`   Chain RPC:   ${RPC_URL}`);
  console.log(`   Goldsky:     ${GOLDSKY_URL}${GOLDSKY_CHAIN}\n`);

  // 1. Read on-chain state via Goldsky (Base, e.g. latest block)
  const block = await readOnChain(GOLDSKY_CHAIN, 'eth_blockNumber', []);
  console.log(`📡 Goldsky RPC → Base latest block: ${parseInt(block, 16)}`);

  // 2. Analyze the market with 0G Compute
  const analysis = await analyzeMarket(
    broker,
    PROVIDER_ADDRESS,
    'You are a DeFi portfolio agent. Given the current market, give a one-paragraph risk-adjusted read on whether to hold, add, or trim a stablecoin LP position. Be concise and specific.'
  );
  console.log(`🧠 0G Compute analysis:\n${analysis}\n`);

  // 3. (Dry-run) settle the decision on Kite AI
  //    Real execution requires a funded Passport wallet + a destination.
  console.log('💸 Kite AI settlement: dry-run (no tx sent — needs funded Passport wallet)');
  console.log('   Decision: ' + (analysis.includes('trim') ? 'TRIM' : 'HOLD/ADD'));

  console.log('\n✅ Loop complete. Trade log would persist to 0G Storage.');
}

main().catch((e) => {
  console.error('❌ Agent error:', e.message);
  process.exit(1);
});
