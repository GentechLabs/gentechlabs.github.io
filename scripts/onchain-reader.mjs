#!/usr/bin/env node
/**
 * On-Chain LP Position Reader (LFJ V2.1)
 * Reads live wallet + LP position from Avalanche blockchain.
 * Outputs dashboard-compatible defi-data.json with curve data.
 */

import { createPublicClient, http, formatUnits } from 'viem';
import { avalanche } from 'viem/chains';
import sdkV2 from '@traderjoe-xyz/sdk-v2';
import { writeFileSync, existsSync, readFileSync } from 'fs';

const { LBPairV21ABI, Bin } = sdkV2;

// Config
const WALLET = process.argv.find((a, i) => process.argv[i - 1] === '--wallet')
  || process.env.WALLET
  || '';
const OUTPUT_PATH = process.argv.find((a, i) => process.argv[i - 1] === '--output')
  || process.env.OUTPUT_PATH
  || '/root/ProtoJay4789.github.io/DeFi/defi-data.json';
const SHAPE = (process.argv.find((a, i) => process.argv[i - 1] === '--shape')
  || process.env.SHAPE
  || 'bid-ask').toLowerCase();

const POOL = '0x864d4e5ee7318e97483db7eb0912e09f161516ea';
const WAVAX_ADDR = '0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7';
const USDC_ADDR = '0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E';

const MILESTONES = [
  { tier: 1, label: 'Scout', daily_fees: 5.0, description: 'Entry strategies (CURVE)' },
  { tier: 2, label: 'Raider', daily_fees: 20.0, description: 'SPOT + BIDIRECTIONAL shapes' },
  { tier: 3, label: 'Warlord', daily_fees: 50.0, description: 'Multi-pool positions' },
  { tier: 4, label: 'Sovereign', daily_fees: 100.0, description: 'Custom strategy creation + mentorship' },
];

const SHAPE_LABELS = {
  'bid-ask': 'Bid-Ask',
  'bidirectional': 'Bidirectional',
  'curve': 'Curve',
  'spot': 'Spot',
  'uniform': 'Uniform',
};
const DISPLAY_SHAPE = SHAPE_LABELS[SHAPE] || 'Bid-Ask';

// Viem client
const client = createPublicClient({
  chain: avalanche,
  transport: http('https://api.avax.network/ext/bc/C/rpc'),
});

// ─── Helpers ───

const ERC20 = [
  { name: 'balanceOf', type: 'function', inputs: [{ name: 'a', type: 'address' }], outputs: [{ type: 'uint256' }], stateMutability: 'view' },
  { name: 'decimals', type: 'function', inputs: [], outputs: [{ type: 'uint8' }], stateMutability: 'view' },
];

function getArg(flag) {
  const idx = process.argv.indexOf(flag);
  return idx !== -1 && process.argv[idx + 1] ? process.argv[idx + 1] : undefined;
}

async function tokenBal(addr, wallet, dec) {
  try { return Number(formatUnits(await client.readContract({ address: addr, abi: ERC20, functionName: 'balanceOf', args: [wallet] }), dec)); }
  catch { return 0; }
}

async function tokenDecimals(addr) {
  try { return Number(await client.readContract({ address: addr, abi: ERC20, functionName: 'decimals' })); }
  catch { return 18; }
}

async function price() {
  try {
    const r = await fetch(`https://api.dexscreener.com/latest/dex/pairs/avalanche/${POOL}`, { headers: { 'User-Agent': 'GenTech/1.0' } });
    const d = await r.json(); const p = d.pairs?.[0];
    return p ? { price: +p.priceNative, priceUsd: +p.priceUsd, change24h: +(p.priceChange?.h24||0), volume24h: +(p.volume?.h24||0), liquidity: +(p.liquidity?.usd||0) } : null;
  } catch { return null; }
}

function loadPreviousData() {
  try {
    if (existsSync(OUTPUT_PATH)) {
      return JSON.parse(readFileSync(OUTPUT_PATH, 'utf8'));
    }
  } catch (e) {
    console.warn('[Reader] Could not load previous data:', e.message);
  }
  return null;
}

// ─── Position Reader ───

