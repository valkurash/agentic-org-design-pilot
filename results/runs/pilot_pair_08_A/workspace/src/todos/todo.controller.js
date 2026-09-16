const express = require('express');
// Session middleware
const { requireAuth } = require('../auth/middleware');

const router = express.Router();

// TODO model
const TODO_ITEMS = [];

// Create TODO
router.post('/api/todos', requireAuth, (req, res) => {
  const { title, description, reminderDatetime } = req.body;
  const newTodo = {
    id: TODO_ITEMS.length + 1, // This should be a UUID in practice
    title,
    description,
    isCompleted: false,
    reminderDatetime: reminderDatetime ? new Date(reminderDatetime) : null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
  TODO_ITEMS.push(newTodo);
  res.status(201).json(newTodo);
});

// List TODOs
router.get('/api/todos', requireAuth, (req, res) => {
  res.status(200).json(TODO_ITEMS);
});

// Delete TODO
router.delete('/api/todos/:id', requireAuth, (req, res) => {
  const { id } = req.params;
  const index = TODO_ITEMS.findIndex((item) => item.id === parseInt(id));
  if (index >= 0) {
    TODO_ITEMS.splice(index, 1);
    res.status(204).send();
  } else {
    res.status(404).json({ message: 'TODO item not found' });
  }
});

module.exports = router;