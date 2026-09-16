class NotificationService:
    def __init__(self, db_session):
        self.db_session = db_session

    def send_notification(self, user_id, message):
        notification = {
            'user_id': user_id,
            'message': message,
            'created_at': datetime.now(),
            'is_read': False
        }
        # Write notification to database
        self.db_session.add(notification)
        self.db_session.commit()

    def get_notifications(self, user_id):
        # Retrieve notifications from the database
        return self.db_session.query(Notification).filter_by(user_id=user_id).all()