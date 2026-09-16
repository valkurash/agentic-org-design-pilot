const express = require('express');
const router = express.Router();

// Middleware to ensure user authentication
const authMiddleware = require('../auth/middleware');
// Date validation utility
const { validateISODateString } = require('../utils/dateValidation');

// Simulating a database for reminders
let reminders = [];

// POST /api/reminders - Create or cancel a reminder
router.post('/', authMiddleware, (req, res) => {
    const { todoItemId, reminder_time } = req.body;
    const userId = req.session.userId;

    // Validate the reminder time
    if (!validateISODateString(reminder_time)) {
        return res.status(400).json({ error: 'Invalid reminder time format' });
    }

    const newReminder = {
        id: Date.now().toString(),
        todoItemId,
        reminder_time: new Date(reminder_time),
        created_at: new Date(),
    };

    reminders.push(newReminder);

    // Simulate notification scheduling
    setTimeout(() => {
        // In-app notification logic
        console.log(`Reminder for TODO ${todoItemId} is due!`);
    }, new Date(reminder_time) - new Date());

    res.status(201).json(newReminder);
});

module.exports = router;