#!/bin/bash

set -euo pipefail

# ==== Complete Fabric Network Setup + Chaincode + Enrollment ====

BASE_DIR=$PWD
TEST_NETWORK=$BASE_DIR/fabric-samples/test-network
CHAINCODE_NAME=landrecords
CHAINCODE_PATH=$BASE_DIR/chaincode/landrecords
CHAINCODE_LANG=javascript
CHANNEL_NAME=mychannel

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔻 STEP 1: Shutting down existing network..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd $TEST_NETWORK
./network.sh down 2>&1 | tail -5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🟢 STEP 2: Starting network with CAs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./network.sh up createChannel -ca -c $CHANNEL_NAME 2>&1 | tail -10

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 STEP 3: Deploying chaincode v1.0 (Org1 + Org2)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./network.sh deployCC \
  -ccn $CHAINCODE_NAME \
  -ccp $CHAINCODE_PATH \
  -ccl $CHAINCODE_LANG \
  -ccv 1.0 \
  -ccs 1 \
  -ccep "AND('Org1MSP.peer','Org2MSP.peer')" 2>&1 | tail -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⬆️ STEP 4: Upgrading chaincode to v2.0 (all 3 orgs)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
./network.sh deployCC \
  -ccn $CHAINCODE_NAME \
  -ccp $CHAINCODE_PATH \
  -ccl $CHAINCODE_LANG \
  -ccv 2.0 \
  -ccs 2 \
  -ccep "AND('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')" 2>&1 | tail -15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Chaincode deployed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "⏳ Waiting 5 seconds for CAs to stabilize..."
sleep 5

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 STEP 5: Enrolling admins and registering users..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$BASE_DIR/fabric-api"
npm install --silent

echo "Enrolling admins..."
node enrollAdmin.js org1 2>&1 | grep -E "(✅|❌|Enrolling)"
node enrollAdmin.js org2 2>&1 | grep -E "(✅|❌|Enrolling)"
node enrollAdmin.js org3 2>&1 | grep -E "(✅|❌|Enrolling)" || echo "⚠️  Org3 CA may not be ready yet"

echo ""
echo "Registering Org1 users..."
node registerUser.js org1 Clerk 2>&1 | grep -E "(✅|❌|Registering)"
node registerUser.js org1 Superintendent 2>&1 | grep -E "(✅|❌|Registering)"
node registerUser.js org1 ProjectOfficer 2>&1 | grep -E "(✅|❌|Registering)"

echo ""
echo "Registering Org2 users..."
node registerUser.js org2 VRO 2>&1 | grep -E "(✅|❌|Registering)"
node registerUser.js org2 Surveyor 2>&1 | grep -E "(✅|❌|Registering)"
node registerUser.js org2 RevenueInspector 2>&1 | grep -E "(✅|❌|Registering)"
node registerUser.js org2 MRO 2>&1 | grep -E "(✅|❌|Registering)"
node registerUser.js org2 RevenueDeptOfficer 2>&1 | grep -E "(✅|❌|Registering)"

echo ""
echo "Registering Org3 users (if admin enrolled)..."
node registerUser.js org3 JointCollector 2>&1 | grep -E "(✅|❌|Registering)" || echo "⚠️  Org3 registration skipped"
node registerUser.js org3 DistrictCollector 2>&1 | grep -E "(✅|❌|Registering)" || echo "⚠️  Org3 registration skipped"
node registerUser.js org3 MinistryOfWelfare 2>&1 | grep -E "(✅|❌|Registering)" || echo "⚠️  Org3 registration skipped"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup complete! Wallets stored in fabric-api/wallet/"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
