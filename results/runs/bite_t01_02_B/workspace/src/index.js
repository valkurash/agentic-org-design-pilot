const express = require('express');
const app = express();
const todosController = require('./todos/todosController');
const remindersController = require('./reminders/remindersController');

app.use(express.json());
app.use(todosController);
app.use(remindersController);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
