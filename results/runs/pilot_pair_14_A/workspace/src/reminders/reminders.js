const express = require('express');
const { v4: uuidv4 } = require('uuid');
const router = express.Router();
const { isValidDate } = require('../utils/dateValidation');

let reminders = [];

// POST /api/reminders
router.post('/api/reminders', (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    
    if (!isValidDate(reminder_datetime)) {
        return res.status(400).send('Invalid date format. Use ISO-8601.');
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
