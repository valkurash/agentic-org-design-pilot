from datetime import datetime

class TODOItemService:
    def __init__(self, db_session):
        self.db_session = db_session

    def create_todo(self, user_id, description, reminder_datetime=None):
        new_todo = {
            'user_id': user_id,
            'description': description,
            'is_complete': False,
            'created_at': datetime.now(),
            'reminder_datetime': reminder_datetime
        }
        # Persist new_todo to the database
        self.db_session.add(new_todo)
        self.db_session.commit()
        return new_todo

    def list_todos(self, user_id):
        # Retrieve todos from database
        return self.db_session.query(TODOItem).filter_by(user_id=user_id).all()

    def complete_todo(self, todo_id):
        # Mark todo as complete in the database
        todo = self.db_session.query(TODOItem).filter_by(id=todo_id).first()
        todo.is_complete = True
        self.db_session.commit()
        return todo

    def delete_todo(self, todo_id):
        # Remove todo from the database
        todo = self.db_session.query(TODOItem).filter_by(id=todo_id).first()
        self.db_session.delete(todo)
        self.db_session.commit()