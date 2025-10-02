require("@nomiclabs/hardhat-ethers");

module.exports = {
  solidity: "0.8.19",
  networks: {
    hardhat: {
      forking: {
        url: "https://eth-mainnet.g.alchemy.com/v2/demo", // Using demo RPC
        blockNumber: 18500000 // Recent block
      }
    }
  }
};