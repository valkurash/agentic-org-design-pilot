const express = require('express');
const router = express.Router();
const WebSocket = require('ws');

// Middleware for session authentication
const sessionMiddleware = require('../../auth/sessionMiddleware');
router.use(sessionMiddleware);

// WebSocket server setup
const wss = new WebSocket.Server({ port: 8080 });
wss.on('connection', ws => {
  console.log('Client connected');

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

// Reminder scheduling
router.post('/api/reminders', (req, res) => {
  // Logic to schedule reminder
  res.status(201).send('Reminder scheduled');
});

module.exports = router;