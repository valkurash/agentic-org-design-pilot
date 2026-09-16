const express = require('express');
const router = express.Router();

const ReminderService = require('./reminderService');

// Middleware for authentication
const authMiddleware = require('../../auth/middleware');

// Apply authentication middleware
router.use(authMiddleware);

// Create reminder
router.post('/api/reminders', async (req, res) => {
    try {
        const { todoId, reminder_datetime } = req.body;
        const reminder = await ReminderService.createReminder(todoId, reminder_datetime);
        res.status(201).json(reminder);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
