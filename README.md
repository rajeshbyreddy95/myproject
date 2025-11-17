# 🧾 Land Record Management System — Complete Setup Guide (Fabric + API + Django)

---

## 📥 0. Clone the Project Repository

First, clone your GitHub project repository:

```bash
git clone https://github.com/abojha/fabric-land-records
cd land-record-blockchain
```

### Install Prerequisites

Make sure the following are installed:

```bash
sudo apt update
sudo apt install curl docker.io docker-compose git npm nodejs python3 python3-pip jq -y
```

### ✅ Check Versions

Ensure you're running compatible versions:

```bash
node -v          # Should be >= 14.x
npm -v           # Should be >= 6.x
docker -v        # Should be >= 20.x
docker-compose -v  # Should be >= 1.25.x
python3 --version
```

If `node` is not available after installing `nodejs`, create an alias:

```bash
sudo ln -s /usr/bin/nodejs /usr/bin/node
```

---

## 📦 1. Download `fabric-samples` and Fabric Binaries

The project expects the standard Hyperledger `fabric-samples` folder for network setup and testing.

```bash
# Clone fabric-samples
git clone https://github.com/hyperledger/fabric-samples.git
cd fabric-samples
git checkout v2.5.0

# Download Fabric binaries
wget https://github.com/hyperledger/fabric/releases/download/v2.5.0/hyperledger-fabric-linux-amd64-2.5.0.tar.gz
wget https://github.com/hyperledger/fabric-ca/releases/download/v1.5.6/hyperledger-fabric-ca-linux-amd64-1.5.6.tar.gz

# Extract the binaries
tar -xvzf hyperledger-fabric-linux-amd64-2.5.0.tar.gz
tar -xvzf hyperledger-fabric-ca-linux-amd64-1.5.6.tar.gz
```

Ensure the `bin/` and `config/` directories are now available in `fabric-samples/`.

---

## 🔁 2. Bring Up Fabric Network

From your **main project directory**:

```bash
source network_up.sh
```

This script:

- Brings down any existing network
- Brings up new Fabric network using CAs
- Creates `mychannel`
- Joins Org1 & Org2
- Sets anchor peers
- Deploys chaincode from `../chaincode/landrecords`
- Copies connection profile to API folder
- Clears and re-enrolls admin in wallet

---

## 🧤 3. Set Org1 CLI Environment

In your **main project directory**:

```bash
source setOrg1.sh
```

This sets:

- TLS cert paths
- Peer/Orderer MSP env
- Orderer CA, Fabric bin in PATH

---

## 🌐 4. Setup Fabric API Server

In new Termina and Inside fabric-api:

```bash
cd fabric-api
npm install
source setup.sh
```

This:

- Deletes old `wallet/`
- Copies latest `connection-org1.json`
- Enrolls admin via `enrollAdmin.js`

---

## 🚀 5. Start the Fabric API Server

```bash
node api.js
```

Visit: [http://localhost:3000](http://localhost:3000/)

---

## 🖥️ 6. Run Django Web Application

In a new terminal:

```bash
cd myproject
python3 -m venv myenv           # Create virtual environment (if not already created)
source myenv/bin/activate       # Activate virtual environment
pip install -r requirements.txt # Install dependencies
python manage.py runserver      # Start Django development server
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000/)

Supports:

- Citizen & official login
- Land request & workflow
- Blockchain updates via signals

---

## 📬 7. Blockchain Sync via Django Signals

`signals.py` triggers blockchain writes:

- `createLandRequest()` for new land
- `updateLandStatus()` for forwarding/status changes

---

## 🔐 Sample Peer CLI Commands (Run after `source setOrg1.sh`)

📦 **Create Land Request**

```bash
peer chaincode invoke \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls --cafile $ORDERER_CA \
  -C mychannel \
  -n landrecords \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE \
  -c '{"Args":["createLandRequest", "12345", "{\"owner\":\"John Doe\",\"area\":\"500 sqft\",\"location\":\"Sector 21\",\"status\":\"Pending\",\"currently_with\":\"clerk\"}"]}'
```

📖 **Read a Land Request**

```bash
peer chaincode query \
  -C mychannel \
  -n landrecords \
  -c '{"Args":["readLandRequest", "12345"]}'
```

🔄 **Update Land Status**

```bash
peer chaincode invoke \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls --cafile $ORDERER_CA \
  -C mychannel \
  -n landrecords \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles $CORE_PEER_TLS_ROOTCERT_FILE \
  -c '{"Args":["updateLandStatus", "12345", "Approved", "superintendent", "Verified documents", "clerk", "2025-03-31T23:30:00Z"]}'
```

📋 **Get All Land Requests**

```bash
peer chaincode query \
  -C mychannel \
  -n landrecords \
  -c '{"Args":["getAllLandRequests"]}'
```

---

## 🌐 API Endpoints (via curl)

📦 **Create Land Request**

```bash
curl -X POST http://localhost:3000/api/landrequests/create \
  -H "Content-Type: application/json" \
  -d '{
    "receiptNumber": "12345",
    "data": {
      "owner": "John Doe",
      "area": "500 sqft",
      "location": "Sector 21",
      "status": "Pending",
      "currently_with": "clerk",
      "history": []
    }
  }'
```

🔍 **Get All Land Requests**

```bash
curl http://localhost:3000/api/landrequests | jq
```

🔄 **Update Land Request Status**

```bash
curl -X POST http://localhost:3000/api/landrequests/update \
  -H "Content-Type: application/json" \
  -d '{
    "receiptNumber": "12345",
    "newStatus": "Approved",
    "assignedTo": "superintendent",
    "remarks": "Verified documents",
    "fromUser": "clerk",
    "timestamp": "2025-03-31T23:30:00Z"
  }'
```

---

## 📦 Final Project Structure Summary

| 🔧 Component        | 📁 Location                                     | 📝 Purpose                                |
|--------------------|-------------------------------------------------|--------------------------------------------|
| Fabric Network     | `network_up.sh`                                 | Full chaincode deploy and setup            |
| CLI Config         | `setOrg1.sh`                                    | Environment for peer CLI commands         |
| Chaincode          | `fabric-samples/chaincode/landrecords`         | Smart contract logic                      |
| API Setup Script   | `fabric-api/setup.sh`                           | Admin re-enrollment + wallet setup        |
| Fabric API Server  | `fabric-api/api.js`                             | REST API to interact with chaincode       |
| Admin Wallet       | `fabric-api/wallet/`                            | Stores enrolled identity                  |
| Django Web App     | `myproject/`                                    | UI for citizens & officials               |
| Signal Hooks       | `myproject/myapp/signals.py`                    | Trigger API from database events          |

---
