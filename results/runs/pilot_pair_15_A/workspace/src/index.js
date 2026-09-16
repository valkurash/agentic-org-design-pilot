const express = require('express');
const todosRouter = require('./todos');
const remindersRouter = require('./reminders');

const app = express();
app.use(express.json());

// Use the TODOs and Reminders routes
app.use('/api', todosRouter);
app.use('/api', remindersRouter);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
