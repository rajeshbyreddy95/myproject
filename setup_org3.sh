#!/bin/bash

set -euo pipefail

# ==== Start Org3 CA and Complete Enrollment/Registration ====

BASE_DIR=$PWD
TEST_NETWORK=$BASE_DIR/fabric-samples/test-network
FABRIC_API=$BASE_DIR/fabric-api

echo "🟢 Starting Org3 CA container..."
cd $TEST_NETWORK
docker-compose -f docker-compose-ca.yaml up -d ca_org3

echo "⏳ Waiting for Org3 CA to be ready (15 seconds)..."
sleep 15

echo "🔐 Enrolling admin for Org3..."
cd $FABRIC_API
node enrollAdmin.js org3

echo "👤 Registering users in org3..."
node registerUser.js org3 JointCollector
node registerUser.js org3 DistrictCollector
node registerUser.js org3 MinistryOfWelfare

echo "✅ Org3 enrollment and registrations complete!"
echo "📁 All user wallets stored under fabric-api/wallet/"
