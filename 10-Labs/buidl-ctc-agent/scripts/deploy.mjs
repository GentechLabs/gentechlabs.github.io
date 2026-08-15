import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying VerifiedRebalance with account:", deployer.address);

  const VerifiedRebalance = await ethers.getContractFactory("VerifiedRebalance");
  const contract = await VerifiedRebalance.deploy();
  await contract.waitForDeployment();

  const addr = await contract.getAddress();
  console.log("✅ VerifiedRebalance deployed at:", addr);
  console.log("   Explorer: https://scan.creditcoin.network/address/" + addr);
}

main().catch((e) => {
  console.error("❌ Deploy error:", e.message);
  process.exit(1);
});
