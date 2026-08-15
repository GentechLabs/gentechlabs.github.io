require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.24",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    cc3: {
      url: "https://rpc.cc3-testnet.creditcoin.network",
      chainId: 102031,
      accounts: process.env.AGENT_PRIVATE_KEY ? [process.env.AGENT_PRIVATE_KEY] : [],
    },
  },
};
