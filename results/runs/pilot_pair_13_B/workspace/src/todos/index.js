const express = require('express');
const router = express.Router();

let todos = [];

router.post('/', (req, res) => {
  // Assuming body contains title, description, and reminder
  const { title, description, reminder } = req.body;
  const newTodo = {
    id: require('crypto').randomUUID(),
    title,
    description,
    isCompleted: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    reminder: {
      reminderTime: reminder,
      isNotified: false
    }
  };
  todos.push(newTodo);
  res.status(201).json(newTodo);
});

router.get('/', (req, res) => {
  res.json(todos);
});

router.delete('/:id', (req, res) => {
  const { id } = req.params;
  todos = todos.filter(todo => todo.id !== id);
  res.status(204).end();
});

module.exports = router;
