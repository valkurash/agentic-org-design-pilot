const TodoItem = require('./todoModel');

let todos = [];

const createTodo = (req, res) => {
  const { title, description } = req.body;
  const userId = req.session.userId;
  if (!title || !userId) {
    return res.status(400).json({ error: 'Title and user ID are required' });
  }
  const todo = new TodoItem(userId, title, description);
  todos.push(todo);
  res.status(201).json(todo);
};

const listTodos = (req, res) => {
  const userId = req.session.userId;
  const userTodos = todos.filter(todo => todo.user_id === userId);
  res.json(userTodos);
};

const deleteTodo = (req, res) => {
  const { id } = req.params;
  const userId = req.session.userId;
  const index = todos.findIndex(todo => todo.id === id && todo.user_id === userId);
  if (index === -1) {
    return res.status(404).json({ error: 'Todo not found' });
  }
  todos.splice(index, 1);
  res.status(204).send();
};

module.exports = { createTodo, listTodos, deleteTodo };