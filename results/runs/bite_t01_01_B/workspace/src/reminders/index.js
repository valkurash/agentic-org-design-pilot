const express = require('express');
const { requireAuth } = require('../../auth/middleware');
const router = express.Router();

// Dummy reminder store
const reminders = [];

// POST create a reminder
router.post('/', requireAuth, (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    if (!isValidISODate(reminder_datetime)) {
        return res.status(400).json({ error: 'Invalid date format' });
    }

    const newReminder = {
        id: generateUUID(),
        todo_id,
        reminder_datetime,
        notified: false
    };

    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

function isValidISODate(dateString) {
    // Validate ISO 8601 date string
    return !isNaN(Date.parse(dateString));
}

function generateUUID() {
    // Simplified UUID generation for illustration
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

module.exports = router;
