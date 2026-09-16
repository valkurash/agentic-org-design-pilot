const express = require('express');
const router = express.Router();

let reminders = [];

const requireAuth = require('../../auth/middleware').requireAuth;

function isValidISO8601(date) {
    return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(date);
}

// Add a reminder
router.post('/', requireAuth, (req, res) => {
    const { todo_id, reminder_datetime } = req.body;
    if (!todo_id || !reminder_datetime) {
        return res.status(400).json({ error: 'TODO ID and reminder datetime are required' });
    }

    if (!isValidISO8601(reminder_datetime)) {
        return res.status(400).json({ error: 'Invalid datetime format' });
    }

    const reminder = {
        id: uuidv4(),
        todo_id,
        reminder_datetime,
        notified: false,
    };
    reminders.push(reminder);
    res.status(201).json(reminder);
});

// Check reminders (pseudo scheduler)
setInterval(() => {
    const now = new Date();
    reminders.forEach(reminder => {
        const reminderTime = new Date(reminder.reminder_datetime);
        if (!reminder.notified && reminderTime <= now) {
            console.log(`Reminder for TODO ID ${reminder.todo_id}`);
            reminder.notified = true;
        }
    });
}, 60000);

module.exports = router;