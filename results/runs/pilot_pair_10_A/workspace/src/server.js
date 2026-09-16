const express = require('express');
const app = express();
const session = require('./auth/middleware');
const todosRouter = require('./todos/todosController');
const remindersRouter = require('./reminders/remindersController');

app.use(express.json()); 
app.use(session);

app.use('/api/todos', todosRouter);
app.use('/api/reminders', remindersRouter);

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

module.exports = app;
