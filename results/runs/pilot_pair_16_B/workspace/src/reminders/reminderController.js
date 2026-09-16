const express = require('express');
const Reminder = require('./reminderModel');
const { isValidDate } = require('../utils/dateValidation');
const router = express.Router();

const reminders = new Map();

router.post('/', (req, res) => {
  const { todo_id, reminder_date } = req.body;
  if (!isValidDate(reminder_date)) {
    return res.status(400).json({ error: 'Invalid date format. Expecting YYYY-MM-DD.' });
  }
  const reminder = new Reminder(todo_id, reminder_date);
  reminders.set(reminder.id, reminder);
  // To deliver notifications, we'd include the logic here
  res.status(201).json(reminder);
});

module.exports = router;
