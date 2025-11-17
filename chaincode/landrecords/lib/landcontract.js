'use strict';

const { Contract } = require('fabric-contract-api');

class LandRecordContract extends Contract {
    async Init(ctx) {
        console.info('Smart contract instantiated');
    }

    async createLandRequest(ctx, receipt_number, dataJson) {
        const exists = await ctx.stub.getState(receipt_number);
        if (exists && exists.length > 0) {
            throw new Error(`Land request with receipt number ${receipt_number} already exists`);
        }

        const data = JSON.parse(dataJson);
        data.history = [];
        await ctx.stub.putState(receipt_number, Buffer.from(JSON.stringify(data)));
        return `Land request ${receipt_number} created successfully`;
    }

    async readLandRequest(ctx, receipt_number) {
        const buffer = await ctx.stub.getState(receipt_number);
        if (!buffer || buffer.length === 0) {
            throw new Error(`Land request ${receipt_number} does not exist`);
        }
        return buffer.toString();
    }

async updateLandStatus(ctx, receipt_number, newStatus, assignedTo, remarks, fromUser, timestamp) {
    const buffer = await ctx.stub.getState(receipt_number);
    console.log("buffer is ", buffer)



    // --------------------
    console.log("ctx iss.   ",ctx)
    if (!buffer || buffer.length === 0) {
        throw new Error(`Land request ${receipt_number} does not exist`);
    }

    // Parse the existing record
    const land = JSON.parse(buffer.toString());

    // Build the new history entry
    const newEntry = {
        timestamp: timestamp || new Date().toISOString(),
        from_user: fromUser || land.currently_with || "unknown",
        to_user: assignedTo,
        action: newStatus,
        remarks: remarks || "",
        patta_id: ""  // ✅ Always present, but initially empty
    };

    // ✅ Only when approved, set Patta ID
    if (newStatus === "approved") {
        newEntry.patta_id = receipt_number;
        land.patta_id = receipt_number; // Store globally on main record
        land.patta_generated_on = new Date().toISOString(); // optional
    }



    // Ensure history exists
    if (!Array.isArray(land.history)) {
        land.history = [];
    }

    // Append new history entry
    land.history.push(newEntry);

    // Update main fields
    land.status = newStatus;
    land.currently_with = assignedTo;

    // Save back to ledger
    await ctx.stub.putState(receipt_number, Buffer.from(JSON.stringify(land)));

    return `✅ Land request ${receipt_number} updated with status '${newStatus}'` +
           (newStatus === "approved" ? ` (Patta ID = ${receipt_number})` : '');
}



    

    async getAllLandRequests(ctx) {
        const iterator = await ctx.stub.getStateByRange('', '');
        const results = [];

        while (true) {
            const res = await iterator.next();
            if (res.value && res.value.value.toString()) {
                const record = JSON.parse(res.value.value.toString());
                results.push(record);
            }
            if (res.done) break;
        }

        return JSON.stringify(results);
    }
}

module.exports = LandRecordContract;
