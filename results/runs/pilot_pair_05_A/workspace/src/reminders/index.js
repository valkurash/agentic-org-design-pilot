const express = require('express');
const router = express.Router();
const { createReminder } = require('./service');

router.post('/reminders', createReminder);

module.exports = router;