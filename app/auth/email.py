from flask import render_template
from flask_mail import Message
from app import app, mail
from threading import Thread

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()

def send_password_reset_email(doctor):
    token = doctor.get_reset_password_token()
    send_email('[Digi Doc] Reset your password',
        sender = app.config['ADMINS'][0],
        recipients=[doctor.email],
        text_body = render_template('email/reset_password.txt', doctor=doctor, token=token),
        html_body = render_template('email/reset_password.html', doctor=doctor, token=token)
        )

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
