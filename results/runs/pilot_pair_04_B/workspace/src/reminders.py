from datetime import datetime
from flask import Flask, request, jsonify
import smtplib
from email.message import EmailMessage
import threading

app = Flask(__name__)

# Mock database
DATABASE = {
    'reminders': []
}

# Configuration for sending email
EMAIL_ADDRESS = 'youremail@example.com'
EMAIL_PASSWORD = 'yourpassword'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    data = request.json
    reminder = {
        'id': len(DATABASE['reminders']) + 1,
        'due_date': data['due_date'],
        'email': data['email'],
        'message': data['message']
    }
    DATABASE['reminders'].append(reminder)
    # Start a thread to manage the reminder
    threading.Thread(target=send_reminder_email, args=(reminder,)).start()
    return jsonify(reminder), 201

def send_reminder_email(reminder):
    reminder_time = datetime.strptime(reminder['due_date'], "%Y-%m-%dT%H:%M:%S")
    while datetime.now() < reminder_time:
        time.sleep(10)  # Check every 10 seconds
    # Send email when the reminder time is reached
    msg = EmailMessage()
    msg.set_content(reminder['message'])
    msg['Subject'] = 'Reminder Notification'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = reminder['email']
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print('Reminder email sent successfully')
    except Exception as e:
        print(f'Failed to send email: {e}')

# Entry point
if __name__ == '__main__':
    app.run(debug=True)