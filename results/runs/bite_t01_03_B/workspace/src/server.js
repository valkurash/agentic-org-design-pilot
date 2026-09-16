const express = require('express');
const app = express();
const todoController = require('./todos/todoController');
const reminderController = require('./reminders/reminderController');

app.use(express.json());
app.use('/api/todos', todoController);
app.use('/api/reminders', reminderController);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});