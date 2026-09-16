const express = require('express');
const { requireAuth } = require('../../auth/middleware');
const router = express.Router();

// Mock data for example
let todos = [];

// Create a new TODO item
router.post('/api/todos', requireAuth, (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: todos.length + 1,
        title,
        description,
        completed: false,
        created_at: new Date(),
        updated_at: new Date()
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// List all TODO items
router.get('/api/todos', requireAuth, (req, res) => {
    res.json(todos);
});

// Delete a TODO item
router.delete('/api/todos/:id', requireAuth, (req, res) => {
    const { id } = req.params;
    todos = todos.filter(todo => todo.id !== parseInt(id));
    res.status(204).send();
});

module.exports = router;
