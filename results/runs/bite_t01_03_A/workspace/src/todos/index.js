const express = require('express');
const router = express.Router();

// Mock database
let todos = [];

// Middleware to validate the TODO request
function validateTodoRequest(req, res, next) {
    const { title, description } = req.body;
    if (!title || typeof title !== 'string') {
        return res.status(400).json({ error: 'Title is required and must be a string.' });
    }
    if (description && typeof description !== 'string') {
        return res.status(400).json({ error: 'Description must be a string.' });
    }
    next();
}

// Create TODO
router.post('/', validateTodoRequest, (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: todos.length + 1,
        title,
        description,
        status: 'Pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: req.user.id // Assume req.user is populated by auth middleware
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// Get all TODOs
router.get('/', (req, res) => {
    res.json(todos.filter(todo => todo.user_id === req.user.id));
});

// Delete TODO by ID
router.delete('/:id', (req, res) => {
    const { id } = req.params;
    todos = todos.filter(todo => todo.id !== Number(id) || todo.user_id !== req.user.id);
    res.status(204).end();
});

module.exports = router;
