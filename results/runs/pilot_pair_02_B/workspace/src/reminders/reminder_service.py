
from datetime import datetime

class ReminderService:
    def __init__(self, db_session, notification_service):
        self.db_session = db_session
        self.notification_service = notification_service

    def trigger_reminder(self):
        # Fetch reminders that need to be triggered
        reminders = self.db_session.query(Reminder).filter_by(is_triggered=False).all()
        for reminder in reminders:
            if reminder.reminder_datetime <= datetime.now():
                # Send notification
                todo = self.db_session.query(TODOItem).filter_by(id=reminder.todo_id).first()
                user_id = todo.user_id
                message = f"Reminder: {todo.description}"
                self.notification_service.send_notification(user_id, message)
                reminder.is_triggered = True
                # Update reminder as triggered
                self.db_session.commit()