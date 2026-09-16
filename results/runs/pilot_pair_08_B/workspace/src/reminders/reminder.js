const express = require('express');
const router = express.Router();

// Middleware for authentication
const { requireAuth } = require('../../auth/middleware');

// Placeholder for storing Reminders in memory
const reminders = new Map();

// Create a Reminder
router.post('/api/reminders', requireAuth, (req, res) => {
    const { todo_id, reminder_time } = req.body;
    const id = generateUUID();
    const newReminder = {
        id,
        todo_id,
        reminder_time: new Date(reminder_time),
        notified: false
    };
    reminders.set(id, newReminder);

    // Schedule notification
    scheduleNotification(newReminder);

    res.status(201).json(newReminder);
});

// Helper function to generate UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Placeholder function to schedule notifications
function scheduleNotification(reminder) {
    const delay = reminder.reminder_time - new Date();
    if (delay > 0) {
        setTimeout(() => {
            reminder.notified = true;
            console.log(`Reminder for TODO ${reminder.todo_id} is due!`);
        }, delay);
    }
}

module.exports = router;