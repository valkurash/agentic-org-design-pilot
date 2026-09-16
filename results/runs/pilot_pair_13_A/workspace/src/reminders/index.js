const express = require('express');
const router = express.Router();
const nodemailer = require('nodemailer');
const { isValidDate } = require('../utils/dateValidation');

// Your existing authentication middleware
const { requireAuth } = require('../../auth/middleware');

// Placeholder for reminder logic
// POST /api/reminders
router.post('/', requireAuth, (req, res) => {
  const { todoId, reminder } = req.body;
  // Logic to add a reminder
  if (!isValidDate(reminder)) {
    return res.status(400).send({ error: 'Invalid date format' });
  }
  
  // Logic for setting up email notification (simplified)
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    }
  });

  const mailOptions = {
    from: process.env.EMAIL_USER,
    to: 'user@example.com', // would be dynamically set in a real app
    subject: 'Reminder Notification',
    text: 'This is your reminder notification.'
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      return res.status(500).send({ error: 'Failed to send email' });
    } else {
      res.status(200).send({ message: 'Reminder set and email sent' });
    }
  });
});

module.exports = router;