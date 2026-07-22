import hre from "hardhat";

async function main() {
  console.log("Deploying AgentCatcher to Somnia Testnet...");

  const catcher = await hre.viem.deployContract("AgentCatcher");
  const address = catcher.address;

  console.log(`AgentCatcher deployed to: ${address}`);
  console.log(`Verify on explorer: https://shannon-explorer.somnia.network/address/${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
