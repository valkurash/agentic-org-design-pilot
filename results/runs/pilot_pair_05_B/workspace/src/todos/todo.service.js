const db = require('../db');

async function createTodo(data) {
  const { userId, title, description, reminderDatetime } = data;
  const result = await db.query(
    'INSERT INTO todos (user_id, title, description, reminder_datetime) VALUES ($1, $2, $3, $4) RETURNING *',
    [userId, title, description, reminderDatetime]
  );
  return result.rows[0];
}

async function listTodos(userId) {
  const result = await db.query('SELECT * FROM todos WHERE user_id = $1', [userId]);
  return result.rows;
}

async function deleteTodo(todoId) {
  await db.query('DELETE FROM todos WHERE id = $1', [todoId]);
}

module.exports = {
  createTodo,
  listTodos,
  deleteTodo
};
