const TodoRepository = require('./todoRepository');
const ReminderService = require('../reminders/reminderService');

class TodoService {
    static async createTodo(title, due_date, reminder_datetime) {
        const todo = await TodoRepository.create(title, due_date, reminder_datetime);
        if (reminder_datetime) {
            await ReminderService.scheduleReminder(todo.id, reminder_datetime);
        }
        return todo;
    }

    static async getTodos() {
        return await TodoRepository.findAll();
    }

    static async deleteTodo(id) {
        await TodoRepository.delete(id);
    }
}

module.exports = TodoService;
