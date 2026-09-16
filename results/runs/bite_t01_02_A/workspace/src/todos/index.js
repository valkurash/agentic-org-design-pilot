const express = require('express');
const { v4: uuidv4 } = require('uuid');

const router = express.Router();

let todos = [];

// Create TODO Item
router.post('/api/todos', (req, res) => {
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

// List TODO Items
router.get('/api/todos', (req, res) => {
    res.json(todos);
});

// Delete TODO Item
router.delete('/api/todos/:id', (req, res) => {
    const { id } = req.params;
    todos = todos.filter(todo => todo.id !== id);
    res.status(204).send();
});

module.exports = router;
