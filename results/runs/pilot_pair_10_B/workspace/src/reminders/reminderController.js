const reminders = [];

function createReminder(req, res) {
  const { todoId, scheduledTime } = req.body;
  const newReminder = {
    reminderId: String(reminders.length + 1),
    todoId,
    scheduledTime: new Date(scheduledTime)
  };
  reminders.push(newReminder);
  res.status(201).json(newReminder);
}

module.exports = { createReminder };