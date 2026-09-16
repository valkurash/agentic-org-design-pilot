const express = require('express');
const { createTodo, listTodos, deleteTodo } = require('./todos/todoController');
const { createReminder } = require('./reminders/reminderController');

const app = express();
app.use(express.json());

const RATE_LIMIT = 100;
app.use((req, res, next) => {
  let requestCount = 0;
  const startTime = Date.now();
  requestCount += 1;
  if (requestCount > RATE_LIMIT) {
    if (Date.now() - startTime < 1000) {
      return res.status(503).json({ message: 'Rate limit exceeded' });
    } else {
      requestCount = 0;
    }
  }
  next();
});

// TODO routes
app.post('/api/todos', createTodo);
app.get('/api/todos', listTodos);
app.delete('/api/todos/:id', deleteTodo);

// Reminder route
app.post('/api/reminders', createReminder);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

module.exports = app;