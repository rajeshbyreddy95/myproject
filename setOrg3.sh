#!/bin/bash
export PATH=$PATH:/Users/rajeshbyreddy/bchain/project/fabric-samples/bin
export FABRIC_CFG_PATH=/Users/rajeshbyreddy/bchain/project/fabric-samples/config

export CORE_PEER_TLS_ENABLED=true
export CORE_PEER_LOCALMSPID="Org3MSP"
export CORE_PEER_TLS_ROOTCERT_FILE=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt
export CORE_PEER_MSPCONFIGPATH=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/peerOrganizations/org3.example.com/users/Admin@org3.example.com/msp
export CORE_PEER_ADDRESS=localhost:11051
export ORDERER_CA=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/ordererOrganizations/example.com/msp/tlscacerts/tlsca.example.com-cert.pem

# Required for commit
export ORG3_CA=/Users/rajeshbyreddy/bchain/project/fabric-samples/test-network/organizations/peerOrganizations/org3.example.com/peers/peer0.org3.example.com/tls/ca.crt

echo "✔ Org3 environment variables set (Org3MSP)"
