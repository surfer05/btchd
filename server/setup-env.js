#!/usr/bin/env node

// Simple script to help set up environment variables for the geofence relayer
import fs from "fs";
import { execSync } from "child_process";

console.log(
  "🔧 Setting up environment variables for the geofence relayer...\n"
);

// Check if .env already exists
if (fs.existsSync(".env")) {
  console.log("⚠️  .env file already exists. Backing up to .env.backup");
  fs.copyFileSync(".env", ".env.backup");
}

// Create a basic .env file
const envContent = `# Environment variables for the geofence relayer server
# Replace these with your actual values

# Sepolia testnet RPC URL (you can use a free one from Alchemy, Infura, etc.)
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID

# Private key for the relayer wallet (must have some ETH for gas fees)
# Generate a new wallet or use an existing one for testing
RELAYER_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef

# Address of the deployed GeofenceRegistry contract
# This will be set after you deploy the contract
REGISTRY_ADDR=0x0000000000000000000000000000000000000000
`;

fs.writeFileSync(".env", envContent);

console.log("✅ Created .env file with template values");
console.log("\n📝 Next steps:");
console.log(
  "1. Get a Sepolia RPC URL from https://infura.io/ or https://alchemy.com/"
);
console.log(
  "2. Generate a private key for testing (you can use MetaMask or generate one)"
);
console.log("3. Deploy the GeofenceRegistry contract and update REGISTRY_ADDR");
console.log("4. Make sure your wallet has some Sepolia ETH for gas fees");
console.log("\n🚀 Then run: node index.js");
