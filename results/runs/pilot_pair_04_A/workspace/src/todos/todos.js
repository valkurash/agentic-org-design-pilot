const express = require('express');
const router = express.Router();
const TodoService = require('./todoService');

// Middleware for authentication
const authMiddleware = require('../../auth/middleware');

// Apply authentication middleware
router.use(authMiddleware);

// Create TODO item
router.post('/api/todos', async (req, res) => {
    try {
        const { title, due_date, reminder_datetime } = req.body;
        const todo = await TodoService.createTodo(title, due_date, reminder_datetime);
        res.status(201).json(todo);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// List TODO items
router.get('/api/todos', async (req, res) => {
    try {
        const todos = await TodoService.getTodos();
        res.json(todos);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Delete TODO item
router.delete('/api/todos/:id', async (req, res) => {
    try {
        const { id } = req.params;
        await TodoService.deleteTodo(id);
        res.status(204).send();
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
