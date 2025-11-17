#!/bin/bash

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

echo "🟢 Adding Org3 to the network..."
cd addOrg3
./addOrg3.sh up -c $CHANNEL_NAME -ca
cd ..

echo "⬆️ Upgrading chaincode to include Org3..."
./network.sh deployCC \
  -ccn $CHAINCODE_NAME \
  -ccp $CHAINCODE_PATH \
  -ccl $CHAINCODE_LANG \
  -ccv 2.0 \
  -ccs 2 \
  -ccep "AND('Org1MSP.peer','Org2MSP.peer','Org3MSP.peer')"

echo "✅ Network ready with Org1 + Org2 + Org3"
