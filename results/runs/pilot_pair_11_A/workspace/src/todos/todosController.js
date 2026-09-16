const express = require('express');
const router = express.Router();

// Middleware to ensure user authentication
const authMiddleware = require('../auth/middleware');

// Simulating a database with todo items
let todoItems = [];

// POST /api/todos - Create a new TODO item
router.post('/', authMiddleware, (req, res) => {
    const { title, description } = req.body;
    const newItem = {
        id: Date.now().toString(),
        userId: req.session.userId,
        title,
        description,
        created_at: new Date(),
        updated_at: new Date(),
    };
    todoItems.push(newItem);
    res.status(201).json(newItem);
});

// GET /api/todos - Read all TODO items for authenticated user
router.get('/', authMiddleware, (req, res) => {
    const userTodos = todoItems.filter(item => item.userId === req.session.userId);
    res.status(200).json(userTodos);
});

// DELETE /api/todos/:id - Delete a TODO item
router.delete('/:id', authMiddleware, (req, res) => {
    const { id } = req.params;
    const userId = req.session.userId;
    todoItems = todoItems.filter(item => item.id !== id || item.userId !== userId);
    res.status(204).send();
});

module.exports = router;