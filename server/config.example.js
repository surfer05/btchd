// Configuration template for the geofence relayer server
// Copy this file to config.js and replace these with your actual values

export const config = {
  // Sepolia testnet RPC URL (you can use a free one from Alchemy, Infura, etc.)
  SEPOLIA_RPC_URL: "https://sepolia.infura.io/v3/YOUR_INFURA_PROJECT_ID",

  // Private key for the relayer wallet (must have some ETH for gas fees)
  // Generate a new wallet or use an existing one for testing
  RELAYER_PRIVATE_KEY:
    "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",

  // Address of the deployed GeofenceRegistry contract
  // This will be set after you deploy the contract
  REGISTRY_ADDR: "0x0000000000000000000000000000000000000000",
};
