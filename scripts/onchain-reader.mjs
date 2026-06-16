#!/usr/bin/env node
/**
 * On-Chain LP Position Reader (LFJ V2.1)
 * 
 * Reads live wallet + LP position data directly from Avalanche blockchain.
 * Uses LFJ SDK ABIs + viem for contract reads. DexScreener for price data.
 * 
 * Part of the GenTech Agent Kit — universal LP position template.
 * 
 * Usage:
 *   node reader.mjs --wallet 0xYourAddress
 *   node reader.mjs --wallet 0xYourAddress --json
 *   node reader.mjs --wallet 0xYourAddress --output /path/to/data.json
 */

import { createPublicClient, http, formatUnits } from 'viem';
import { avalanche } from 'viem/chains';
import sdkV2 from '@traderjoe-xyz/sdk-v2';
import { writeFileSync } from 'fs';

const { LBPairV21ABI } = sdkV2;

// ============================================================
// CONFIG
// ============================================================

const WALLET = process.argv.find((a, i) => process.argv[i - 1] === '--wallet')
  || '0x7ebff188f2Eba16518C02864589b1403a5d1296a';
const JSON_OUTPUT = process.argv.includes('--json');
const OUTPUT_PATH = process.argv.find((a, i) => process.argv[i - 1] === '--output')
  || '/root/vaults/gentech/defi-data.json';

const POOL_ADDRESS = '0x864d4e5ee7318e97483db7eb0912e09f161516ea';
const WAVAX_ADDR = '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7';
const USDC_ADDR = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E';

const MILESTONES = {
  Scout: 5, Raider: 20, Warlord: 55, Fisher: 100, Sovereign: 200,
};

// ============================================================
// CLIENT
// ============================================================

const client = createPublicClient({
  chain: avalanche,
  transport: http('https://api.avax.network/ext/bc/C/rpc'),
});

// ============================================================
// ERC-20 + NATIVE BALANCES
// ============================================================

