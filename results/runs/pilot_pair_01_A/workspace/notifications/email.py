import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    def __init__(self, smtp_server: str, port: int, login: str, password: str):
        self.smtp_server = smtp_server
        self.port = port
        self.login = login
        self.password = password

    def send_email(self, recipient: str, subject: str, body: str) -> None:
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_server, self.port) as server:
            server.starttls()
            server.login(self.login, self.password)
            server.send_message(msg)

# Example usage:
# notifier = EmailNotifier(smtp_server='smtp.example.com', port=587, login='your_email@example.com', password='your_password')
# notifier.send_email(recipient='recipient@example.com', subject='Reminder', body='This is your reminder email.')