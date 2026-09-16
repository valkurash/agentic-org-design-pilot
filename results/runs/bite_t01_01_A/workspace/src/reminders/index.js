const express = require('express');
const { isValidDate } = require('../utils/dateValidation');
const router = express.Router();

// Middleware simulation for authentication placeholder
function isAuthenticated(req, res, next) {
    // Simulate authentication check
    console.log('Auth middleware invoked');
    return next();
}

// Reminders storage
const reminders = [];

// Create a new reminder
router.post('/', isAuthenticated, (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    if (!isValidDate(reminder_datetime)) {
        return res.status(400).send('Invalid reminder datetime format');
    }
    const newReminder = {
        id: reminders.length + 1,
        todo_id,
        reminder_datetime: new Date(reminder_datetime),
        notified: false
    };
    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

// Cancel a reminder (Assuming delete functionality for simplicity)
router.delete('/:id', isAuthenticated, (req, res) => {
    const { id } = req.params;
    const index = reminders.findIndex(r => r.id === parseInt(id));
    if (index === -1) return res.status(404).send('Reminder not found');
    const deletedReminder = reminders.splice(index, 1);
    res.json(deletedReminder);
});

module.exports = router;
