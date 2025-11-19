#!/bin/bash

set -euo pipefail

# ==== Enroll Org3 Admin and Approve Chaincode ====

BASE_DIR=$PWD
TEST_NETWORK=$BASE_DIR/fabric-samples/test-network
CHAINCODE_NAME=landrecords
CHANNEL_NAME=mychannel

echo "🟢 Setting up Org3 CA environment..."
export FABRIC_CFG_PATH=$TEST_NETWORK/../config
export CORE_PEER_LOCALMSPID="Org3MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=$TEST_NETWORK/organizations/peerOrganizations/org3.example.com/tlsca/tlsca.org3.example.com-cert.pem
export CORE_PEER_ADDRESS=localhost:11051
export PATH=$TEST_NETWORK/../../bin:$PATH

# Create Admin@org3 MSP directory structure
ORG3_ADMIN_DIR=$TEST_NETWORK/organizations/peerOrganizations/org3.example.com/users/Admin@org3.example.com
mkdir -p $ORG3_ADMIN_DIR/msp/{admincerts,cacerts,keystore,signcerts,tlscacerts,tlsintermediatecerts}

echo "🔐 Enrolling Org3 admin via CA..."
fabric-ca-client enroll \
  -u https://admin:adminpw@localhost:12054 \
  --caname ca-org3 \
  -M $ORG3_ADMIN_DIR/msp \
  --tls.certfiles $TEST_NETWORK/organizations/fabricca/org3/tls-cert.pem 2>&1 | tail -20

echo "✅ Org3 admin enrolled!"

export CORE_PEER_MSPCONFIGPATH=$ORG3_ADMIN_DIR/msp

echo "📦 Installing chaincode package on Org3 peer..."
peer lifecycle chaincode install $TEST_NETWORK/$CHAINCODE_NAME.tar.gz 2>&1 | tail -5

echo "🔍 Querying installed chaincode..."
PKG_ID=$(peer lifecycle chaincode queryinstalled 2>/dev/null | grep landrecords_2.0 | head -1 | awk '{print $1}' | sed 's/,$//')
echo "✅ Package ID: $PKG_ID"

echo "👍 Approving chaincode v2.0 from Org3..."
peer lifecycle chaincode approveformyorg \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls \
  --cafile $TEST_NETWORK/organizations/ordererOrganizations/example.com/tlsca/tlsca.example.com-cert.pem \
  --channelID $CHANNEL_NAME \
  --name $CHAINCODE_NAME \
  --version 2.0 \
  --package-id "$PKG_ID" \
  --sequence 2 \
  --signature-policy "AND('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')" 2>&1 | tail -10

echo "✅ Org3 approval complete!"
echo "🔍 Verifying commitment status..."
peer lifecycle chaincode querycommitted --channelID $CHANNEL_NAME --name $CHAINCODE_NAME 2>&1 | grep -A 2 "Approvals"
