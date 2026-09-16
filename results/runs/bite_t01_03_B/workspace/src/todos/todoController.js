const express = require('express');
const { v4: uuidv4 } = require('uuid');
const router = express.Router();

let todos = [];

// Middleware
const requireAuth = require('../../auth/middleware').requireAuth;

// Create a new TODO
router.post('/', requireAuth, (req, res) => {
    const { title, description } = req.body;
    if (!title || !description) {
        return res.status(400).json({ error: 'Title and description are required' });
    }

    const todo = {
        id: uuidv4(),
        title,
        description,
        completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
    };
    todos.push(todo);
    res.status(201).json(todo);
});

// Get list of TODOs
router.get('/', requireAuth, (req, res) => {
    res.status(200).json(todos);
});

// Delete a TODO by ID
router.delete('/:id', requireAuth, (req, res) => {
    const { id } = req.params;
    const index = todos.findIndex(todo => todo.id === id);
    if (index === -1) {
        return res.status(404).json({ error: 'TODO not found' });
    }
    todos.splice(index, 1);
    res.status(204).send();
});

module.exports = router;