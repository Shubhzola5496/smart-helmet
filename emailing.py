import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(message):
    sender_email = "shubham.gugaliya5496@gmail.com"
    receiver_email = "shubham.gugaliya5496@gmail.com"
    password = "rxcl gqml hpzr uaby"  # Consider using environment variables for security

    subject = "Smart Helmet Data Update"

    # Create email content
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    # Send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print("✅ Email sent successfully!")
