const express = require('express');
const router = express.Router();
const { v4: uuidv4 } = require('uuid');

// Temporary in-memory storage
const todos = [];

// Create a TODO item
router.post('/todos', (req, res) => {
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

// List all TODO items
router.get('/todos', (req, res) => {
  res.status(200).json(todos);
});

// Delete a TODO item
router.delete('/todos/:id', (req, res) => {
  const { id } = req.params;
  const index = todos.findIndex(todo => todo.id === id);
  if (index !== -1) {
    todos.splice(index, 1);
    res.status(200).send({ message: 'TODO item deleted' });
  } else {
    res.status(404).send({ message: 'TODO item not found' });
  }
});

module.exports = router;