const ERC20_ABI = [
  { name: 'balanceOf', type: 'function', inputs: [{ name: 'account', type: 'address' }], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
  { name: 'decimals', type: 'function', inputs: [], outputs: [{ type: 'uint8' }], stateMutability: 'view' },
];

async function getTokenBalance(tokenAddr, wallet, decimals) {
  try {
    const bal = await client.readContract({
      address: tokenAddr, abi: ERC20_ABI, functionName: 'balanceOf', args: [wallet],
    });
    return Number(formatUnits(bal, decimals));
  } catch { return 0; }
}

async function getNativeBalance(wallet) {
  return Number(formatUnits(await client.getBalance({ address: wallet }), 18));
}

// ============================================================
// PRICE (DexScreener — Free)
// ============================================================

async function fetchPrice() {
  try {
    const resp = await fetch(
      `https://api.dexscreener.com/latest/dex/pairs/avalanche/${POOL_ADDRESS}`,
      { headers: { 'User-Agent': 'GenTech/1.0' } }
    );
    const data = await resp.json();
    const p = data.pairs?.[0];
    if (!p) return null;
    return {
      price: parseFloat(p.priceNative || 0),
      priceUsd: parseFloat(p.priceUsd || 0),
      change24h: parseFloat(p.priceChange?.h24 || 0),
      volume24h: parseFloat(p.volume?.h24 || 0),
      liquidity: parseFloat(p.liquidity?.usd || 0),
      txns24h: p.txns?.h24 || {},
    };
  } catch { return null; }
}

// ============================================================
// LFJ LP POSITION
// ============================================================

async function readPosition(wallet, poolAddr) {
  console.log('📊 Reading LFJ V2.1 pool...');

  // 1. Pool metadata
  const meta = await client.multicall({
    contracts: [
      { address: poolAddr, abi: LBPairV21ABI, functionName: 'getReserves' },
      { address: poolAddr, abi: LBPairV21ABI, functionName: 'getActiveId' },
      { address: poolAddr, abi: LBPairV21ABI, functionName: 'getBinStep' },
      { address: poolAddr, abi: LBPairV21ABI, functionName: 'getTokenX' },
      { address: poolAddr, abi: LBPairV21ABI, functionName: 'getTokenY' },
    ],
  });

  const reserveX = meta[0].result ? Number(formatUnits(meta[0].result[0], 18)) : 0;
  const reserveY = meta[0].result ? Number(formatUnits(meta[0].result[1], 6)) : 0;
  const activeId = meta[1].result ? Number(meta[1].result) : 0;
  const binStep = meta[2].result ? Number(meta[2].result) : 0;
  const tokenX = meta[3].result;
  const tokenY = meta[4].result;

  // Price from bin: price = (1 + binStep/10000)^(activeId - 2^23)
  const price = Math.pow(1 + binStep / 10000, activeId - 8388608);

  console.log(`   Active bin: ${activeId} | Step: ${binStep} bps | Price: ${price.toFixed(4)}`);
  console.log(`   Pool: ${reserveX.toFixed(2)} WAVAX / ${reserveY.toFixed(2)} USDC`);

  // 2. Find wallet's bins (scan ±200 around active)
  const found = [];
  const scanStart = activeId - 200;
  const scanEnd = activeId + 200;

  for (let binId = scanStart; binId <= scanEnd; binId++) {
    try {
      const bal = await client.readContract({
        address: poolAddr, abi: LBPairV21ABI,
        functionName: 'balanceOf', args: [wallet, BigInt(binId)],
      });
      if (bal > 0n) found.push({ binId, liquidity: bal });
    } catch {}
  }

  if (found.length === 0) {
    console.log('   ⚠ No LP position found in scan range');
    return { activeId, binStep, price, reserveX, reserveY, bins: [], totalWavax: 0, totalUsdc: 0 };
  }

  console.log(`   Found ${found.length} bins (${found[0].binId}–${found[found.length - 1].binId})`);

  // 3. Calculate actual token amounts (share of each bin)
  let totalWavax = 0;
  let totalUsdc = 0;

  // Batch: get totalSupply + bin reserves for each bin
  const calls = found.flatMap(b => [
    { address: poolAddr, abi: LBPairV21ABI, functionName: 'totalSupply', args: [BigInt(b.binId)] },
    { address: poolAddr, abi: LBPairV21ABI, functionName: 'getBin', args: [BigInt(b.binId)] },
  ]);

  const results = await client.multicall({ contracts: calls });

  for (let i = 0; i < found.length; i++) {
    const totalSupply = results[i * 2].result;
    const binReserves = results[i * 2 + 1].result;

    if (totalSupply > 0n && binReserves) {
      const share = Number(found[i].liquidity) / Number(totalSupply);
      // binReserves is [uint128 reserveX, uint128 reserveY]
      const binX = Number(binReserves[0]);
      const binY = Number(binReserves[1]);
      totalWavax += share * binX / 1e18;
      totalUsdc += share * binY / 1e6;
    }
  }

  return {
    activeId, binStep, price, reserveX, reserveY,
    bins: found.map(b => ({ binId: b.binId, liquidity: b.liquidity.toString() })),
    totalBins: found.length,
    binRange: [found[0].binId, found[found.length - 1].binId],
    totalWavax, totalUsdc,
  };
}

// ============================================================
// DASHBOARD DATA WRITER
// ============================================================

function writeDashboard(balances, price, position) {
  const now = new Date().toISOString();
  const avaxPrice = price?.priceUsd || 0;
  const liquidValue = balances.avax * avaxPrice + balances.usdc;
  const lpValue = (position?.totalWavax || 0) * avaxPrice + (position?.totalUsdc || 0);
  const totalValue = liquidValue + lpValue;

  let milestone = 'None';
  for (const [name, threshold] of Object.entries(MILESTONES).sort((a, b) => a[1] - b[1])) {
    if (lpValue >= threshold) milestone = name;
  }

  const data = {
    lastUpdated: now,
    dataSource: 'onchain-live',
    pool: 'AVAX/USDC',
    chain: 'Avalanche',
    dex: 'LFJ V2.1',
    wallet: WALLET,
    currentPrice: avaxPrice,
    priceChange24h: price?.change24h || 0,
    volume24h: price?.volume24h || 0,
    liquidity: price?.liquidity || 0,
    walletBalances: {
      avax: balances.avax,
      wavax: balances.wavax,
      usdc: balances.usdc,
      liquidUsd: +liquidValue.toFixed(2),
    },
    lpPosition: position ? {
      activeBin: position.activeId,
      binStep: position.binStep,
      binRange: position.binRange,
      totalBins: position.totalBins,
      wavax: +position.totalWavax.toFixed(6),
      usdc: +position.totalUsdc.toFixed(6),
      totalValueUsd: +lpValue.toFixed(2),
      poolReserveX: +position.reserveX.toFixed(2),
      poolReserveY: +position.reserveY.toFixed(2),
    } : null,
    totalValueUsd: +totalValue.toFixed(2),
    milestone,
    milestones: MILESTONES,
  };

  writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2));
  console.log(`\n✅ Written to ${OUTPUT_PATH}`);
  return data;
}

