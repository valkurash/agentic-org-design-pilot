const express = require('express');
const router = express.Router();

// Middleware for authentication
const { requireAuth } = require('../../auth/middleware');

// Placeholder for storing TODOs in memory
const todos = new Map();

// Create a TODO
router.post('/api/todos', requireAuth, (req, res) => {
    const { title, description } = req.body;
    const id = generateUUID();
    const newTodo = {
        id,
        title,
        description,
        completed: false,
        created_at: new Date(),
        updated_at: new Date()
    };
    todos.set(id, newTodo);
    res.status(201).json(newTodo);
});

// List all TODOs
router.get('/api/todos', requireAuth, (req, res) => {
    res.json(Array.from(todos.values()));
});

// Delete a TODO
router.delete('/api/todos/:id', requireAuth, (req, res) => {
    const { id } = req.params;
    if (todos.has(id)) {
        todos.delete(id);
        res.status(204).send();
    } else {
        res.status(404).send('TODO not found');
    }
});

// Helper function to generate UUID
function generateUUID() {
    // Placeholder UUID generation
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

module.exports = router;