import express from 'express';
import { addTodo, getTodos, deleteTodo } from './todoService';

const router = express.Router();

router.post('/api/todos', async (req, res) => {
  try {
    const todo = await addTodo(req.body);
    res.status(201).json(todo);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.get('/api/todos', async (req, res) => {
  try {
    const todos = await getTodos();
    res.status(200).json(todos);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.delete('/api/todos/:id', async (req, res) => {
  try {
    await deleteTodo(req.params.id);
    res.status(204).send();
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

export default router;
