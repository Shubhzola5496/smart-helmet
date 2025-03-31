import smtplib,ssl
from web import send_data


def send(self, message):
    host = "smtp.gmail.com"
    port = 465

    username = "shubham.gugaliya5496@gmail.com"
    password = "rxcl gqml hpzr uaby"

    receiver = "shubham.gugaliya5496@gmail.com"
    context = ssl.create_default_context()

    message = send_data()

    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(username, password)
        server.sendmail(username, receiver, message)