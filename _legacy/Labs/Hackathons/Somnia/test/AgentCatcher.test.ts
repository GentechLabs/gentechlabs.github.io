import { expect } from "chai";
import hre from "hardhat";
import "@nomicfoundation/hardhat-chai-matchers";
import { loadFixture } from "@nomicfoundation/hardhat-toolbox/network-helpers";

const PLATFORM = "0x037Bb9C718F3f7fe5eCBDB0b600D607b52706776";

async function deployFixture() {
  const catcher = await hre.ethers.deployContract("AgentCatcher");
  const [owner, user] = await hre.ethers.getSigners();

  await hre.network.provider.request({
    method: "hardhat_impersonateAccount",
    params: [PLATFORM],
  });
  const platformSigner = await hre.ethers.getSigner(PLATFORM);

  await owner.sendTransaction({
    to: PLATFORM as `0x${string}`,
    value: hre.ethers.parseEther("10"),
  });

  return { catcher, owner, user, platformSigner };
}

function makeRequest(id: bigint, requester: string, callback: string) {
  return {
    id,
    agentId: BigInt(0),
    requester,
    payload: "0x" as `0x${string}`,
    callbackAddress: callback,
    callbackSelector: "0x00000000" as `0x${string}`,
    deposit: BigInt(0),
    timestamp: BigInt(0),
    status: 0,
  };
}

describe("AgentCatcher", function () {
  describe("Deployment", function () {
    it("should deploy successfully", async function () {
      const { catcher } = await loadFixture(deployFixture);
      expect(await catcher.requestCount()).to.equal(BigInt(0));
    });

    it("should have correct platform address", async function () {
      const { catcher } = await loadFixture(deployFixture);
      expect(await catcher.PLATFORM()).to.equal(PLATFORM);
    });

    it("should have correct agent IDs", async function () {
      const { catcher } = await loadFixture(deployFixture);
      expect(await catcher.JSON_API_AGENT_ID()).to.equal(BigInt("13174292974160097713"));
      expect(await catcher.LLM_AGENT_ID()).to.equal(BigInt("12847293847561029384"));
    });

    it("should return risk levels array", async function () {
      const { catcher } = await loadFixture(deployFixture);
      const levels = await catcher.getRiskLevels();
      expect(levels).to.deep.equal([
        "safe",
        "low_risk",
        "moderate_risk",
        "high_risk",
        "scam",
      ]);
    });
  });

  describe("Access Control", function () {
    it("handleDataFetched: only PLATFORM can call", async function () {
      const { catcher, user } = await loadFixture(deployFixture);
      const req = makeRequest(BigInt(1), user.address, catcher.target as string);
      await expect(
        catcher.connect(user).handleDataFetched(BigInt(1), [], 0, req)
      ).to.be.revertedWith("Only platform");
    });

    it("handleClassification: only PLATFORM can call", async function () {
      const { catcher, user } = await loadFixture(deployFixture);
      const req = makeRequest(BigInt(1), user.address, catcher.target as string);
      await expect(
        catcher.connect(user).handleClassification(BigInt(1), [], 0, req)
      ).to.be.revertedWith("Only platform");
    });

    it("handleDataFetched: rejects invalid request ID", async function () {
      const { catcher, platformSigner } = await loadFixture(deployFixture);
      const req = makeRequest(BigInt(999), platformSigner.address, catcher.target as string);
      await expect(
        catcher.connect(platformSigner).handleDataFetched(BigInt(999), [], 0, req)
      ).to.be.revertedWith("Invalid request");
    });

    it("handleClassification: rejects invalid request ID", async function () {
      const { catcher, platformSigner } = await loadFixture(deployFixture);
      const req = makeRequest(BigInt(999), platformSigner.address, catcher.target as string);
      await expect(
        catcher.connect(platformSigner).handleClassification(BigInt(999), [], 0, req)
      ).to.be.revertedWith("Invalid request");
    });
  });
});
