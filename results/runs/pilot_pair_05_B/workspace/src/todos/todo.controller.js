const express = require('express');
const router = express.Router();
const { validateSession } = require('../auth/session');
const { createTodo, listTodos, deleteTodo } = require('./todo.service');

// Middleware to validate session
router.use(validateSession);

// POST /api/todos
router.post('/', async (req, res) => {
  try {
    const todo = await createTodo(req.body);
    res.status(201).send(todo);
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
});

// GET /api/todos
router.get('/', async (req, res) => {
  try {
    const todos = await listTodos(req.user.id);
    res.send(todos);
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
});

// DELETE /api/todos/:id
router.delete('/:id', async (req, res) => {
  try {
    await deleteTodo(req.params.id);
    res.status(204).send();
  } catch (error) {
    res.status(400).send({ error: error.message });
  }
});

module.exports = router;
