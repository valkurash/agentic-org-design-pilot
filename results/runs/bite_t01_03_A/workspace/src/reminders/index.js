const express = require('express');
const router = express.Router();

// Mock database
let reminders = [];

// Middleware to validate reminder request
function validateReminderRequest(req, res, next) {
    const { reminder_datetime } = req.body;
    if (!reminder_datetime || !isValidISODate(reminder_datetime)) {
        return res.status(400).json({ error: 'Valid ISO-8601 datetime required.' });
    }
    next();
}

// Validate full ISO-8601 format
function isValidISODate(value) {
    return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$/.test(String(value));
}

// Create Reminder
router.post('/', validateReminderRequest, (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    const newReminder = {
        id: reminders.length + 1,
        todo_id,
        reminder_datetime,
        notified: false,
        user_id: req.user.id // Assume req.user is populated by auth middleware
    };
    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

module.exports = router;
