from flask import Flask
from src.todos.todo_routes import todo_bp
from src.reminders.reminder_routes import reminder_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(todo_bp)
app.register_blueprint(reminder_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)