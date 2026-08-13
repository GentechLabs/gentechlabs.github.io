#!/usr/bin/env node
/**
 * Deploy the GenTech Agent Identity contract to 0G Chain.
 * Uses ethers v6 + evmVersion "cancun" (0G requirement).
 */
import { ethers } from 'ethers';
import { readFileSync } from 'node:fs';
import 'dotenv/config';

const RPC_URL = process.env.RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;

async function main() {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);

  const artifact = JSON.parse(
    readFileSync(new URL('../foundry/out/GenTechAgentIdentity.sol/GenTechAgentIdentity.json', import.meta.url), 'utf8')
  );
  const factory = new ethers.ContractFactory(artifact.abi, artifact.bytecode.object, wallet);

  console.log('🚀 Deploying GenTechAgentIdentity to 0G Chain...');
  console.log(`   Deployer: ${wallet.address}`);
  const contract = await factory.deploy('GenTech AI DeFi Agent', 'ipfs://placeholder');
  await contract.waitForDeployment();
  const addr = await contract.getAddress();
  console.log(`✅ Deployed at: ${addr}`);
  console.log(`   Explorer: https://chainscan-newton.0g.ai/address/${addr}`);
  return addr;
}

main().catch((e) => { console.error('❌ Deploy error:', e.message); process.exit(1); });
