const { ethers } = require('ethers');
require('dotenv').config();

// --- CONFIGURATION ---
const USDC_DECIMALS = 6; // for logging credit limits nicely

// Support both Base mainnet (default) and Base Sepolia testnet
const NETWORKS = {
    mainnet: {
        name: "base-mainnet",
        rpcUrl: "https://mainnet.base.org",
        chainId: 8453n, // Base mainnet
        addresses: {
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
        },
    },
    testnet: {
        name: "base-sepolia",
        rpcUrl: "https://sepolia.base.org",
        chainId: 84532n, // Base Sepolia
        addresses: {
            borrowerManager: "0xa891C7F98e3Eb42cB61213F28f3B8Aa13a8Be435",
        },
    },
};

const BORROWER_MANAGER_ABI = [
    "function isBorrowerRegistered(address) view returns (bool)",
    "function isActiveBorrower(address) view returns (bool)",
    "function getAgentSpendLimit(address) view returns (uint256)",
    "function registerAgent(address agent) external",
];

async function main() {
    // 1. Load Signer from Environment
    const privateKey = process.env.PRIVATE_KEY;
    if (!privateKey) {
        console.error("❌ FATAL: PRIVATE_KEY environment variable not set. This skill cannot sign transactions.");
        process.exit(1);
    }

    // 2. Parse Command-Line Arguments
    // Usage:
    //   node register.js                   # default: mainnet
    //   node register.js mainnet
    //   node register.js testnet

    let networkKey = "mainnet";
    if (process.argv[2]) {
        const maybeNetwork = process.argv[2].toLowerCase();
        if (maybeNetwork === "mainnet" || maybeNetwork === "testnet") {
            networkKey = maybeNetwork;
        } else {
            console.error("❌ USAGE: node register.js [mainnet|testnet]");
            process.exit(1);
        }
    }

    const networkConfig = NETWORKS[networkKey];

    // 3. Setup Provider & Wallet
    const provider = new ethers.JsonRpcProvider(networkConfig.rpcUrl);

    const network = await provider.getNetwork();
    const actualChainId = Number(network.chainId);
    const expectedChainId = Number(networkConfig.chainId);

    if (actualChainId !== expectedChainId) {
        console.error(`❌ FATAL: Unexpected chainId ${actualChainId}. Expected ${expectedChainId} (${networkConfig.name}). Aborting.`);
        process.exit(1);
    }

    const wallet = new ethers.Wallet(privateKey, provider);
    const agentAddress = wallet.address;

    console.log("--- SOHO Pay Borrower Registration ---");
    console.log(`- Network: ${networkConfig.name} (${networkKey})`);
    console.log(`- Agent (PRIVATE_KEY address): ${agentAddress}`);
    console.log("---------------------------------------");

    const borrowerManager = new ethers.Contract(
        networkConfig.addresses.borrowerManager,
        BORROWER_MANAGER_ABI,
        wallet
    );

    // 4. Check current registration state
    console.log("\n🔍 Checking current borrower state...");
    const isRegistered = await borrowerManager.isBorrowerRegistered(agentAddress);
    const isActive = await borrowerManager.isActiveBorrower(agentAddress);
    const creditLimit = await borrowerManager.getAgentSpendLimit(agentAddress).catch(() => 0n);

    console.log(`- isRegistered: ${isRegistered ? "✅ yes" : "❌ no"}`);
    console.log(`- isActive: ${isActive ? "✅ yes" : "❌ no"}`);
    if (creditLimit) {
        console.log(`- Existing agentSpendLimit: ${ethers.formatUnits(creditLimit, USDC_DECIMALS)} USDC`);
    }

    if (isActive) {
        console.log("\n✅ Agent is already active. No registration transaction needed.");
        return;
    }

    console.log("\n🚀 Sending registerAgent transaction...");
    try {
        const tx = await borrowerManager.registerAgent(agentAddress);
        console.log(`- Tx hash: ${tx.hash}`);
        console.log("Waiting for confirmation...");
        const receipt = await tx.wait();
        console.log(`\n🎉 Agent registered in block: ${receipt.blockNumber}`);
    } catch (error) {
        console.error("\n❌ Registration transaction failed:", error.reason || error.message);
        process.exit(1);
    }
}

main().catch((err) => {
    console.error("\n❌ Unexpected error in register.js:", err);
    process.exit(1);
});
