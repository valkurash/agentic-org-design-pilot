const express = require('express');
const router = express.Router();
const { validateSession } = require('../auth/session');
const { createReminder, triggerInAppNotification } = require('./reminder.service');

// Middleware to validate session
router.use(validateSession);

// POST /api/reminders
router.post('/', async (req, res) => {
  try {
    const reminder = await createReminder(req.body);
    res.status(201).send(reminder);
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
});

module.exports = router;
