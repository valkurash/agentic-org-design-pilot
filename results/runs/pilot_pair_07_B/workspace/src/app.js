const express = require('express');
const app = express();
const todosRouter = require('./todos/todosController.js');
const remindersRouter = require('./reminders/remindersController.js');
const sessionMiddleware = require('./middleware/session.js');

app.use(express.json());
app.use(sessionMiddleware);

app.use('/api/todos', todosRouter);
app.use('/api/reminders', remindersRouter);

// Rate limiter middleware to handle 100 req/s
const rateLimit = require('express-rate-limit');
const limiter = rateLimit({
  windowMs: 1000, // 1 second
  max: 100,       // limit each IP to 100 requests per windowMs
});
app.use(limiter);

module.exports = app;
