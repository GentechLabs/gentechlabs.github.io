#!/usr/bin/env node
/**
 * 0G Compute provider discovery — FREE, read-only.
 * Lists available chatbot/text-to-image/speech providers on 0G testnet
 * so we know which PROVIDER_ADDRESS to use for the agent's inference.
 */
import { ethers } from 'ethers';
import { createZGComputeNetworkBroker } from '@0glabs/0g-serving-broker';
import 'dotenv/config';

const RPC_URL = process.env.RPC_URL || 'https://evmrpc-testnet.0g.ai';
// Use a throwaway testnet key if none set — discovery is read-only.
const PRIVATE_KEY = process.env.PRIVATE_KEY || '0x0000000000000000000000000000000000000000000000000000000000000001';

async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const broker = await createZGComputeNetworkBroker(wallet);

  console.log('🔍 Discovering 0G Compute providers on testnet...\n');
  const services = await broker.inference.listService();

  const chatbot = services.filter((s) => s[1] === 'chatbot');
  const image = services.filter((s) => s[1] === 'text-to-image');
  const speech = services.filter((s) => s[1] === 'speech-to-text');

  console.log(`Total services: ${services.length}`);
  console.log(`Chatbot: ${chatbot.length} | Text-to-Image: ${image.length} | Speech-to-Text: ${speech.length}\n`);

  if (chatbot.length) {
    console.log('=== CHATBOT PROVIDERS (for market analysis) ===');
    chatbot.slice(0, 5).forEach((s) => {
      console.log(`  addr=${s[0]} | model=${s[6]} | TEE=${s[10]} | url=${s[2]}`);
    });
  }
  if (image.length) {
    console.log('\n=== TEXT-TO-IMAGE PROVIDERS ===');
    image.slice(0, 3).forEach((s) => {
      console.log(`  addr=${s[0]} | model=${s[6]} | TEE=${s[10]}`);
    });
  }
  if (speech.length) {
    console.log('\n=== SPEECH-TO-TEXT PROVIDERS ===');
    speech.slice(0, 3).forEach((s) => {
      console.log(`  addr=${s[0]} | model=${s[6]} | TEE=${s[10]}`);
    });
  }
}

main().catch((e) => { console.error('❌ Discovery error:', e.message); process.exit(1); });
