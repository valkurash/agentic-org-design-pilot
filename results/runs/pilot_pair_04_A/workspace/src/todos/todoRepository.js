const { Pool } = require('pg');

const pool = new Pool({
    // Your database configuration here
});

class TodoRepository {
    static async create(title, due_date, reminder_datetime) {
        const { rows } = await pool.query(
            `INSERT INTO todos (title, due_date, reminder_datetime) VALUES ($1, $2, $3) RETURNING *`,
            [title, due_date, reminder_datetime]
        );
        return rows[0];
    }

    static async findAll() {
        const { rows } = await pool.query('SELECT * FROM todos');
        return rows;
    }

    static async delete(id) {
        await pool.query('DELETE FROM todos WHERE id = $1', [id]);
    }
}

module.exports = TodoRepository;
