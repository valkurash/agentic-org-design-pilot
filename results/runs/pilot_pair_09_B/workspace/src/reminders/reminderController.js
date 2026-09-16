const express = require('express');
const { v4: uuidv4 } = require('uuid');
let reminders = [];

const createReminder = (req, res) => {
  const { todo_id, reminder_time } = req.body;
  const newReminder = {
    id: uuidv4(),
    todo_id,
    reminder_time: new Date(reminder_time),
    notification_sent: false
  };
  reminders.push(newReminder);
  res.status(201).json(newReminder);
};

module.exports = { createReminder };
