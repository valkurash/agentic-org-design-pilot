from datetime import datetime
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Mock database
DATABASE = {
    'todos': []
}

@app.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json
    todo_item = {
        'id': str(uuid.uuid4()),
        'title': data['title'],
        'description': data.get('description', ''),
        'due_date': data.get('due_date'),
        'reminder_datetime': data.get('reminder_datetime'),
        'user_id': data['user_id']
    }
    DATABASE['todos'].append(todo_item)
    return jsonify(todo_item), 201

@app.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(DATABASE['todos']), 200

@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    original_length = len(DATABASE['todos'])
    DATABASE['todos'] = [todo for todo in DATABASE['todos'] if todo['id'] != todo_id]
    if len(DATABASE['todos']) < original_length:
        return '', 204
    else:
        return 'Not Found', 404

# Entry point
if __name__ == '__main__':
    app.run(debug=True)