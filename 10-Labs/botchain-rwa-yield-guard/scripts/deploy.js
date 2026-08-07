// Deploy the RWA Yield Guard Agent to BOT Chain.
// Usage: npx hardhat run scripts/deploy.js --network botTestnet|botMainnet
const hre = require("hardhat");

async function main() {
  // The AI decision layer operator address (off-chain agent that signs intents).
  // For the challenge demo, this is the deployer; in production it's the agent's
  // dedicated wallet.
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying RWA Yield Guard with account:", deployer.address);

  const RWAYieldGuard = await hre.ethers.getContractFactory("RWAYieldGuard");
  const guard = await RWAYieldGuard.deploy(deployer.address);
  await guard.waitForDeployment();

  const addr = await guard.getAddress();
  console.log("RWAYieldGuard deployed to:", addr);
  console.log("Network:", hre.network.name, "| chainId:", hre.network.config.chainId);

  // Verify on BOTScan if a verifier is configured
  if (hre.network.name === "botMainnet" || hre.network.name === "botTestnet") {
    console.log("To verify: npx hardhat verify --network", hre.network.name, addr);
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
