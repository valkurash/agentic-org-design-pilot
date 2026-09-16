const express = require('express');
const nodemailer = require('nodemailer');
const router = express.Router();

// Placeholder reminder checks
setInterval(() => {
  // Logic to check reminders and send notifications.
}, 60 * 1000);

async function sendEmail(reminderMessage) {
  let transporter = nodemailer.createTransport({
    service: 'gmail', // Example using Gmail
    auth: {
      user: 'your-email@gmail.com',
      pass: 'your-email-password'
    }
  });

  let info = await transporter.sendMail({
    from: 'your-email@gmail.com',
    to: 'user-email@gmail.com',
    subject: 'TODO Reminder',
    text: reminderMessage
  });

  console.log('Email sent: ' + info.response);
}

router.post('/', (req, res) => {
  // Endpoint for reminder creation - Placeholder
  res.status(201).json({ message: 'Reminder set successfully' });
});

module.exports = router;
