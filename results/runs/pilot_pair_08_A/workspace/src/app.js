const express = require('express');
const bodyParser = require('body-parser');
const todoController = require('./todos/todo.controller');
const reminderController = require('./reminders/reminder.controller');

const app = express();
app.use(bodyParser.json());

// Use controllers
app.use(todoController);
app.use(reminderController);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
