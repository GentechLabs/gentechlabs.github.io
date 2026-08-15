const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("VerifiedRebalance", function () {
  let contract, owner, other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    const Factory = await ethers.getContractFactory("VerifiedRebalance");
    contract = await Factory.deploy();
    await contract.waitForDeployment();
  });

  it("records a verified event and triggers rebalance above threshold", async function () {
    const chainKey = 1;
    const blockNumber = 12345;
    const txHash = ethers.keccak256(ethers.toUtf8Bytes("test-tx"));
    const amountUsd = 150; // above 100 threshold
    const verified = true;
    const threshold = 100;

    const tx = await contract.recordVerifiedEvent(
      chainKey, blockNumber, txHash, amountUsd, verified, threshold
    );
    const receipt = await tx.wait();

    // Rebalance should have been triggered
    expect(await contract.rebalanceCount()).to.equal(1);
    expect(await contract.totalVerifiedUsd()).to.equal(150);

    // Event recorded
    const eventId = ethers.keccak256(
      ethers.concat([
        ethers.toBeHex(chainKey, 32),
        ethers.toBeHex(blockNumber, 32),
        txHash,
      ])
    );
    const ev = await contract.getEventById(eventId);
    expect(ev.verified).to.equal(true);
    expect(ev.amountUsd).to.equal(150);
  });

  it("refuses to record an unverified event (core thesis)", async function () {
    const txHash = ethers.keccak256(ethers.toUtf8Bytes("unverified"));
    await expect(
      contract.recordVerifiedEvent(1, 1, txHash, 50, false, 100)
    ).to.be.revertedWith("Event not verified on-chain - refusing to record");
  });

  it("does not trigger rebalance below threshold", async function () {
    const txHash = ethers.keccak256(ethers.toUtf8Bytes("small"));
    await contract.recordVerifiedEvent(1, 1, txHash, 50, true, 100);
    expect(await contract.rebalanceCount()).to.equal(0);
  });

  it("only owner can record events", async function () {
    const txHash = ethers.keccak256(ethers.toUtf8Bytes("non-owner"));
    await expect(
      contract.connect(other).recordVerifiedEvent(1, 1, txHash, 150, true, 100)
    ).to.be.revertedWith("Not owner");
  });
});
