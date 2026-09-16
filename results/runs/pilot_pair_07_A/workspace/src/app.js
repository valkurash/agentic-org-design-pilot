const express = require('express');
const session = require('express-session');
const todoController = require('./todos/todoController');
const reminderController = require('./reminders/reminderController');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true,
}));

// Use controllers
app.use(todoController);
app.use(reminderController);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
