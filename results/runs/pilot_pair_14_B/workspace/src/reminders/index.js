const express = require('express');
const { requireAuth } = require('../../auth/middleware');
const router = express.Router();

// Mock data for example
let reminders = [];

// Create a reminder for a TODO item
router.post('/api/reminders', requireAuth, (req, res) => {
    const { todoId, reminderDatetime } = req.body;
    // Reminder date validation placeholder
    // This assumes 'reminderDatetime' is ISO 8601
    const newReminder = {
        id: reminders.length + 1,
        todo_id: todoId,
        reminder_datetime: new Date(reminderDatetime),
        notified: false
    };
    reminders.push(newReminder);
    res.status(201).json(newReminder);
});

// Placeholder for sending a notification
function sendNotification(reminder) {
    console.log(`Reminder for TODO ${reminder.todo_id}`);
}

module.exports = router;
