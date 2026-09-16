import { db } from '../db';

export const addReminder = async (reminderData) => {
  const { rows } = await db.query(
    'INSERT INTO reminders (todo_id, reminder_time) VALUES ($1, $2) RETURNING *',
    [reminderData.todo_id, reminderData.reminder_time]
  );
  return rows[0];
};

const checkReminders = async () => {
  const { rows } = await db.query(
    'SELECT * FROM reminders WHERE reminder_time <= NOW()'
  );
  return rows;
};

setInterval(async () => {
  const dueReminders = await checkReminders();
  dueReminders.forEach(reminder => {
    console.log(`Triggering reminder for TODO ID ${reminder.todo_id}`);
    // Logic for triggering in-app notifications
  });
}, 60000);
