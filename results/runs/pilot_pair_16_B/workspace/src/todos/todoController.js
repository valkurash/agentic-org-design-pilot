const express = require('express');
const Todo = require('./todoModel');
const router = express.Router();

const todos = new Map();

router.post('/', (req, res) => {
  const { title, description } = req.body;
  const todo = new Todo(title, description);
  todos.set(todo.id, todo);
  res.status(201).json(todo);
});

router.get('/', (req, res) => {
  res.json(Array.from(todos.values()));
});

router.delete('/:id', (req, res) => {
  const { id } = req.params;
  if (todos.has(id)) {
    todos.delete(id);
    res.sendStatus(204);
  } else {
    res.sendStatus(404);
  }
});

module.exports = router;
