const express = require('express');
const router = express.Router();

// Mock Reminder Database (Array for simplicity)
let reminders = [];

// Create a new Reminder
router.post('/api/reminders', (req, res) => {
    const { todoId, reminderDatetime } = req.body;
    const newReminder = {
        id: (reminders.length + 1).toString(),
        todoId,
        reminderDatetime
    };
    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

module.exports = router;
