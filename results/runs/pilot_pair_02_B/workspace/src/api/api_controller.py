from flask import Flask, request, jsonify
from .todo_service import TODOItemService
from .reminder_service import ReminderService
from .notification_service import NotificationService

app = Flask(__name__)

todo_service = TODOItemService(db_session="<DB_SESSION>")
reminder_service = ReminderService(db_session="<DB_SESSION>", notification_service=NotificationService(db_session="<DB_SESSION>"))
notification_service = NotificationService(db_session="<DB_SESSION>")

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json
    todo = todo_service.create_todo(
        user_id=data['user_id'],
        description=data['description'],
        reminder_datetime=data.get('reminder_datetime'))
    return jsonify(todo), 201

@app.route('/api/todos', methods=['GET'])
def list_todos():
    user_id = request.args.get('user_id')
    todos = todo_service.list_todos(user_id=user_id)
    return jsonify(todos), 200

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo_service.delete_todo(todo_id=todo_id)
    return '', 204

@app.route('/api/todos/<int:todo_id>', methods=['PUT'])
def complete_todo(todo_id):
    todo = todo_service.complete_todo(todo_id=todo_id)
    return jsonify(todo), 200

@app.route('/api/reminders', methods=['GET'])
def get_reminders():
    user_id = request.args.get('user_id')
    reminders = reminder_service.get_reminders(user_id=user_id)
    return jsonify(reminders), 200

@app.route('/api/notifications', methods=['POST'])
def post_notification():
    data = request.json
    notification_service.send_notification(
        user_id=data['user_id'],
        message=data['message'])
    return '', 204