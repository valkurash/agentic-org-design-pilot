from flask import Blueprint, request, jsonify

todo_bp = Blueprint('todo', __name__)

# In-memory storage for demonstration purposes
todos = []

@todo_bp.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.json
    todo_id = str(len(todos) + 1)  # Simple ID generation
    new_todo = {
        'id': todo_id,
        'title': data.get('title'),
        'description': data.get('description'),
        'due_date': data.get('due_date'),
        'reminder_datetime': data.get('reminder_datetime'),
        'user_id': data.get('user_id')
    }
    todos.append(new_todo)
    return jsonify(new_todo), 201

@todo_bp.route('/api/todos', methods=['GET'])
def get_todos():
    return jsonify(todos), 200

@todo_bp.route('/api/todos/<string:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    todos = [todo for todo in todos if todo['id'] != todo_id]
    return '', 204
