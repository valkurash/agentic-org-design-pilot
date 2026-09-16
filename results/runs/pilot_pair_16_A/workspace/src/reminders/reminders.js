const express = require('express');
const router = express.Router();
// Store for Reminders
const reminders = new Map();
// Example UUID generation for simplicity
const generateUUID = () => Math.random().toString(36).substring(2, 15);

// Create a new Reminder
router.post('/api/reminders', (req, res) => {
  const { todo_id, reminder_datetime } = req.body;
  const id = generateUUID();

  // For simplicity, the date validation is not included in reminder_datetime.
  const reminder = { id, todo_id, reminder_datetime, notified: false };
  reminders.set(id, reminder);
  res.status(201).json(reminder);
});

module.exports = router;