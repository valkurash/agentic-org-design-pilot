const express = require('express');
const rateLimit = require('express-rate-limit');

const todosRouter = require('./todos/todos');
const remindersRouter = require('./reminders/reminders');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Rate limiting middleware
const apiLimiter = rateLimit({
    windowMs: 1000, // 1 second
    max: 100 // limit each IP to 100 requests per windowMs
});

// Apply the rate limiting middleware to API routes only
app.use('/api/', apiLimiter);

// API routes
app.use(todosRouter);
app.use(remindersRouter);

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
