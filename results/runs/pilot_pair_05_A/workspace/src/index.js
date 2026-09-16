const express = require('express');
const session = require('express-session');
const todosRouter = require('./todos');
const remindersRouter = require('./reminders');
const sequelize = require('./config/database');

const app = express();
app.use(express.json());

app.use(session({
    secret: process.env.SESSION_SECRET,
    resave: false,
    saveUninitialized: true,
}));

app.use('/api', todosRouter);
app.use('/api', remindersRouter);

sequelize.sync().then(() => {
    app.listen(process.env.PORT, () => {
        console.log(`Server is running on port ${process.env.PORT}`);
    });
}).catch(error => {
    console.error('Unable to connect to the database:', error);
});