async function readPosition(wallet, pxData) {
  const meta = await client.multicall({
    contracts: [
      { address: POOL, abi: LBPairV21ABI, functionName: 'getReserves' },
      { address: POOL, abi: LBPairV21ABI, functionName: 'getActiveId' },
      { address: POOL, abi: LBPairV21ABI, functionName: 'getBinStep' },
      { address: POOL, abi: LBPairV21ABI, functionName: 'tokenX' },
      { address: POOL, abi: LBPairV21ABI, functionName: 'tokenY' },
    ],
  });

  const reserveX = meta[0].result ? Number(formatUnits(meta[0].result[0], 18)) : 0;
  const reserveY = meta[0].result ? Number(formatUnits(meta[0].result[1], 6)) : 0;
  const activeId = meta[1].result ? Number(meta[1].result) : 0;
  const binStep = meta[2].result ? Number(meta[2].result) : 10;
  const tokenXAddr = meta[3].result || WAVAX_ADDR;
  const tokenYAddr = meta[4].result || USDC_ADDR;

  const [decX, decY] = await Promise.all([
    tokenDecimals(tokenXAddr),
    tokenDecimals(tokenYAddr),
  ]);

  // Price scale: raw ratio -> human USD price
  const priceScale = 10 ** (decX - decY);
  const binPriceUsd = (id) => Bin.getPriceFromId(id, binStep) * priceScale;

  // Scan ±200 bins for wallet's liquidity
  const found = [];
  for (let id = activeId - 200; id <= activeId + 200; id++) {
    try {
      const bal = await client.readContract({ address: POOL, abi: LBPairV21ABI, functionName: 'balanceOf', args: [wallet, BigInt(id)] });
      if (bal > 0n) found.push({ id, liquidity: bal });
    } catch {}
  }

  if (found.length === 0) return { activeId, binStep, totalWavax: 0, totalUsdc: 0, bins: [], curveData: null, tokenXAddr, tokenYAddr, decX, decY };

  // Get totalSupply + bin reserves for each bin
  const calls = found.flatMap(b => [
    { address: POOL, abi: LBPairV21ABI, functionName: 'totalSupply', args: [BigInt(b.id)] },
    { address: POOL, abi: LBPairV21ABI, functionName: 'getBin', args: [BigInt(b.id)] },
  ]);
  const results = await client.multicall({ contracts: calls });

  // Build curve data from ACTUAL bin prices
  const binPrices = [];
  let totalWavax = 0, totalUsdc = 0;
  for (let i = 0; i < found.length; i++) {
    const ts = results[i*2].result;
    const bd = results[i*2+1].result;
    if (ts > 0n && bd) {
      const share = Number(found[i].liquidity) / Number(ts);
      const wx = share * Number(bd[0]) / (10 ** decX);
      const uy = share * Number(bd[1]) / (10 ** decY);
      totalWavax += wx;
      totalUsdc += uy;
      const binPrice = binPriceUsd(found[i].id);
      const depth = wx * (pxData?.priceUsd || binPrice) + uy; // USD value in this bin
      binPrices.push({ price: binPrice, depth, id: found[i].id });
    }
  }

  // Actual range is min/max of bins that contain liquidity
  const actualPrices = binPrices.map(b => b.price);
  const rangeMin = Math.min(...actualPrices);
  const rangeMax = Math.max(...actualPrices);

  // Normalize depth to 0-1
  const maxDepth = Math.max(...binPrices.map(b => b.depth), 0.01);
  const curveBins = binPrices
    .map(b => ({ price: +b.price.toFixed(4), depth: b.depth / maxDepth, id: b.id }))
    .sort((a, b) => a.price - b.price);

  return {
    activeId, binStep, totalWavax, totalUsdc,
    bins: found.map(b => ({ binId: b.id, liquidity: b.liquidity.toString() })),
    totalBins: found.length,
    binRange: [found[0].id, found[found.length - 1].id],
    rangeMin: +rangeMin.toFixed(4),
    rangeMax: +rangeMax.toFixed(4),
    tokenXAddr, tokenYAddr, decX, decY,
    curveData: {
      currentPrice: pxData?.priceUsd || binPriceUsd(activeId),
      rangeMin: +rangeMin.toFixed(4),
      rangeMax: +rangeMax.toFixed(4),
      bins: curveBins,
    },
  };
}

// ─── Main ───

