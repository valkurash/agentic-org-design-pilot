const express = require('express');
const router = express.Router();

// Memory storage for reminders (this would be replaced by a real database in production)
let reminders = [];

// Create a new reminder
router.post('/api/reminders', (req, res) => {
    const reminderDatetime = req.body.reminder_datetime;

    // Validate the date using the frozen dateValidation module
    const { isValidDate } = require('../utils/dateValidation');
    if (!isValidDate(reminderDatetime.split('T')[0])) {
        return res.status(400).json({ error: 'Invalid date format. Use YYYY-MM-DD' });
    }

    const newReminder = {
        id: generateUUID(),
        todo_id: req.body.todo_id,
        reminder_datetime: reminderDatetime,
        notified: false
    };
    reminders.push(newReminder);
    scheduleNotification(newReminder);
    res.status(201).json(newReminder);
});

// Schedule notification
function scheduleNotification(reminder) {
    const reminderTime = new Date(reminder.reminder_datetime).getTime();
    const now = Date.now();
    const delay = reminderTime - now;

    if (delay > 0) {
        setTimeout(() => {
            notifyUser(reminder);
        }, delay);
    }
}

// Placeholder notification function
function notifyUser(reminder) {
    reminder.notified = true;
    console.log(`Notification sent for Reminder ID: ${reminder.id}`); // Replace with actual notification logic
}

// UUID generator for simplicity
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

module.exports = router;
