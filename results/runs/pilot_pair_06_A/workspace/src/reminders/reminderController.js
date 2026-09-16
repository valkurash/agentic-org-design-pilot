import express from 'express';
import { addReminder } from './reminderService';

const router = express.Router();

router.post('/api/reminders', async (req, res) => {
  try {
    const reminder = await addReminder(req.body);
    res.status(201).json(reminder);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

export default router;
