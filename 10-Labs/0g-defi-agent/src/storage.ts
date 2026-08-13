#!/usr/bin/env node
/**
 * 0G Storage — persist the agent's trade log (Merkle-verified).
 * Every decision the agent makes is stored on 0G Storage with a root hash
 * that proves integrity. This is the agent's verifiable memory.
 */
import { ZgFile, Indexer } from '@0glabs/0g-ts-sdk';
import { ethers } from 'ethers';
import 'dotenv/config';

const RPC_URL = process.env.RPC_URL;
const PRIVATE_KEY = process.env.PRIVATE_KEY;
const STORAGE_INDEXER = process.env.STORAGE_INDEXER || 'https://indexer-storage-testnet-turbo.0g.ai';

/**
 * Upload a trade-log entry to 0G Storage.
 * @param entry JSON-serializable trade decision
 * @returns root hash (the only way to retrieve the file later)
 */
export async function persistTradeLog(entry) {
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const indexer = new Indexer(STORAGE_INDEXER);

  // Write the entry to a temp file
  const fs = await import('node:fs');
  const os = await import('node:os');
  const path = await import('node:path');
  const tmpFile = path.join(os.tmpdir(), `trade-log-${Date.now()}.json`);
  fs.writeFileSync(tmpFile, JSON.stringify(entry, null, 2));

  const file = await ZgFile.fromFilePath(tmpFile);
  try {
    const [tree, err] = await file.merkleTree();
    if (err) throw new Error(`Merkle tree error: ${err}`);
    const rootHash = tree.rootHash();
    console.log('🌳 Merkle root hash:', rootHash);

    const [tx, uploadErr] = await indexer.upload(file, RPC_URL, wallet);
    if (uploadErr) throw new Error(`Upload failed: ${uploadErr.message}`);
    console.log('📤 Upload tx:', tx);

    return rootHash;
  } finally {
    await file.close();
    fs.unlinkSync(tmpFile);
  }
}

// CLI: node src/storage.ts '<json>'
if (import.meta.url === `file://${process.argv[1]}`) {
  const entry = JSON.parse(process.argv[2] || '{"decision":"HOLD","reason":"dry-run"}');
  persistTradeLog(entry).catch((e) => { console.error('❌', e.message); process.exit(1); });
}
