const express = require('express');
const app = express();
const todosRouter = require('./todos/todo');
const remindersRouter = require('./reminders/reminder');
const rateLimit = require('express-rate-limit');

const apiLimiter = rateLimit({
    windowMs: 1000, // 1 second
    max: 100 // limit each IP to 100 requests per windowMs
});

app.use(express.json());
app.use(apiLimiter);
app.use(todosRouter);
app.use(remindersRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});