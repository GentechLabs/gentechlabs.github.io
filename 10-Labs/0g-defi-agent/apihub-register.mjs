#!/usr/bin/env node
// Register GenTech on APIHub (x402/USDC-on-Base marketplace) — fully autonomous.
// Flow: GET challenge → sign message with EVM wallet → POST /v1/register → API key.
import { ethers } from 'ethers';
import { readFileSync } from 'node:fs';

const WALLET_JSON = '/root/.blockrun/remit-test-wallet.json';
const API = 'https://api.apihub.io';

async function main() {
  const { address, private_key } = JSON.parse(readFileSync(WALLET_JSON, 'utf8'));
  const wallet = new ethers.Wallet(private_key);
  console.log('🔑 Wallet:', wallet.address);

  // 1. Get challenge
  const challenge = await (await fetch(`${API}/v1/register/challenge`)).json();
  const { message, nonce } = challenge.data;
  console.log('📝 Challenge message:', message);

  // 2. Sign the exact message
  const signature = await wallet.signMessage(message);
  console.log('✍️ Signed:', signature.slice(0, 20) + '...');

  // 3. POST registration
  const reg = await fetch(`${API}/v1/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ wallet_address: wallet.address, signature, nonce }),
  });
  const result = await reg.json();
  console.log('📦 Register response:', JSON.stringify(result, null, 2));
  if (result.ok && result.data?.api_key) {
    console.log('✅ APIHub API key:', result.data.api_key);
  }
}

main().catch((e) => { console.error('❌', e.message); process.exit(1); });
