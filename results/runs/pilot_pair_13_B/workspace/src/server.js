const express = require('express');
const app = express();
const todosRouter = require('./todos');
const remindersRouter = require('./reminders');
const sessionAuth = require('./middleware/sessionAuth');

const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});

app.use(express.json());
app.use(limiter);
app.use('/api/todos', todosRouter);
app.use('/api/reminders', sessionAuth, remindersRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
