const express = require('express');
const { createTodo, listTodos, deleteTodo } = require('./todoController');
const { ensureAuthenticated } = require('../../auth/middleware');

const router = express.Router();

router.use(ensureAuthenticated);
router.post('/todos', createTodo);
router.get('/todos', listTodos);
router.delete('/todos/:id', deleteTodo);

module.exports = router;