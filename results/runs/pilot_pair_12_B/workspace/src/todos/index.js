const express = require('express');
const router = express.Router();

// Create a new TODO
router.post('/api/todos', (req, res) => {
  res.send('Create TODO');
});

// List all TODOs
router.get('/api/todos', (req, res) => {
  res.send('List TODOs');
});

// Delete a TODO by ID
router.delete('/api/todos/:id', (req, res) => {
  res.send(`Delete TODO with id ${req.params.id}`);
});

module.exports = router;
