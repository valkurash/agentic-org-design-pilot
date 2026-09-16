const express = require('express');
const nodemailer = require('nodemailer');
const { requireAuth } = require('../auth/middleware');

const router = express.Router();

// Email setup
const transporter = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: 'your-email@gmail.com',
    pass: 'your-email-password',
  },
});

// Send Reminder
router.post('/api/reminders', requireAuth, (req, res) => {
  const { email, reminderDatetime, message } = req.body;
  const reminderTime = new Date(reminderDatetime);

  setTimeout(() => {
    const mailOptions = {
      from: 'your-email@gmail.com',
      to: email,
      subject: 'Reminder Notification',
      text: message,
    };

    transporter.sendMail(mailOptions, (error, info) => {
      if (error) {
        return console.log(error);
      }
      console.log('Email sent: ' + info.response);
    });
  }, reminderTime - new Date());

  res.status(200).json({ message: 'Reminder scheduled' });
});

module.exports = router;