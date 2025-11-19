// api.js
'use strict';

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { v4: uuidv4 } = require('uuid');

const {
    getAllLandRequests,
    createLandRequest,
    updateLandStatus
} = require('./landcontract');

const app = express();
const port = 3000;

app.use(cors());
app.use(bodyParser.json());

/** GET ALL REQUESTS */
app.get('/api/landrequests', async (req, res) => {
    try {
        const org = req.query.org || "org1";
        const user = req.query.user || "admin";

        const result = await getAllLandRequests(org, user);
        res.setHeader("Content-Type", "application/json");
        res.send(JSON.stringify(result, null, 4));   // Pretty JSON
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/** CREATE REQUEST */
app.post('/api/landrequests/create', async (req, res) => {
    try {
        const { receiptNumber, data } = req.body;
        const result = await createLandRequest(receiptNumber, data);
        res.json({ message: result });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

/** UPDATE STATUS */
app.post('/api/landrequests/update', async (req, res) => {
    try {
        const { receiptNumber, newStatus, assignedTo, remarks, fromUser, timestamp } = req.body;
        const result = await updateLandStatus(receiptNumber, newStatus, assignedTo, remarks, fromUser, timestamp);
        res.json({ message: result });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`🚀 Fabric API server running at http://localhost:${port}`);
});
