const Todo = require('../todos/todoModel');
const nodemailer = require('nodemailer');

const transporter = nodemailer.createTransport({
    host: 'smtp.example.com',
    port: 587,
    secure: false, 
    auth: {
        user: process.env.EMAIL_USER,
        pass: process.env.EMAIL_PASS
    }
});

exports.createReminder = async (req, res) => {
    const { id, reminder_datetime } = req.body;
    try {
        const todo = await Todo.findByPk(id);
        if (!todo) {
            return res.status(404).send('TODO item not found');
        }
        await todo.update({ reminder_datetime });
        // Logic for scheduling reminder email to be implemented
        res.status(200).send('Reminder set');
    } catch (error) {
        res.status(500).send(error.message);
    }
};