const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("RWAYieldGuard", function () {
  let guard, token, owner, ai, attacker;

  beforeEach(async function () {
    [owner, ai, attacker] = await ethers.getSigners();

    const MockERC20 = await ethers.getContractFactory("MockERC20");
    token = await MockERC20.deploy("RWA Token", "RWA", ethers.parseEther("1000000"));

    const RWAYieldGuard = await ethers.getContractFactory("RWAYieldGuard");
    guard = await RWAYieldGuard.deploy(ai.address);
  });

  it("should set owner and ai operator", async function () {
    expect(await guard.owner()).to.equal(owner.address);
    expect(await guard.aiOperator()).to.equal(ai.address);
  });

  it("should let AI register a position", async function () {
    await token.mint(guard.target, ethers.parseEther("1000"));
    await guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 20);
    const pos = await guard.getPosition(token.target);
    expect(pos.active).to.equal(true);
    expect(pos.amount).to.equal(ethers.parseEther("1000"));
    expect(pos.riskScore).to.equal(20);
  });

  it("should reject position with risk score above limit", async function () {
    await expect(
      guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 90)
    ).to.be.revertedWith("risk score exceeds limit");
  });

  it("should execute a valid rebalance intent", async function () {
    await token.mint(guard.target, ethers.parseEther("1000"));
    await guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 20);

    const nonce = (await guard.nonceCounter()) + 1n;
    const deadline = Math.floor(Date.now() / 1000) + 3600;
    const intent = {
      asset: token.target,
      amount: ethers.parseEther("200"),
      riskScore: 20,
      nonce: nonce,
      deadline: deadline,
    };

    await expect(guard.connect(ai).executeRebalance(intent))
      .to.emit(guard, "RebalanceExecuted")
      .withArgs(token.target, ethers.parseEther("200"), 20, nonce);

    // Owner received the rebalanced funds (owner is also the token deployer,
    // so check the delta from the initial 1M supply)
    const ownerBal = await token.balanceOf(owner.address);
    expect(ownerBal).to.equal(ethers.parseEther("1000000") + ethers.parseEther("200"));
  });

  it("should reject stale nonce (replay protection)", async function () {
    await token.mint(guard.target, ethers.parseEther("1000"));
    await guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 20);

    const nonce = (await guard.nonceCounter()) + 1n;
    const deadline = Math.floor(Date.now() / 1000) + 3600;
    const intent = {
      asset: token.target,
      amount: ethers.parseEther("200"),
      riskScore: 20,
      nonce: nonce,
      deadline: deadline,
    };

    await guard.connect(ai).executeRebalance(intent);
    // Replay same nonce -> should revert
    await expect(guard.connect(ai).executeRebalance(intent)).to.be.revertedWith("stale nonce");
  });

  it("should reject expired intent", async function () {
    await token.mint(guard.target, ethers.parseEther("1000"));
    await guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 20);

    const nonce = (await guard.nonceCounter()) + 1n;
    const intent = {
      asset: token.target,
      amount: ethers.parseEther("200"),
      riskScore: 20,
      nonce: nonce,
      deadline: Math.floor(Date.now() / 1000) - 100, // expired
    };

    await expect(guard.connect(ai).executeRebalance(intent)).to.be.revertedWith("intent expired");
  });

  it("should halt when circuit breaker is set", async function () {
    await guard.setCircuitBreaker(1);
    await expect(
      guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 20)
    ).to.be.revertedWith("circuit breaker active");
  });

  it("should only allow owner to withdraw", async function () {
    await token.mint(guard.target, ethers.parseEther("1000"));
    await guard.connect(ai).updatePosition(token.target, ethers.parseEther("1000"), 3000, 20);

    await expect(
      guard.connect(attacker).withdraw(token.target, ethers.parseEther("100"))
    ).to.be.revertedWith("not owner");

    await guard.withdraw(token.target, ethers.parseEther("100"));
    expect(await token.balanceOf(owner.address)).to.equal(ethers.parseEther("1000000") + ethers.parseEther("100"));
  });
});