async function main() {
  if (!WALLET) {
    console.error('❌ No wallet provided. Use --wallet <address> or set WALLET env var.');
    process.exit(1);
  }

  console.log(`🔗 On-Chain Reader | Wallet: ${WALLET.slice(0, 6)}...${WALLET.slice(-4)} | Shape: ${DISPLAY_SHAPE}`);

  const [avax, wavax, usdc, px] = await Promise.all([
    client.getBalance({ address: WALLET }).then(b => Number(formatUnits(b, 18))),
    tokenBal(WAVAX_ADDR, WALLET, 18),
    tokenBal(USDC_ADDR, WALLET, 6),
    price(),
  ]);

  const pos = await readPosition(WALLET, px);
  const avaxPrice = px?.priceUsd || 0;

  // Build dashboard-compatible output
  const liquidValue = avax * avaxPrice + usdc;
  const lpValue = pos.totalWavax * avaxPrice + pos.totalUsdc;
  const totalValue = liquidValue + lpValue;
  const now = new Date();

  // Actual range from on-chain bins
  const rangeLow = pos.rangeMin || 0;
  const rangeHigh = pos.rangeMax || 0;
  const rangeMid = (rangeLow + rangeHigh) / 2;
  const rangeWidth = rangeHigh - rangeLow;

  // Estimate daily fees from 24h volume * fee tier * user's share of pool
  const feeBps = pos.binStep || 10; // V2.1: fee = binStep in bps
  const poolTvl = px?.liquidity || (pos.totalWavax * avaxPrice + pos.totalUsdc) / 0.0001;
  const estimatedDailyFees = poolTvl > 0 && px?.volume24h
    ? px.volume24h * (feeBps / 10000) * (lpValue / poolTvl)
    : 0.16;
  const dailyFees = +estimatedDailyFees.toFixed(3);

  // Persist cumulative fees across runs (add prorated daily fees since last update)
  const prev = loadPreviousData();
  let cumulativeFees = prev?.fees?.cumulativeFees || 0;
  if (prev?.lastUpdated) {
    const hoursSince = Math.max(0, (Date.now() - new Date(prev.lastUpdated).getTime()) / 3600000);
    cumulativeFees += dailyFees * (hoursSince / 24);
  }
  cumulativeFees = +cumulativeFees.toFixed(4);

  // Efficiency: how close is current price to the CENTER of the ACTUAL position range
  const distFromCenter = rangeWidth > 0 ? Math.abs(avaxPrice - rangeMid) / (rangeWidth / 2) : 0;
  const efficiency = Math.max(0, Math.min(100, Math.round((1 - distFromCenter) * 100)));

  const inRange = pos.totalBins > 0 && avaxPrice >= rangeLow && avaxPrice <= rangeHigh;

  // Fee milestones with tiers array — based on DAILY FEES like old AAE system
  const tierIcons = ['🔭', '⚔️', '👑', '🏰'];
  const tierUnlocks = [
    'Entry strategies (CURVE)',
    'SPOT + BIDIRECTIONAL shapes',
    'Multi-pool positions',
    'Custom strategy creation + mentorship',
  ];
  const tiers = MILESTONES.map((ms, i) => ({
    tier: ms.tier,
    icon: tierIcons[i],
    label: ms.label,
    target: ms.daily_fees,
    unlocks: tierUnlocks[i],
    achieved: dailyFees >= ms.daily_fees,
  }));

  // Find current tier from daily fees
  let currentTierIdx = -1;
  for (let i = 0; i < MILESTONES.length; i++) {
    if (dailyFees >= MILESTONES[i].daily_fees) currentTierIdx = i;
    else break;
  }
  const milestone = currentTierIdx >= 0 ? MILESTONES[currentTierIdx].label : 'Unranked';
  const nextMilestone = currentTierIdx < MILESTONES.length - 1 ? MILESTONES[currentTierIdx + 1] : null;

  // Progress to next milestone
  let milestoneProgress = 0;
  if (currentTierIdx === -1) {
    milestoneProgress = MILESTONES[0].daily_fees > 0
      ? Math.round((dailyFees / MILESTONES[0].daily_fees) * 100) : 0;
  } else if (nextMilestone) {
    const currentTarget = MILESTONES[currentTierIdx].daily_fees;
    const nextTarget = nextMilestone.daily_fees;
    milestoneProgress = nextTarget > currentTarget
      ? Math.round(((dailyFees - currentTarget) / (nextTarget - currentTarget)) * 100) : 100;
  } else {
    milestoneProgress = 100;
  }

  // Rebalance suggestions based on real range + market trend
  const rebalanceSuggestions = [];
  if (!inRange) {
    rebalanceSuggestions.push({
      icon: '🚨',
      title: 'Price Out of Range',
      description: `AVAX at $${avaxPrice.toFixed(2)} is outside your $${rangeLow.toFixed(2)}-$${rangeHigh.toFixed(2)} range. You are not earning fees.`,
      priority: 'high',
      impact: 'Immediate',
      action: 'Rebalance on LFJ',
    });
  } else if (efficiency < 50) {
    rebalanceSuggestions.push({
      icon: '⚠️',
      title: 'Price Near Edge',
      description: `Price is near the edge of your range (${efficiency}% efficiency). Consider narrowing or recentering.`,
      priority: 'medium',
      impact: 'Moderate',
      action: 'Review Range',
    });
  }
  const trend = px?.change24h > 2 ? 'bullish' : px?.change24h < -2 ? 'bearish' : 'neutral';
  if (trend === 'bullish' && avaxPrice < rangeHigh) {
    rebalanceSuggestions.push({
      icon: '📈',
      title: 'Bullish Momentum',
      description: 'AVAX is up 24h. Consider shifting range slightly higher to capture upside.',
      priority: 'low',
      impact: 'Opportunity',
      action: 'Adjust Up',
    });
  } else if (trend === 'bearish' && avaxPrice > rangeLow) {
    rebalanceSuggestions.push({
      icon: '📉',
      title: 'Bearish Pressure',
      description: 'AVAX is down 24h. Widen range or shift lower to avoid going out of range.',
      priority: 'low',
      impact: 'Risk',
      action: 'Adjust Down',
    });
  }
  if (rebalanceSuggestions.length === 0) {
    rebalanceSuggestions.push({
      icon: '✅',
      title: 'Position Healthy',
      description: 'Price is in range and efficiency is good. No action needed.',
      priority: 'low',
      impact: 'None',
      action: null,
    });
  }

  // Recent activity (placeholder until event scanning is implemented)
  const todayStr = now.toISOString().split('T')[0];
  const transactions = (prev?.transactions || [])
    .map(t => ({ ...t, date: String(t.date || '').split('T')[0] }))
    .filter(t => t.date !== todayStr)
    .slice(0, 4);
  transactions.unshift({
    date: todayStr,
    type: 'Snapshot',
    token: 'AVAX/USDC',
    amount: `${pos.totalWavax.toFixed(4)} WAVAX + ${pos.totalUsdc.toFixed(2)} USDC`,
    usd: lpValue.toFixed(2),
    status: inRange ? 'In Range' : 'Out of Range',
  });
  if (transactions.length > 5) transactions.length = 5;

  // News placeholder (can be replaced with RSS/API feed later)
  const news = [
    {
      headline: `AVAX ${px?.change24h >= 0 ? 'up' : 'down'} ${Math.abs(px?.change24h || 0).toFixed(2)}% in 24h`,
      impact: px?.change24h >= 0 ? 'bullish' : 'bearish',
      relevance: 'high',
    },
    {
      headline: `LFJ AVAX/USDC pool volume: $${((px?.volume24h || 0) / 1000).toFixed(1)}K`,
      impact: 'neutral',
      relevance: 'medium',
    },
  ];

  const data = {
    lastUpdated: now.toISOString(),
    pool: 'AVAX/USDC',
    chain: 'Avalanche',
    dex: 'LFJ',
    currentPrice: avaxPrice,
    priceChange24h: px?.change24h || 0,
    volume24h: px?.volume24h || 0,
    liquidity: px?.liquidity || 0,
    lpPosition: {
      pair: 'AVAX/USDC',
      feeTier: `${pos.binStep}bps`,
      shape: SHAPE,
      displayShape: DISPLAY_SHAPE,
      currentPrice: avaxPrice,
      rangeMin: +rangeLow.toFixed(4),
      rangeMax: +rangeHigh.toFixed(4),
      avaxAmount: +pos.totalWavax.toFixed(6),
      usdcAmount: +pos.totalUsdc.toFixed(6),
      totalValue: +lpValue.toFixed(2),
      totalValueUSD: +lpValue.toFixed(2),
      activeBin: pos.activeId,
      binStep: pos.binStep,
      totalBins: pos.totalBins,
    },
    fees: {
      dailyFees,
      cumulativeFees,
      feeCurrency: 'USD',
    },
    efficiency,
    hero: {
      positionUsd: +lpValue.toFixed(2),
      dailyFees,
      efficiency,
      efficiencyZone: efficiency >= 70 ? 'Center' : efficiency >= 50 ? 'Inner' : 'Outer',
      shape: DISPLAY_SHAPE,
      rangeStatus: inRange ? 'In Range' : 'Out of Range',
      currentPrice: avaxPrice,
      rangeMin: +rangeLow.toFixed(4),
      rangeMax: +rangeHigh.toFixed(4),
      milestoneNext: nextMilestone ? nextMilestone.label : 'Max',
      milestoneTarget: nextMilestone ? nextMilestone.daily_fees : 100,
      milestoneProgress,
    },
    marketIntel: {
      avaxPrice,
      change24h: px?.change24h || 0,
      volume24h: px?.volume24h || 0,
      tvl: px?.liquidity || 0,
      trend,
      news,
    },
    strategyAdvisor: {
      efficiency,
      efficiencyZone: efficiency >= 70 ? 'Center' : efficiency >= 50 ? 'Inner' : 'Outer',
      recommendedAction: inRange ? 'Hold' : 'Rebalance',
      dcaType: efficiency >= 70 ? 'Full DCA' : efficiency >= 50 ? 'Moderate DCA' : 'Micro-DCA',
      dcaDetails: `${efficiency >= 70 ? 'Full' : efficiency >= 50 ? 'Moderate' : 'Micro'} DCA — ${inRange ? 'price in range' : 'rebalance needed'}`,
      rebalanceTrigger: `Price exits $${rangeLow.toFixed(2)}-$${rangeHigh.toFixed(2)} range`,
      compoundThreshold: 50,
      cumulativeFees,
      nextCompound: `$${Math.max(0, 50 - cumulativeFees).toFixed(2)} away from first compound`,
      riskLevel: inRange ? (efficiency >= 70 ? 'Low' : efficiency >= 50 ? 'Medium' : 'High') : 'Critical',
      riskNote: inRange
        ? `Price at $${avaxPrice.toFixed(2)}, ${efficiency}% efficiency`
        : 'Out of range — rebalance needed',
      shape: DISPLAY_SHAPE,
    },
    milestones: MILESTONES.reduce((acc, ms) => { acc[ms.label] = ms.daily_fees; return acc; }, {}),
    feeMilestones: {
      currentDailyFees: dailyFees,
      cumulativeFees,
      positionUsd: +lpValue.toFixed(2),
      daysActive: 1,
      nextMilestone: nextMilestone ? nextMilestone.label : 'Max',
      nextTarget: nextMilestone ? nextMilestone.daily_fees : 100,
      progress: milestoneProgress,
      tiers,
    },
    curveData: pos.curveData,
    walletBalances: { avax, wavax, usdc, liquidUsd: +liquidValue.toFixed(2) },
    supportResistance: {
      currentPrice: avaxPrice,
      levels: [
        { price: +rangeHigh.toFixed(2), type: 'resistance', strength: 'strong', label: 'Range High', note: 'Current position top' },
        { price: +(rangeHigh + rangeWidth * 0.2).toFixed(2), type: 'resistance', strength: 'weak', label: 'Minor Resistance', note: 'Local high' },
        { price: +rangeLow.toFixed(2), type: 'support', strength: 'strong', label: 'Range Low', note: 'Current position bottom' },
        { price: +(rangeLow - rangeWidth * 0.2).toFixed(2), type: 'support', strength: 'weak', label: 'Minor Support', note: 'Local low' },
      ],
      shapeRecommendation: {
        shape: DISPLAY_SHAPE,
        reason: `Price at $${avaxPrice.toFixed(2)}, ${inRange ? 'within' : 'outside'} $${rangeLow.toFixed(2)}-$${rangeHigh.toFixed(2)} range.`,
        optimalRange: [+rangeLow.toFixed(2), +rangeHigh.toFixed(2)],
      },
      proximityAlert: inRange
        ? `Price ${((avaxPrice - rangeLow) / rangeWidth * 100).toFixed(0)}% into range`
        : `⚠️ Price out of range`,
    },
    rebalanceSuggestions: {
      efficiency,
      price: avaxPrice,
      rangeMin: +rangeLow.toFixed(2),
      rangeMax: +rangeHigh.toFixed(2),
      volatility: Math.abs(px?.change24h || 0),
      trend,
      suggestions: rebalanceSuggestions,
    },
    transactions,
  };

  writeFileSync(OUTPUT_PATH, JSON.stringify(data, null, 2));
  console.log(`✅ Written to ${OUTPUT_PATH}`);
  console.log(`   LP: ${pos.totalWavax.toFixed(4)} WAVAX + ${pos.totalUsdc.toFixed(2)} USDC = $${lpValue.toFixed(2)}`);
  console.log(`   Total: $${totalValue.toFixed(2)} | Milestone: ${milestone} (${milestoneProgress}%)`);
  console.log(`   Bins: ${pos.totalBins} active | Range: $${rangeLow.toFixed(2)}-$${rangeHigh.toFixed(2)} | Status: ${inRange ? 'In Range' : 'Out of Range'}`);
  console.log(`   Est. daily fees: $${dailyFees.toFixed(3)} | Cumulative: $${cumulativeFees.toFixed(4)}`);
}

main().catch(console.error);
