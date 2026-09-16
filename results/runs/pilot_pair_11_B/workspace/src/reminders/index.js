const express = require('express');
const nodemailer = require('nodemailer');
const router = express.Router();

let reminders = [];

// POST REMINDER
router.post('/api/reminders', (req, res) => {
  const { todo_id, reminder_datetime } = req.body;
  if (!isValidISODateTime(reminder_datetime)) {
    return res.status(400).send('Invalid datetime format');
  }
  const reminder = {
    id: generateUUID(),
    todo_id,
    reminder_datetime,
    user_id: req.user.id,
    scheduled: false,
  };
  reminders.push(reminder);
  // Schedule notification logic
  scheduleNotification(reminder);
  res.status(201).json(reminder);
});

function scheduleNotification(reminder) {
  const timeUntilReminder = new Date(reminder.reminder_datetime) - Date.now();
  if (timeUntilReminder > 0) {
    setTimeout(() => {
      sendEmailNotification(reminder);
    }, timeUntilReminder);
  }
}

function sendEmailNotification(reminder) {
  // Configure transport
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: 'example@gmail.com',
      pass: 'password',
    },
  });

  const mailOptions = {
    from: 'example@gmail.com',
    to: 'user@example.com',
    subject: 'Reminder Notification',
    text: 'Your reminder is due now!',
  };

  transporter.sendMail(mailOptions, (error, info) => {
    if (error) {
      console.log('Error sending email:', error);
    } else {
      console.log('Email sent:', info.response);
    }
  });
}

function isValidISODateTime(value) {
  const isoFormat = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$/;
  return isoFormat.test(value);
}

function generateUUID() {
  return Math.random().toString(36).substr(2, 9);
}

module.exports = router;
