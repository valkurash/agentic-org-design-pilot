// Models for postgres interaction
const { Sequelize, DataTypes } = require('sequelize');
const sequelize = new Sequelize('postgres://user:pass@localhost:5432/todoapp');

const Todo = sequelize.define('Todo', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  user_id: DataTypes.UUID,
  title: DataTypes.STRING,
  description: DataTypes.STRING,
  completed: DataTypes.BOOLEAN,
  created_at: DataTypes.DATE,
  updated_at: DataTypes.DATE
});

const Reminder = sequelize.define('Reminder', {
  id: {
    type: DataTypes.UUID,
    defaultValue: DataTypes.UUIDV4,
    primaryKey: true
  },
  todo_id: DataTypes.UUID,
  remind_at: DataTypes.DATE,
  notified: DataTypes.BOOLEAN
});

module.exports = { Todo, Reminder };
