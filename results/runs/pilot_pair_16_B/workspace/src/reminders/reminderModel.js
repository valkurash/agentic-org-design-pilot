const { v4: uuidv4 } = require('uuid');

class Reminder {
  constructor(todo_id, reminder_datetime) {
    this.id = uuidv4();
    this.todo_id = todo_id;
    this.reminder_datetime = new Date(reminder_datetime);
    this.notified = false;
  }

  markNotified() {
    this.notified = true;
  }
}

module.exports = Reminder;
