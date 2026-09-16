const express = require('express');
const router = express.Router();

// Reminder storage simulation
let reminders = [];

// Schedule Reminder route
router.post('/reminders', (req, res) => {
    const { todo_id, reminder_time } = req.body;
    const userId = req.session.userId;

    const newReminder = {
        id: (reminders.length + 1).toString(),
        todo_id,
        reminder_time: new Date(reminder_time)
    };
    reminders.push(newReminder);

    // For an initial basic implementation, we would set a timeout to trigger the reminder.
    // This is obviously a simplification and not suitable for production.
    const delay = new Date(reminder_time).getTime() - Date.now();
    setTimeout(() => {
        // Simulate sending in-app notification
        console.log(`Reminder: Your TODO ${todo_id} is due now!`);
    }, delay);

    res.status(201).json(newReminder);
});

module.exports = router;
