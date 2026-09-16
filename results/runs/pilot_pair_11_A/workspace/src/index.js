const express = require('express');
const app = express();
const bodyParser = require('body-parser');

// Middleware for parsing JSON bodies
app.use(bodyParser.json());

// Importing route controllers
const todosController = require('./todos/todosController');
const remindersController = require('./reminders/remindersController');

// Use the route controllers
app.use('/api/todos', todosController);
app.use('/api/reminders', remindersController);

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});