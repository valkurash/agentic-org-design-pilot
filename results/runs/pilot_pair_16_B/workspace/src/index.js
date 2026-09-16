const express = require('express');
const session = require('../auth/middleware');
const todoRoutes = require('./todos/todoController');
const reminderRoutes = require('./reminders/reminderController');

const app = express();

app.use(express.json());
app.use(session.requireAuth);

app.use('/api/todos', todoRoutes);
app.use('/api/reminders', reminderRoutes);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}.`);
});
