const express = require('express');
const router = express.Router();

// TODO items storage simulation
let todos = [];

// Create TODO route
router.post('/todos', (req, res) => {
    const { title, description } = req.body;
    const newTodo = {
        id: (todos.length + 1).toString(),
        user_id: req.session.userId, // getting user id from session
        title,
        description,
        created_at: new Date(),
        completed: false
    };
    todos.push(newTodo);
    res.status(201).json(newTodo);
});

// List all TODOs route
router.get('/todos', (req, res) => {
    res.json(todos.filter(todo => todo.user_id === req.session.userId));
});

// Complete a TODO route (not directly part of DELETE, assuming update for completion)
router.patch('/todos/:id', (req, res) => {
    const { id } = req.params;
    const todo = todos.find(t => t.id === id && t.user_id === req.session.userId);
    if (todo) {
        todo.completed = true;
        res.json(todo);
    } else {
        res.status(404).json({ message: 'TODO not found' });
    }
});

// Delete TODO route
router.delete('/todos/:id', (req, res) => {
    const { id } = req.params;
    const todoIndex = todos.findIndex(t => t.id === id && t.user_id === req.session.userId);
    if (todoIndex !== -1) {
        todos.splice(todoIndex, 1);
        res.status(204).send();
    } else {
        res.status(404).json({ message: 'TODO not found' });
    }
});

module.exports = router;
