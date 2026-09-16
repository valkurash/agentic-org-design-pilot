const express = require('express');
const router = express.Router();

// Create a new Reminder
router.post('/', (req, res) => {
    // Code to create Reminder
    res.status(201).send('Reminder created');
});

module.exports = router;
