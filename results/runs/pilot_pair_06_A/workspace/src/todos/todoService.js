import { db } from '../db';

export const addTodo = async (todoData) => {
  const { rows } = await db.query(
    'INSERT INTO todos (title, description, reminder) VALUES ($1, $2, $3) RETURNING *',
    [todoData.title, todoData.description, todoData.reminder]
  );
  return rows[0];
};

export const getTodos = async () => {
  const { rows } = await db.query('SELECT * FROM todos');
  return rows;
};

export const deleteTodo = async (id) => {
  await db.query('DELETE FROM todos WHERE id = $1', [id]);
};
