const express = require('express');
const { v4: uuidv4 } = require('uuid');
let todos = [];

const getTodos = (req, res) => {
  res.json(todos);
};

const createTodo = (req, res) => {
  const { title, description } = req.body;
  const newTodo = {
    id: uuidv4(),
    title,
    description,
    created_at: new Date(),
    updated_at: new Date()
  };
  todos.push(newTodo);
  res.status(201).json(newTodo);
};

const deleteTodo = (req, res) => {
  const { id } = req.params;
  todos = todos.filter(todo => todo.id !== id);
  res.status(204).send();
};

module.exports = { getTodos, createTodo, deleteTodo };
