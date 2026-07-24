/**
 * Solana x402 Agent Economy — API Server
 * 
 * Agents pay via x402 (USDC on Solana) to interact with
 * AgentRegistry and JobEscrow smart contracts.
 * 
 * Flow:
 *   1. Agent sends request → HTTP 402 Payment Required
 *   2. Agent signs payment proof (USDC on Solana)
 *   3. Server verifies → calls Solana contract
 *   4. Returns result + receipt
 */

import express from 'express';
import { ethers } from 'ethers';
import crypto from 'crypto';

const app = express();
app.use(express.json());

// Configuration
const CONFIG = {
  solanaRpc: process.env.SOLANA_RPC || 'https://api.devnet.solana.com',
  routerAddress: process.env.ROUTER_ADDRESS || '0x...',
  usdcMint: 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v', // Solana USDC
  minPayment: '0.01', // USDC
  port: process.env.PORT || 3080,
};

// Mock storage for pending payments
const pendingPayments = new Map();

// --- x402 Handler ---

function challenge402(req, price) {
  const paymentId = 'sol_' + crypto.randomBytes(16).toString('hex');
  pendingPayments.set(paymentId, {
    amount: price,
    asset: CONFIG.usdcMint,
    chain: 'solana',
    recipient: CONFIG.routerAddress,
    expiresAt: Date.now() + 300_000, // 5 min
  });

  return {
    status: 402,
    headers: {
      'X-Payment-Required': paymentId,
      'X-Payment-Amount': price,
      'X-Payment-Token': CONFIG.usdcMint,
      'X-Payment-Chain': 'solana',
      'X-Payment-Recipient': CONFIG.routerAddress,
    },
    body: {
      paymentId,
      message: 'Pay with USDC on Solana to continue',
      chain: 'solana',
      amount: price,
    },
  };
}

// --- Endpoints ---

// Register an agent on Solana
app.post('/solana/register', (req, res) => {
  const { name, skillHash, paymentProof } = req.body;

  if (!paymentProof) {
    return res.status(402).json(challenge402(req, '0.01'));
  }

  // Verify payment
  if (!verifyPayment(paymentProof)) {
    return res.status(402).json({ error: 'Invalid or expired payment' });
  }

  // Would call Solana AgentRegistry.registerAgent() here
  const agentId = ethers.hexlify(ethers.randomBytes(4));

  res.json({
    status: 'agent_registered',
    agentId,
    chain: 'solana',
    network: 'solana-devnet',
    receipt: generateReceipt(paymentProof, `register:${agentId}`),
  });
});

// Create a job on Solana via JobEscrow
app.post('/solana/job', (req, res) => {
  const { agent, deadline, description, paymentProof } = req.body;

  if (!paymentProof) {
    return res.status(402).json(challenge402(req, '0.05'));
  }

  if (!verifyPayment(paymentProof)) {
    return res.status(402).json({ error: 'Invalid or expired payment' });
  }

  // Would call Solana JobEscrow.createJob() here
  const jobId = ethers.hexlify(ethers.randomBytes(4));

  res.json({
    status: 'job_created',
    jobId,
    chain: 'solana',
    escrow: CONFIG.routerAddress,
    receipt: generateReceipt(paymentProof, `createJob:${jobId}`),
  });
});

// Check agent reputation
app.get('/solana/agent/:id', (req, res) => {
  // Would query Solana AgentRegistry.getAgent() here
  res.json({
    agentId: req.params.id,
    name: 'Example Agent',
    reputation: 7500, // 75/100
    totalJobs: 12,
    chain: 'solana',
  });
});

// --- Helpers ---

function verifyPayment(proof) {
  if (!proof || !proof.paymentId) return false;
  const pending = pendingPayments.get(proof.paymentId);
  if (!pending) return false;
  if (Date.now() > pending.expiresAt) {
    pendingPayments.delete(proof.paymentId);
    return false;
  }
  pendingPayments.delete(proof.paymentId);
  return true;
}

function generateReceipt(proof, action) {
  return {
    receiptId: 'rct_sol_' + crypto.randomBytes(8).toString('hex'),
    paymentId: proof.paymentId,
    action,
    timestamp: Date.now(),
    chain: 'solana',
    verifier: CONFIG.routerAddress,
  };
}

app.listen(CONFIG.port, () => {
  console.log(`Solana x402 Gateway running on port ${CONFIG.port}`);
  console.log(`USDC Mint: ${CONFIG.usdcMint}`);
  console.log(`Router: ${CONFIG.routerAddress}`);
});
