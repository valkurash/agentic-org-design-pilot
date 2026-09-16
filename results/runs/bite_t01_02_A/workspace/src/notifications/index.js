const express = require('express');

const router = express.Router();

// This module will have logic for the notification
router.post('/notification', (req, res) => {
    const { email, message } = req.body;
    // Simulate sending out a notification to the user
    console.log(`Sending email to ${email} with message: ${message}`);
    res.status(200).send('Notification sent successfully');
});

module.exports = router;