// ============================================================
// MAIN
// ============================================================

async function main() {
  console.log('🔗 On-Chain LP Position Reader');
  console.log(`   Wallet: ${WALLET}`);
  console.log(`   Pool: ${POOL_ADDRESS}\n`);

  // Parallel reads
  const [avax, wavax, usdc, price] = await Promise.all([
    getNativeBalance(WALLET),
    getTokenBalance(WAVAX_ADDR, WALLET, 18),
    getTokenBalance(USDC_ADDR, WALLET, 6),
    fetchPrice(),
  ]);

  console.log('💰 Wallet:', `AVAX=${avax.toFixed(4)}`, `WAVAX=${wavax.toFixed(6)}`, `USDC=${usdc.toFixed(6)}`);
  if (price) console.log('📈 Price:', `$${price.priceUsd.toFixed(4)}`, `${price.change24h >= 0 ? '+' : ''}${price.change24h.toFixed(2)}%`);

  const position = await readPosition(WALLET, POOL_ADDRESS);

  // Summary
  const avaxVal = avax * (price?.priceUsd || 0);
  const lpWavaxVal = (position?.totalWavax || 0) * (price?.priceUsd || 0);
  const lpUsdcVal = position?.totalUsdc || 0;
  const lpTotal = lpWavaxVal + lpUsdcVal;

  console.log(`\n${'═'.repeat(44)}`);
  console.log(`📊 POSITION SUMMARY`);
  console.log(`${'═'.repeat(44)}`);
  console.log(`Liquid:  ${avax.toFixed(4)} AVAX + ${usdc.toFixed(2)} USDC = $${(avaxVal + usdc).toFixed(2)}`);
  console.log(`LP:      ${(position?.totalWavax || 0).toFixed(4)} WAVAX + ${(position?.totalUsdc || 0).toFixed(2)} USDC = $${lpTotal.toFixed(2)}`);
  console.log(`Total:   $${((avaxVal + usdc) + lpTotal).toFixed(2)}`);
  console.log(`Bins:    ${position?.totalBins || 0} active (${position?.binRange?.[0] || '?'}–${position?.binRange?.[1] || '?'})`);
  console.log(`${'═'.repeat(44)}`);

  if (JSON_OUTPUT) {
    console.log(JSON.stringify({ balances: { avax, wavax, usdc }, price, position }, null, 2));
  } else {
    writeDashboard({ avax, wavax, usdc }, price, position);
  }
}

main().catch(console.error);
