const Todo = require('./todoModel');

exports.createTodo = async (req, res) => {
    const { title, description } = req.body;
    try {
        const todo = await Todo.create({ title, description, completed: false });
        res.status(201).json(todo);
    } catch (error) {
        res.status(400).send(error.message);
    }
};

exports.getTodos = async (req, res) => {
    try {
        const todos = await Todo.findAll();
        res.status(200).json(todos);
    } catch (error) {
        res.status(500).send(error.message);
    }
};

exports.deleteTodo = async (req, res) => {
    const { id } = req.params;
    try {
        await Todo.destroy({ where: { id } });
        res.status(204).send();
    } catch (error) {
        res.status(500).send(error.message);
    }
};