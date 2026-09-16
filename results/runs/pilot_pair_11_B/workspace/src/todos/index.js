const express = require('express');
const router = express.Router();

let todos = [];

// CREATE TODO
router.post('/api/todos', (req, res) => {
  const { title, description, reminder_datetime } = req.body;
  const newTodo = {
    id: generateUUID(),
    title,
    description,
    completed: false,
    reminder_datetime,
    user_id: req.user.id,
  };
  todos.push(newTodo);
  res.status(201).json(newTodo);
});

// LIST TODOS
router.get('/api/todos', (req, res) => {
  res.json(todos.filter(todo => todo.user_id === req.user.id));
});

// COMPLETE TODO
router.post('/api/todos/:id/complete', (req, res) => {
  const todo = todos.find(t => t.id === req.params.id && t.user_id === req.user.id);
  if (todo) {
    todo.completed = true;
    res.status(200).json(todo);
  } else {
    res.status(404).send('Todo not found');
  }
});

// DELETE TODO
router.delete('/api/todos/:id', (req, res) => {
  todos = todos.filter(t => !(t.id === req.params.id && t.user_id === req.user.id));
  res.status(204).send();
});

function generateUUID() {
  // Mock UUID generator
  return Math.random().toString(36).substr(2, 9);
}

module.exports = router;
