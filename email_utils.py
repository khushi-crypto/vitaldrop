import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# load .env variables automatically
load_dotenv()


def send_appreciation_email(receiver_email: str, donor_name: str) -> None:
    sender_email = os.getenv("VB_SENDER_EMAIL")
    sender_password = os.getenv("VB_APP_PASSWORD")

    if not sender_email or not sender_password:
        raise RuntimeError("❌ Email credentials missing in .env file.")

    subject = "Thank You from VitalDrop!"
    body = (
        f"Hello {donor_name},\n\n"
        "Thank you for donating blood. Your contribution can save lives.\n\n"
        "We truly appreciate your support in helping patients in need.\n\n"
        "Regards,\n"
        "VitalDrop Team"
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    # use secure SSL connection (more reliable than starttls)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print(f"✅ Email sent successfully to {receiver_email}")
