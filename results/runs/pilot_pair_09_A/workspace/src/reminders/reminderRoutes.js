const express = require('express');
const { addReminder } = require('./reminderController');
const { ensureAuthenticated } = require('../../auth/middleware');

const router = express.Router();

router.use(ensureAuthenticated);
router.post('/reminders', addReminder);

module.exports = router;