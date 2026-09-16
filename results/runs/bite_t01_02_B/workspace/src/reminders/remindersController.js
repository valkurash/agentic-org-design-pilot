const express = require('express');
const router = express.Router();
const { requireAuth } = require('../../auth/middleware');
const { v4: uuidv4 } = require('uuid');
const { isValidISODateTime } = require('../utils/isoDateValidation');

// In-memory storage for simplicity
const reminders = [];

router.post('/api/reminders', requireAuth, (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    if (!isValidISODateTime(reminder_datetime)) {
        return res.status(400).send('Invalid date format. Expected full ISO-8601 date-time.');
    }

    const newReminder = {
        id: uuidv4(),
        todo_id,
        reminder_datetime: new Date(reminder_datetime),
        notified: false
    };

    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

module.exports = router;
