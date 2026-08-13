#!/usr/bin/env node
// Register GenTech on RelAI (x402 API marketplace) — fully autonomous.
// Flow: POST publicKey → get challenge → sign → POST signature → sk_live_ key.
import { ethers } from 'ethers';
import { readFileSync } from 'node:fs';

const WALLET_JSON = '/root/.blockrun/remit-test-wallet.json';
const API = 'https://api.relai.fi';

async function main() {
  const { private_key } = JSON.parse(readFileSync(WALLET_JSON, 'utf8'));
  const wallet = new ethers.Wallet(private_key);
  console.log('🔑 Wallet:', wallet.address);

  // 1. Get challenge
  const challenge = await (await fetch(`${API}/mcp/management/bootstrap/agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ publicKey: wallet.address }),
  })).json();
  console.log('📝 Challenge response:', JSON.stringify(challenge).slice(0, 200));

  const message = challenge.message || challenge.data?.message;
  if (!message) throw new Error('No challenge message in response');

  // 2. Sign the message
  const signature = await wallet.signMessage(message);
  console.log('✍️ Signed:', signature.slice(0, 20) + '...');

  // 3. Submit signature
  const reg = await fetch(`${API}/mcp/management/bootstrap/agent`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ publicKey: wallet.address, signature, message, label: 'gentech' }),
  });
  const result = await reg.json();
  console.log('📦 Register response:', JSON.stringify(result, null, 2));
  if (result.key) {
    console.log('✅ RelAI service key:', result.key);
  }
}

main().catch((e) => { console.error('❌', e.message); process.exit(1); });
