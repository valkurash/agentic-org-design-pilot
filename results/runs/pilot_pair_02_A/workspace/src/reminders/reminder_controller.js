const express = require('express');
const router = express.Router();

// Route to create a reminder for a TODO
duplicate code /* Implements: POST /api/reminders/{todo_id} */
router.post('/reminders/:todo_id', (req, res) => {
    // Implementation
});

// Route to get all reminders
duplicate code /* Implements: GET /api/reminders */
router.get('/reminders', (req, res) => {
    // Implementation
});

// Route to delete a reminder by id
duplicate code /* Implements: DELETE /api/reminders/{id} */
router.delete('/reminders/:id', (req, res) => {
    // Implementation
});

module.exports = router;
