const express = require('express');
const router = express.Router();

// Middleware simulation for authentication placeholder
function isAuthenticated(req, res, next) {
    // Simulate authentication check
    console.log('Auth middleware invoked');
    return next();
}

// TODO items data storage
const todos = [];

// Create a new TODO
router.post('/', isAuthenticated, (req, res) => {
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

// List all TODOs
router.get('/', isAuthenticated, (req, res) => {
    res.json(todos);
});

// Mark a TODO as complete
router.patch('/:id', isAuthenticated, (req, res) => {
    const { id } = req.params;
    const todo = todos.find(t => t.id === parseInt(id));
    if (!todo) return res.status(404).send('Todo not found');
    todo.completed = true;
    todo.updated_at = new Date();
    res.json(todo);
});

// Delete a TODO
router.delete('/:id', isAuthenticated, (req, res) => {
    const { id } = req.params;
    const index = todos.findIndex(t => t.id === parseInt(id));
    if (index === -1) return res.status(404).send('Todo not found');
    const deletedTodo = todos.splice(index, 1);
    res.json(deletedTodo);
});

module.exports = router;
