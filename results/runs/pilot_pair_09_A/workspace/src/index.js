const express = require('express');
const session = require('express-session');
const todoRoutes = require('./todos/todoRoutes');
const reminderRoutes = require('./reminders/reminderRoutes');

const app = express();
app.use(express.json());

// Session middleware
app.use(session({
  secret: 'your-secret-key',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: false } // Note: Set secure to true in production
}));

// Routes
app.use('/api', todoRoutes);
app.use('/api', reminderRoutes);

// Rate limiting constraint implementation
const rateLimit = require('express-rate-limit');
const apiLimiter = rateLimit({
  windowMs: 1000, // 1 second
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api', apiLimiter);

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});