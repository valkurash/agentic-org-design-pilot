const express = require('express');
const session = require('express-session');
const app = express();

const authenticate = require('./auth/middleware');
const todosRouter = require('./todos');
const remindersRouter = require('./reminders');

app.use(express.json());
app.use(session({ secret: 'your-secret-key', resave: false, saveUninitialized: true }));
app.use(authenticate);
app.use(todosRouter);
app.use(remindersRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
