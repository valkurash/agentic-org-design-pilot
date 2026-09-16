const checkReminders = () => {
  const now = new Date().toISOString();
  reminders.forEach(reminder => {
    if (!reminder.notified && reminder.reminder_datetime <= now) {
      // Notification logic goes here, e.g., send an email or push notification
      console.log(`Reminder for todo: ${reminder.todo_id} is due!`);
      reminder.notified = true;
    }
  });
};

setInterval(checkReminders, 60000); // Check every minute

module.exports = { checkReminders };