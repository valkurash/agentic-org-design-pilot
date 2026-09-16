const express = require('express');
const router = express.Router();
const { isValidDate } = require('../utils/dateValidation');
// Store for TODOs
const todos = new Map();
// Example UUID generation for simplicity
const generateUUID = () => Math.random().toString(36).substring(2, 15);

// Create a new TODO
router.post('/api/todos', (req, res) => {
  const { title, description, completed = false, created_at = new Date().toISOString(), updated_at = created_at } = req.body;
  const id = generateUUID();
  const todo = { id, title, description, completed, created_at, updated_at };

  if (isValidDate(created_at.split('T')[0])) {
    todos.set(id, todo);
    res.status(201).json(todo);
  } else {
    res.status(400).json({ error: 'Invalid date format' });
  }
});

// List all TODOs
router.get('/api/todos', (req, res) => {
  res.json(Array.from(todos.values()));
});

// Delete a TODO by id
router.delete('/api/todos/:id', (req, res) => {
  const { id } = req.params;
  if (todos.has(id)) {
    todos.delete(id);
    res.status(204).end();
  } else {
    res.status(404).json({ error: 'TODO not found' });
  }
});

module.exports = router;