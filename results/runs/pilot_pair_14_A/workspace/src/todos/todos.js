const express = require('express');
const { v4: uuidv4 } = require('uuid');
const router = express.Router();

let todos = [];

// POST /api/todos
router.post('/api/todos', (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: uuidv4(),
        title,
        description,
        completed: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// GET /api/todos
router.get('/api/todos', (req, res) => {
    res.json(todos);
});

// DELETE /api/todos/:id
router.delete('/api/todos/:id', (req, res) => {
    const todoId = req.params.id;
    todos = todos.filter(todo => todo.id !== todoId);
    res.status(204).send();
});

module.exports = router;
