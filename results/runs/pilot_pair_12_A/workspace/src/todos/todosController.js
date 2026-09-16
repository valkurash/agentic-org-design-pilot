const express = require('express');
const router = express.Router();
const { isValidDate } = require('../utils/dateValidation');

// Middleware for requiring authentication
const { requireAuth } = require('../../auth/middleware');

let todos = []; // This will be our in-memory "database" for demonstration purposes

router.post('/api/todos', requireAuth, (req, res) => {
  const { title, description, reminder_datetime } = req.body;
  
  // Check for valid date
  if (reminder_datetime && !isValidDate(reminder_datetime.split('T')[0])) {
    return res.status(400).json({ error: "Invalid date format" });
  }

  const newTodo = {
    id: `${Date.now()}`,
    title,
    description,
    is_completed: false,
    reminder_datetime: reminder_datetime || null,
  };

  todos.push(newTodo);
  res.status(201).json(newTodo);
});

router.get('/api/todos', requireAuth, (req, res) => {
  res.json(todos);
});

router.delete('/api/todos/:id', requireAuth, (req, res) => {
  const { id } = req.params;
  todos = todos.filter(todo => todo.id !== id);
  res.status(204).send();
});

router.post('/api/reminders', requireAuth, (req, res) => {
  const { todo_id, datetime } = req.body;
  const todo = todos.find(t => t.id === todo_id);

  if (!todo) {
    return res.status(404).json({ error: "Todo not found" });
  }

  // Update the reminder date
  if (datetime && isValidDate(datetime.split('T')[0])) {
    todo.reminder_datetime = datetime;
    return res.status(200).json(todo);
  }

  return res.status(400).json({ error: "Invalid date format" });
});

module.exports = router;
