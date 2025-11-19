"use strict";

const { Gateway, Wallets } = require("fabric-network");
const fs = require("fs");
const path = require("path");

const CHANNEL = "landrecords";
const CHAINCODE = "landrecords";


// --------------------------------------------------
// ✔ FULL ROLE → ORG MAPPING 
// --------------------------------------------------
const ROLE_TO_ORG = {
    // ORG1 users
    clerk: "org1",
    superintendent: "org1",
    projectofficer: "org1",

    // ORG2 users
    vro: "org2",
    surveyor: "org2",
    revenueinspector: "org2",
    mro: "org2",
    revenuedepofficer: "org2",

    // ORG3 users
    jointcollector: "org3",
    districtcollector: "org3",
    ministryofwelfare: "org3"
};


// --------------------------------------------------
// Normalize role → org1/org2/org3
// --------------------------------------------------
function getOrgFromRole(role) {
    if (!role) return "org1";
    role = role.toLowerCase().replace(/\s+/g, "");
    return ROLE_TO_ORG[role] || "org1";
}


// --------------------------------------------------
// Load connection JSON
// --------------------------------------------------
function loadCCP(org) {
    const ccpPath = path.join(__dirname, `connection-${org}.json`);
    if (!fs.existsSync(ccpPath)) {
        throw new Error(`❌ Connection profile not found: ${ccpPath}`);
    }
    return JSON.parse(fs.readFileSync(ccpPath, "utf8"));
}


// --------------------------------------------------
// Connect to network
// --------------------------------------------------
async function connect(role, userId = "admin") {
    const org = getOrgFromRole(role);

    const ccp = loadCCP(org);

    const walletPath = path.join(__dirname, "wallet", org);
    const wallet = await Wallets.newFileSystemWallet(walletPath);

    const id = await wallet.get(userId);
    if (!id) {
        throw new Error(`❌ Identity "${userId}" missing in wallet/${org}`);
    }

    const gateway = new Gateway();
    await gateway.connect(ccp, {
        wallet,
        identity: userId,

        // ✔ IMPORTANT FIX — disable discovery to avoid endorsement mismatch
        discovery: { enabled: false, asLocalhost: true }
    });

    const network = await gateway.getNetwork(CHANNEL);
    const contract = network.getContract(CHAINCODE);

    return { gateway, contract };
}


// --------------------------------------------------
// 🔹 Get all land requests
// --------------------------------------------------
async function getAllLandRequests(role) {
    const { gateway, contract } = await connect(role, "admin");
    try {
        const res = await contract.evaluateTransaction("getAllLandRequests");
        return JSON.parse(res.toString());
    } finally {
        gateway.disconnect();
    }
}


// --------------------------------------------------
// 🔹 Create new request
// --------------------------------------------------
async function createLandRequest(receiptNumber, data) {
    const role = data.currently_with || "clerk";  // default: clerk → org1

    const { gateway, contract } = await connect(role, role.toLowerCase());
    try {
        const res = await contract.submitTransaction(
            "createLandRequest",
            receiptNumber,
            JSON.stringify(data)
        );
        return res.toString();
    } finally {
        gateway.disconnect();
    }
}


// --------------------------------------------------
// 🔹 Update status
// --------------------------------------------------
async function updateLandStatus(receiptNumber, newStatus, assignedTo, remarks, fromUser, timestamp) {
    const role = fromUser || "clerk";

    const { gateway, contract } = await connect(role, role.toLowerCase());
    try {
        const res = await contract.submitTransaction(
            "updateLandStatus",
            receiptNumber,
            newStatus,
            assignedTo || "",
            remarks || "",
            fromUser || "",
            timestamp || ""
        );
        return res.toString();
    } finally {
        gateway.disconnect();
    }
}


module.exports = {
    getAllLandRequests,
    createLandRequest,
    updateLandStatus,
    getOrgFromRole
};
