#!/bin/bash

# Define paths
TEST_NETWORK=../fabric-samples/test-network
CONN_PROFILE_SRC=$TEST_NETWORK/organizations/peerOrganizations/org1.example.com/connection-org1.json
CONN_PROFILE_DEST=./connection-org1.json
WALLET_DIR=./wallet

# Step 1: Remove old wallet (optional: comment this line if you want to keep existing identities)
echo "🧹 Cleaning wallet..."
rm -rf $WALLET_DIR

# Step 2: Copy connection profile
echo "📁 Copying connection-org1.json..."
if cp $CONN_PROFILE_SRC $CONN_PROFILE_DEST; then
    echo "✅ connection-org1.json copied successfully."
else
    echo "❌ Failed to copy connection profile. Check if the network is up."
    exit 1
fi

# Step 3: Enroll admin
echo "🔐 Enrolling admin identity..."
if node enrollAdmin.js; then
    echo "✅ Admin enrolled successfully."
else
    echo "❌ Failed to enroll admin. Check connection profile or CA settings."
    exit 1
fi

echo "🚀 Setup complete. You're ready to run your API."