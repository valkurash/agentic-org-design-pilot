const express = require('express');
const todoController = require('./todos/todoController');
const reminderController = require('./reminders/reminderController');
const authMiddleware = require('../auth/middleware');

const app = express();
app.use(express.json());

app.get('/api/todos', authMiddleware, todoController.getTodos);
app.post('/api/todos', authMiddleware, todoController.createTodo);
app.delete('/api/todos/:id', authMiddleware, todoController.deleteTodo);
app.post('/api/reminders', authMiddleware, reminderController.createReminder);

module.exports = app;
