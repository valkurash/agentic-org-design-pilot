const NotificationService = require('./notificationService');

class ReminderService {
    static async createReminder(todoId, reminder_datetime) {
        // Logic to create reminder
        // This can include storing the reminder in the database
        return { todoId, reminder_datetime };
    }

    static async scheduleReminder(todoId, reminder_datetime) {
        // Logic to schedule a reminder using in-memory scheduler
        const delay = new Date(reminder_datetime) - new Date();
        if (delay > 0) {
            setTimeout(() => {
                NotificationService.sendNotification(todoId);
            }, delay);
        }
    }
}

module.exports = ReminderService;
