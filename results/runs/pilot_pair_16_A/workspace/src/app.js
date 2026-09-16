const express = require('express');
const todosRouter = require('./todos/todos');
const remindersRouter = require('./reminders/reminders');

const app = express();
app.use(express.json());

// TODO and Reminder routers
app.use(todosRouter);
app.use(remindersRouter);

// Error handler might be expanded in real setup
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});

module.exports = app;