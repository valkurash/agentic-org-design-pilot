from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

reminder_bp = Blueprint('reminder', __name__)

# Assume we have an email sending function
def send_email_notification(todo):
    # Placeholder for email sending logic
    print(f"Sending email notification for TODO: {todo['title']}")

@reminder_bp.route('/api/reminders', methods=['POST'])
def set_reminder():
    data = request.json
    reminder_datetime = datetime.strptime(data.get('reminder_datetime'), '%Y-%m-%dT%H:%M:%S')
    todo_id = data.get('todo_id')
    todo = next((t for t in todos if t['id'] == todo_id), None)
    if todo:
        time_until_reminder = reminder_datetime - datetime.now()
        # Simulating scheduling
        if time_until_reminder.total_seconds() > 0:
            # Schedules the email notification
            send_email_notification(todo)
            return jsonify({'status': 'Reminder set'}), 200
    return jsonify({'error': 'TODO not found or invalid date'}), 404
