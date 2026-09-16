const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const { isValidISO8601 } = require('../utils/dateValidationISO');

// Temporary in-memory storage
const reminders = [];

// Create a reminder
router.post('/reminders', (req, res) => {
  const { todo_id, reminder_datetime } = req.body;
  if (!isValidISO8601(reminder_datetime)) {
    return res.status(400).send({ message: 'Invalid datetime format' });
  }
  const newReminder = {
    id: uuidv4(),
    todo_id,
    reminder_datetime,
    notified: false
  };
  reminders.push(newReminder);
  console.log(`Reminder created for TODO ${todo_id} at ${reminder_datetime}`);
  res.status(201).json(newReminder);
});

module.exports = router;
