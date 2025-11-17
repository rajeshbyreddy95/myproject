#!/bin/bash
export PATH=$PATH:/Users/rajeshbyreddy/bchain/project/fabric-samples/bin
export FABRIC_CFG_PATH=/Users/rajeshbyreddy/bchain/project/fabric-samples/config

export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_ADDRESS=localhost:7051
export ORDERER_CA=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/ordererOrganizations/example.com/msp/tlscacerts/tlsca.example.com-cert.pem

# Required for commit
export ORG1_CA=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt

echo "✔ Org1 environment variables set (Org1MSP)"
