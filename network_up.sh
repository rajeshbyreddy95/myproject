#!/bin/bash

set -euo pipefail

# ==== Paths ====
BASE_DIR=$PWD
TEST_NETWORK=$BASE_DIR/fabric-samples/test-network
CHAINCODE_NAME=landrecords
CHAINCODE_PATH=$BASE_DIR/chaincode/landrecords
CHAINCODE_LANG=javascript
CHANNEL_NAME=mychannel

# ==== Set Fabric binary paths ====
export PATH=$BASE_DIR/fabric-samples/bin:$PATH
export FABRIC_CFG_PATH=$BASE_DIR/fabric-samples/config

echo "🔻 Shutting down network..."
cd $TEST_NETWORK
./network.sh down

echo "🟢 Starting network and creating channel..."
./network.sh up createChannel -ca -c $CHANNEL_NAME

echo "📦 Deploying chaincode for Org1 + Org2..."
./network.sh deployCC \
  -ccn $CHAINCODE_NAME \
  -ccp $CHAINCODE_PATH \
  -ccl $CHAINCODE_LANG \
  -ccv 1.0 \
  -ccs 1 \
  -ccep "AND('Org1MSP.peer','Org2MSP.peer')"

echo "⬆️ Upgrading chaincode to v2.0 for Org1 + Org2..."
./network.sh deployCC \
  -ccn $CHAINCODE_NAME \
  -ccp $CHAINCODE_PATH \
  -ccl $CHAINCODE_LANG \
  -ccv 2.0 \
  -ccs 2 \
  -ccep "AND('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')"

echo "🟢 Approving v2.0 from Org3..."
export FABRIC_CFG_PATH=$TEST_NETWORK/../config
export CORE_PEER_LOCALMSPID="Org3MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=$TEST_NETWORK/organizations/peerOrganizations/org3.example.com/tlsca/tlsca.org3.example.com-cert.pem
export CORE_PEER_MSPCONFIGPATH=$TEST_NETWORK/organizations/peerOrganizations/org3.example.com/users/Admin@org3.example.com/msp
export CORE_PEER_ADDRESS=localhost:11051
peer lifecycle chaincode install $TEST_NETWORK/$CHAINCODE_NAME.tar.gz
PKG_ID=$(peer lifecycle chaincode queryinstalled 2>/dev/null | grep landrecords_2.0 | awk '{print $1}' | sed 's/,$//')
peer lifecycle chaincode approveformyorg -o localhost:7050 --ordererTLSHostnameOverride orderer.example.com \
  --tls --cafile $TEST_NETWORK/organizations/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem \
  --channelID $CHANNEL_NAME --name $CHAINCODE_NAME --version 2.0 --package-id "$PKG_ID" --sequence 2 \
  --signature-policy "AND('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')"

echo "✅ Network ready with Org1 + Org2 + Org3 (all approved)"

# ==== Post-setup: Enroll admins and register users in Node API ====
echo "📦 Preparing Node API dependencies..."
cd "$BASE_DIR/fabric-api"
npm install

echo "🔐 Enrolling admins for org1, org2, org3..."
node enrollAdmin.js org1
node enrollAdmin.js org2
node enrollAdmin.js org3

echo "👤 Registering users in org1..."
node registerUser.js org1 Clerk
node registerUser.js org1 Superintendent
node registerUser.js org1 ProjectOfficer

echo "👤 Registering users in org2..."
node registerUser.js org2 VRO
node registerUser.js org2 Surveyor
node registerUser.js org2 RevenueInspector
node registerUser.js org2 MRO
node registerUser.js org2 RevenueDeptOfficer

echo "👤 Registering users in org3..."
node registerUser.js org3 JointCollector
node registerUser.js org3 DistrictCollector
node registerUser.js org3 MinistryOfWelfare

echo "✅ Enrollment and registrations complete. Wallets stored under fabric-api/wallet/"
