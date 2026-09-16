const express = require('express');
const router = express.Router();

// Create a reminder with datetime
router.post('/api/reminders', (req, res) => {
  const { reminderDatetime } = req.body;
  if (!isValidISO8601Datetime(reminderDatetime)) {
    return res.status(400).send('Invalid datetime format');
  }
  res.send('Reminder scheduled');
});

// Function to validate ISO-8601 datetime
function isValidISO8601Datetime(value) {
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([+-]\d{2}:\d{2}|Z)$/.test(value);
}

module.exports = router;
