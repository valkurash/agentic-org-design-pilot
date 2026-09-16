const express = require('express');
const { v4: uuidv4 } = require('uuid');

const router = express.Router();

let reminders = [];

// Create Reminder
router.post('/api/reminders', (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z$/.test(reminder_datetime)) {
        return res.status(400).send('Invalid ISO-8601 datetime format.');
    }

    const newReminder = {
        id: uuidv4(),
        todo_id,
        reminder_datetime,
        notified: false
    };
    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

module.exports = router;
