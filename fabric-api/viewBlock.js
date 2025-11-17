"use strict";

const fs = require("fs");
const path = require("path");
const { Wallets, Gateway } = require("fabric-network");

const ORGS = {
    org1: { ccp: "connection-org1.json", mspId: "Org1MSP" },
    org2: { ccp: "connection-org2.json", mspId: "Org2MSP" },
    org3: { ccp: "connection-org3.json", mspId: "Org3MSP" }
};

async function main() {
    try {
        const org = (process.argv[2] || "org1").toLowerCase();
        const user = process.argv[3] || "admin";

        console.log(`\n🏛 Using ${org.toUpperCase()} — user: ${user}`);

        const ccpPath = path.resolve(__dirname, ORGS[org].ccp);
        const ccp = JSON.parse(fs.readFileSync(ccpPath, "utf8"));

        const walletPath = path.join(__dirname, "wallet", org);
        const wallet = await Wallets.newFileSystemWallet(walletPath);
        const identity = await wallet.get(user);

        if (!identity) {
            console.error(`❌ Identity ${user} not found in wallet/${org}`);
            return;
        }

        const gateway = new Gateway();
        await gateway.connect(ccp, {
            wallet,
            identity: user,
            discovery: { enabled: true, asLocalhost: true }
        });

        const network = await gateway.getNetwork("landrecords");

        console.log("📡 Listening for latest block...");

        let received = false;

        await network.addBlockListener(
            async (event) => {
                received = true;

                const block = event.blockData;

                console.log("\n🧱 LATEST BLOCK RECEIVED");
                console.log("--------------------------------");
                console.log("🔢 Block Number:", block.header.number);
                console.log("⛓ Data Hash:", block.header.data_hash.toString("hex"));
                console.log("🔐 Prev Hash:", block.header.previous_hash.toString("hex"));

                if (block.data && block.data.data.length > 0) {
                    const tx = block.data.data[0].payload.header.channel_header;
                    console.log("📜 Channel:", tx.channel_id);
                    console.log("🆔 TxID:", tx.tx_id);
                    console.log("⌚ Timestamp:", tx.timestamp);
                }

                console.log("--------------------------------");

                await gateway.disconnect();
            },
            { type: "full", startBlock: "newest" }
        );

        // wait a moment for event
        await new Promise((resolve) => setTimeout(resolve, 2000));

        if (!received) {
            console.log("⚠ No new blocks yet — channel is idle.");
            await gateway.disconnect();
        }

    } catch (err) {
        console.error("❌ Error:", err);
    }
}

main();
