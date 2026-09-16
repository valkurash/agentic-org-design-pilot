const express = require('express');
const sessionMiddleware = require('../auth/middleware');
const todosRouter = require('./todos');
const remindersRouter = require('./reminders');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());
app.use(sessionMiddleware);

app.use(todosRouter);
app.use(remindersRouter);

// Rate limiting middleware
let requestCounts = {};
setInterval(() => {
  requestCounts = {}; // reset every second
}, 1000);

app.use((req, res, next) => {
  const ip = req.ip;
  requestCounts[ip] = (requestCounts[ip] || 0) + 1;
  if (requestCounts[ip] > 100) {
    res.status(429).send('Rate limit exceeded');
  } else {
    next();
  }
});

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
