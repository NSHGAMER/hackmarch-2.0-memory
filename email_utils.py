import smtplib
from email.mime.text import MIMEText
import os

def send_email(to_email, subject, body):
    sender = "devssicm69@gmail.com"
    password = "obutsjuxobkbwytt"  # Gmail App Password

    if not sender or not password:
        print("❌ Email config missing")
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())

        print("✅ Email sent")

    except Exception as e:
        print("❌ Email error:", e)