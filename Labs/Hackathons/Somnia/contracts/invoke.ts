import * as hre from "hardhat";
import { formatEther } from "viem";

// Set via env: CATCHER_ADDRESS=0x... or hardcode after deployment
const CONTRACT_ADDRESS = (process.env.CATCHER_ADDRESS || "SET_DEPLOYED_ADDRESS") as `0x${string}`;
const POLL_INTERVAL = 5000;
const TIMEOUT = 180_000; // 3 min for dual-agent chain

async function main() {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.log("Usage: npx hardhat run contracts/invoke.ts --network somnia -- <tokenAddress> <chainId>");
    console.log("Example: npx hardhat run contracts/invoke.ts --network somnia -- 0x... 1");
    process.exit(1);
  }

  const [tokenAddress, chainIdStr] = args;
  const chainId = parseInt(chainIdStr, 10);

  console.log(`Requesting analysis for ${tokenAddress} (chain ${chainId})...`);

  const catcher = await hre.viem.getContractAt("AgentCatcher", CONTRACT_ADDRESS);
  const publicClient = await hre.viem.getPublicClient();

  const deposit = await catcher.read.getRequiredDeposit();
  console.log(`Required deposit: ${formatEther(deposit)} STT`);

  // Increase deposit buffer for LLM agent (dual-agent = 2 deposits needed)
  const totalDeposit = deposit * BigInt(3);
  console.log(`Using total deposit: ${formatEther(totalDeposit)} STT (3x buffer for dual-agent)`);

  const hash = await catcher.write.requestAnalysis([tokenAddress, BigInt(chainId)], { value: totalDeposit });
  console.log(`Tx hash: ${hash}`);

  const receipt = await publicClient.waitForTransactionReceipt({ hash });
  const fromBlock = receipt.blockNumber;
  console.log(`Request confirmed at block ${fromBlock}. Waiting for agent response...`);

  // Poll for callback event
  const startTime = Date.now();
  while (Date.now() - startTime < TIMEOUT) {
    const events = await catcher.getEvents.RiskScored({}, { fromBlock });
    if (events.length > 0) {
      const e = events[0].args;
      console.log("\n=== Analysis Result ===");
      console.log(`Request ID: ${e.requestId}`);
      console.log(`Token: ${e.tokenAddress}`);
      console.log(`Risk Level: ${e.riskLevel}`);
      console.log(`Risk Score: ${e.riskScore}/100`);
      console.log("========================\n");
      process.exit(0);
    }

    const fails = await catcher.getEvents.RequestFailed({}, { fromBlock });
    if (fails.length > 0) {
      console.log(`Request failed: ${fails[0].args.reason}`);
      process.exit(1);
    }

    process.stdout.write(".");
    await new Promise((r) => setTimeout(r, POLL_INTERVAL));
  }

  console.log("\nTimeout waiting for agent response");
  process.exit(1);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
