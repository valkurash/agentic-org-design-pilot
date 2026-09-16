const db = require('../db');
const io = require('socket.io')(3000);

async function createReminder(data) {
  const { todoId, reminderDatetime } = data;
  const result = await db.query(
    'UPDATE todos SET reminder_datetime = $1 WHERE id = $2 RETURNING *',
    [reminderDatetime, todoId]
  );
  scheduleNotification(todoId, reminderDatetime);
  return result.rows[0];
}

function scheduleNotification(todoId, reminderDatetime) {
  const now = new Date();
  const delay = new Date(reminderDatetime) - now;
  if (delay > 0) {
    setTimeout(() => triggerInAppNotification(todoId), delay);
  }
}

function triggerInAppNotification(todoId) {
  io.emit('reminder', { todoId });
}

module.exports = {
  createReminder,
};
