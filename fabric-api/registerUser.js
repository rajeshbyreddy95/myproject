/*
 * Register + Enroll user (SAFE MODE)
 * Works with Fabric 2.x and wallet directory structure.
 */

"use strict";

const FabricCAServices = require("fabric-ca-client");
const { Wallets } = require("fabric-network");
const fs = require("fs");
const path = require("path");

const ORGS = {
    org1: {
        ccp: "connection-org1.json",
        caName: "ca.org1.example.com",
        mspId: "Org1MSP",
        affiliation: "org1.department1"
    },
    org2: {
        ccp: "connection-org2.json",
        caName: "ca.org2.example.com",
        mspId: "Org2MSP",
        affiliation: "org2.department1"
    },
    org3: {
        ccp: "connection-org3.json",
        caName: "ca.org3.example.com",
        mspId: "Org3MSP",
        affiliation: "org3.department1"
    }
};

async function main() {
    try {
        const org = (process.argv[2] || "org1").toLowerCase();
        const username = process.argv[3];

        if (!username) {
            console.log("❌ Usage: node registerUser.js org1 Clerk");
            return;
        }

        if (!ORGS[org]) {
            console.log(`❌ Invalid org: ${org}`);
            return;
        }

        console.log(`🔐 Registering user "${username}" for ${org}...`);

        // load connection profile
        const ccpPath = path.resolve(__dirname, ORGS[org].ccp);
        const ccp = JSON.parse(fs.readFileSync(ccpPath, "utf8"));

        const caInfo = ccp.certificateAuthorities[ORGS[org].caName];
        const ca = new FabricCAServices(
            caInfo.url,
            { trustedRoots: caInfo.tlsCACerts.pem, verify: false }
        );

        // Load wallet
        const walletPath = path.join(__dirname, "wallet", org);
        const wallet = await Wallets.newFileSystemWallet(walletPath);

        // Remove old identity (SAFE – DOES NOT USE unlink)
        const exists = await wallet.get(username);
        if (exists) {
            console.log(`⚠ Wallet identity exists → removing`);
            await wallet.remove(username);
        }

        // Load admin
        const adminIdentity = await wallet.get("admin");
        if (!adminIdentity) {
            console.log(`❌ Admin not enrolled. Run: node enrollAdmin.js ${org}`);
            return;
        }

        const provider = wallet.getProviderRegistry().getProvider(adminIdentity.type);
        const adminUser = await provider.getUserContext(adminIdentity, "admin");

        // Remove identity from CA (if exists)
        try {
            console.log(`⚠ CA: Removing existing CA identity (if exists)...`);
            await ca.newIdentityService().delete(username, adminUser);
        } catch (e) {
            console.log("ℹ No CA identity found, continuing...");
        }

        // Register user
        const secret = await ca.register(
            {
                enrollmentID: username,
                role: "client",
                affiliation: ORGS[org].affiliation
            },
            adminUser
        );

        // Enroll user
        const enrollment = await ca.enroll({
            enrollmentID: username,
            enrollmentSecret: secret
        });

        const identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes()
            },
            mspId: ORGS[org].mspId,
            type: "X.509"
        };

        await wallet.put(username, identity);

        console.log(`✅ User "${username}" registered + enrolled successfully!`);
        console.log(`📁 Saved to wallet/${org}`);

    } catch (err) {
        console.error("❌ ERROR:", err);
    }
}

main();
