const express = require('express');
const router = express.Router();

// Create a new TODO item
router.post('/', (req, res) => {
    // Code to create TODO
    res.status(201).send('TODO created');
});

// List all TODO items
router.get('/', (req, res) => {
    // Code to list TODOs
    res.status(200).send('List of TODOs');
});

// Delete a TODO item by ID
router.delete('/:id', (req, res) => {
    // Code to delete TODO
    res.status(204).send('TODO deleted');
});

module.exports = router;
