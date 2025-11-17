// enrollAdmin.js
'use strict';

const FabricCAServices = require('fabric-ca-client');
const { Wallets } = require('fabric-network');
const fs = require('fs');
const path = require('path');

const ORGS = {
    org1: { ccp: "connection-org1.json", ca: "ca.org1.example.com", mspId: "Org1MSP" },
    org2: { ccp: "connection-org2.json", ca: "ca.org2.example.com", mspId: "Org2MSP" },
    org3: { ccp: "connection-org3.json", ca: "ca.org3.example.com", mspId: "Org3MSP" }
};

async function main() {
    const org = (process.argv[2] || "org1").toLowerCase();

    if (!ORGS[org]) {
        console.error(`Invalid org: ${org}. Use org1/org2/org3`);
        return;
    }

    const cfg = ORGS[org];
    console.log(`🔐 Enrolling admin for ${cfg.mspId}...`);

    const ccp = JSON.parse(fs.readFileSync(path.join(__dirname, cfg.ccp), "utf8"));
    const caInfo = ccp.certificateAuthorities[cfg.ca];
    const ca = new FabricCAServices(caInfo.url, { trustedRoots: caInfo.tlsCACerts.pem, verify: false });

    const walletPath = path.join(__dirname, "wallet", org);
    const wallet = await Wallets.newFileSystemWallet(walletPath);

    const existing = await wallet.get("admin");
    if (existing) {
        console.log(`ℹ️ Admin already exists for ${org}`);
        return;
    }

    const enrollment = await ca.enroll({
        enrollmentID: "admin",
        enrollmentSecret: "adminpw",
    });

    await wallet.put("admin", {
        credentials: {
            certificate: enrollment.certificate,
            privateKey: enrollment.key.toBytes(),
        },
        mspId: cfg.mspId,
        type: "X.509",
    });

    console.log(`✅ Admin enrolled for ${cfg.mspId}`);
}

main();
