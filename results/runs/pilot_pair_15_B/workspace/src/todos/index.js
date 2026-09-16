const express = require('express');
const router = express.Router();

// TODo CRUD Handlers
// Memory storage for todos (this would be replaced by a real database in production)
let todos = [];

// Create a new TODO
router.post('/api/todos', (req, res) => {
    const newTodo = {
        id: generateUUID(),
        title: req.body.title,
        description: req.body.description || '',
        completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// List all TODOs
router.get('/api/todos', (req, res) => {
    res.json(todos);
});

// Delete a TODO by ID
router.delete('/api/todos/:id', (req, res) => {
    const { id } = req.params;
    todos = todos.filter(todo => todo.id !== id);
    res.status(204).send();
});

// UUID generator for simplicity, you might want to replace with a library like uuid
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

module.exports = router;
