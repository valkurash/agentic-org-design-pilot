const express = require('express');
const router = express.Router();
const { requireAuth } = require('../../auth/middleware');
const { v4: uuidv4 } = require('uuid');

// In-memory storage for simplicity
const todos = [];

router.post('/api/todos', requireAuth, (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: uuidv4(),
        title,
        description,
        completed: false,
        created_at: new Date(),
        updated_at: new Date()
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

router.get('/api/todos', requireAuth, (req, res) => {
    res.status(200).json(todos);
});

router.delete('/api/todos/:id', requireAuth, (req, res) => {
    const todoIndex = todos.findIndex(todo => todo.id === req.params.id);
    if (todoIndex === -1) {
        return res.status(404).send('TODO not found');
    }
    todos.splice(todoIndex, 1);
    res.status(204).send();
});

module.exports = router;
