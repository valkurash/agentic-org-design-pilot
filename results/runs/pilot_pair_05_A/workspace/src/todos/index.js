const express = require('express');
const router = express.Router();
const { createTodo, getTodos, deleteTodo } = require('./service');

router.post('/todos', createTodo);
router.get('/todos', getTodos);
router.delete('/todos/:id', deleteTodo);

module.exports = router;