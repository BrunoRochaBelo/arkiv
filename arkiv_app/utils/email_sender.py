"""Utility for sending emails using Flask-Mail."""
from flask_mail import Mail, Message

mail = Mail()


def send_email(app, to: str, subject: str, body: str) -> None:
    """Send a simple text email."""
    mail.init_app(app)
    with app.app_context():
        msg = Message(subject=subject, recipients=[to], body=body)
        mail.send(msg)
