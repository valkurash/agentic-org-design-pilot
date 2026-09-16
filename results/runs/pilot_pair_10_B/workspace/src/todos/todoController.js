const todos = [];

function createTodo(req, res) {
  const { title, description, reminder } = req.body;
  const newTodo = {
    todoId: String(todos.length + 1),
    userId: req.userId || 'anonymous',
    title,
    description,
    isCompleted: false,
    reminder: reminder ? new Date(reminder) : null
  };
  todos.push(newTodo);
  res.status(201).json(newTodo);
}

function listTodos(req, res) {
  res.status(200).json(todos);
}

function deleteTodo(req, res) {
  const { id } = req.params;
  const index = todos.findIndex(todo => todo.todoId === id);
  if (index !== -1) {
    todos.splice(index, 1);
    res.status(204).send();
  } else {
    res.status(404).json({ message: 'TODO not found' });
  }
}

module.exports = { createTodo, listTodos, deleteTodo };