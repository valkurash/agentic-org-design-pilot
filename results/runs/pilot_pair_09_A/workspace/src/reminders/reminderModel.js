class Reminder {
  constructor(todoId, reminderTime) {
    this.todo_id = todoId;
    this.reminder_time = new Date(reminderTime);
    this.triggered = false;
  }

  trigger() {
    this.triggered = true;
  }
}

module.exports = Reminder;