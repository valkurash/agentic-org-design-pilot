const express = require('express');
const router = express.Router();

// Dummy data store (use a database in production)
const todos = [];

// Create a new TODO
router.post('/', (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: generateUUID(),
        title,
        description,
        completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// List all TODOs
router.get('/', (req, res) => {
    res.status(200).json(todos);
});

// Delete a TODO by ID
router.delete('/:id', (req, res) => {
    const { id } = req.params;
    const index = todos.findIndex(todo => todo.id === id);
    if (index !== -1) {
        todos.splice(index, 1);
        return res.status(204).send();
    }
    res.status(404).json({ error: 'TODO not found' });
});

function generateUUID() {
    // Simplified UUID generation for illustration
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

module.exports = router;
