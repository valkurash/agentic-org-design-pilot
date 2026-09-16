const Reminder = require('./reminderModel');

let reminders = [];

const addReminder = (req, res) => {
  const { todoId, reminderTime } = req.body;
  if (!todoId || !reminderTime) {
    return res.status(400).json({ error: 'Todo ID and reminder time are required.' });
  }
  const reminder = new Reminder(todoId, reminderTime);
  reminders.push(reminder);
  res.status(201).json(reminder);
};

module.exports = { addReminder };