"""Utility for sending emails using Flask-Mail."""
from flask_mail import Mail, Message
from flask import url_for

mail = Mail()


def send_email(app, to: str, subject: str, body: str) -> None:
    """Send a simple text email."""
    mail.init_app(app)
    with app.app_context():
        msg = Message(subject=subject, recipients=[to], body=body)
        mail.send(msg)


def send_reset_email(app, user, token: str) -> None:
    reset_link = url_for('auth.reset_with_token', token=token, _external=True)
    body = f'Clique no link para redefinir sua senha: {reset_link}'
    send_email(app, user.email, 'Recuperar senha', body)
