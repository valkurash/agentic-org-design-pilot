const { DataTypes } = require('sequelize');
const sequelize = require('../config/database');

const Todo = sequelize.define('Todo', {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    title: {
        type: DataTypes.STRING,
        allowNull: false
    },
    description: {
        type: DataTypes.TEXT,
        allowNull: true
    },
    completed: {
        type: DataTypes.BOOLEAN,
        defaultValue: false
    },
    reminder_datetime: {
        type: DataTypes.DATE,
        allowNull: true
    }
}, {
    timestamps: true
});

module.exports = Todo;