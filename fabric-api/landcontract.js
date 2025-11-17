// landcontract.js
"use strict";

const { Gateway, Wallets } = require("fabric-network");
const fs = require("fs");
const path = require("path");

const { getOrgFromRole } = require("./org-role-map");

const CHANNEL = "landrecords";
const CHAINCODE = "landrecords";

// Load correct CCP based on org
function loadCCP(org) {
    const ccpPath = path.resolve(__dirname, `connection-${org}.json`);
    if (!fs.existsSync(ccpPath)) {
        throw new Error(`Connection profile not found: ${ccpPath}`);
    }
    return JSON.parse(fs.readFileSync(ccpPath, "utf8"));
}

// Connect with org + user
async function connect(org, userId = "admin") {
    const ccp = loadCCP(org);

    const walletPath = path.join(__dirname, "wallet", org);
    const wallet = await Wallets.newFileSystemWallet(walletPath);

    const identity = await wallet.get(userId);
    if (!identity) throw new Error(`Identity ${userId} missing from wallet/${org}`);

    const gateway = new Gateway();
    await gateway.connect(ccp, {
        wallet,
        identity: userId,
        discovery: { enabled: true, asLocalhost: true }
    });

    const network = await gateway.getNetwork(CHANNEL);
    const contract = network.getContract(CHAINCODE);

    return { gateway, contract };
}

// ======================================================
//  🔎 API FUNCTIONS CALLED BY Django → Node.js → Fabric
// ======================================================

/** Get All Requests */
async function getAllLandRequests(org = "org1", user = "admin") {
    const { contract, gateway } = await connect(org, user);
    try {
        const result = await contract.evaluateTransaction("getAllLandRequests");
        return JSON.parse(result.toString());
    } finally {
        gateway.disconnect();
    }
}

/** Create Land Request */
async function createLandRequest(receiptNumber, data) {
    const role = data.currently_with;
    const org = getOrgFromRole(role);

    const { contract, gateway } = await connect(org, "admin");
    try {
        const result = await contract.submitTransaction(
            "createLandRequest",
            receiptNumber,
            JSON.stringify(data)
        );
        return result.toString();
    } finally {
        gateway.disconnect();
    }
}

/** Update Land Status */
async function updateLandStatus(receiptNumber, newStatus, assignedTo, remarks, fromUser, timestamp) {
    const org = getOrgFromRole(fromUser);

    const { contract, gateway } = await connect(org, "admin");
    try {
        const result = await contract.submitTransaction(
            "updateLandStatus",
            receiptNumber,
            newStatus,
            assignedTo,
            remarks,
            fromUser,
            timestamp
        );
        return result.toString();
    } finally {
        gateway.disconnect();
    }
}

module.exports = {
    getAllLandRequests,
    createLandRequest,
    updateLandStatus
};
