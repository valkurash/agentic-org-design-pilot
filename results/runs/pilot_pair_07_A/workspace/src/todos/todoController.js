const express = require('express');
const router = express.Router();

// Mock Database (Array for simplicity)
let todos = [];

// Create a new TODO
router.post('/api/todos', (req, res) => {
    const { title, description, reminderDatetime } = req.body;
    const newTodo = {
        id: (todos.length + 1).toString(),
        title,
        description,
        isCompleted: false,
        reminderDatetime
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// List all TODOs
router.get('/api/todos', (req, res) => {
    res.status(200).json(todos);
});

// Delete a TODO
router.delete('/api/todos/:id', (req, res) => {
    const todoId = req.params.id;
    todos = todos.filter(todo => todo.id !== todoId);
    res.status(200).json({ message: 'TODO deleted successfully' });
});

module.exports = router;
