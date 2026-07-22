// Test x402 Verification Logic
// This file demonstrates how to test the payment verification locally

import { verifyPaymentOnChain, getX402Requirements } from './x402-verification.js';

// Mock Cloudflare environment (for testing without KV)
const mockEnv = {
  NONCE_STORE: null // KV not available for local test
};

// Example test cases
async function testX402Verification() {
  console.log('=== x402 Verification Tests ===\n');

  // Test 1: Invalid format
  const invalidProof = {
    signature: 'invalid',
    sender: '0x123',
    timestamp: Math.floor(Date.now() / 1000),
    amount: '0.005',
    nonce: 'test-1'
  };

  const result1 = await verifyPaymentOnChain(invalidProof, 0.005, mockEnv);
  console.log('Test 1 - Invalid format:', result1.valid ? '✅ PASS' : '❌ FAIL', result1.error);

  // Test 2: Expired timestamp
  const expiredProof = {
    signature: '0x123abc...',
    sender: '0x456def...',
    timestamp: Math.floor(Date.now() / 1000) - 1000, // 1000 seconds ago
    amount: '0.005',
    nonce: 'test-2'
  };

  const result2 = await verifyPaymentOnChain(expiredProof, 0.005, mockEnv);
  console.log('Test 2 - Expired timestamp:', !result2.valid ? '✅ PASS' : '❌ FAIL', result2.error);

  // Test 3: Valid format (but no real transaction)
  const validFormatProof = {
    signature: '0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
    sender: '0x7EBff1DbD34172C5b55697654006C9642b5236a3',
    timestamp: Math.floor(Date.now() / 1000),
    amount: '0.005',
    nonce: 'test-3-real-tx'
  };

  const result3 = await verifyPaymentOnChain(validFormatProof, 0.005, mockEnv);
  console.log('Test 3 - Valid format (no tx):', !result3.valid ? '✅ PASS' : '❌ FAIL', result3.error?.substring(0, 50));

  // Test 4: Get x402 requirements
  const requirements = getX402Requirements('/v1/games/search');
  console.log('\nTest 4 - x402 Requirements:');
  console.log('  Amount:', requirements.amount, 'USDC');
  console.log('  Payment Address:', requirements.paymentAddress);
  console.log('  USDC Contract:', requirements.usdcContract);

  console.log('\n=== All Tests Complete ===');
}

// Run tests (commented out - only for local testing)
// testX402Verification();

export { testX402Verification };