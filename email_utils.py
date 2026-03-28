import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ===============================
# 📧 SEND EMAIL FUNCTION
# ===============================
def send_email(to_email, subject, body):
    sender = "devssicm69@gmail.com"       # 🔐 secure
    password = "obutsjuxobkbwyt"  # 🔐 app password
    print("Sending email to:", to_email)

    from email_utils import send_email

    if not sender or not password:
        print("❌ Email credentials not set")
        return False

    # ✅ Create email
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        # 🔐 Secure connection
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed (check app password)")
    except smtplib.SMTPException as e:
        print("❌ SMTP error:", e)
    except Exception as e:
        print("❌ General email error:", e)

    return False