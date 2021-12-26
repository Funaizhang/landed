import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List

class EmailSender():
    def __init__(self, sender='', password='', receivers=List):
        self.sender = sender
        self.receivers = receivers
        if password:
            self.password = password
        else:
            self.password = input("Type your password and press enter:")

    def send_email(self, subject, message):
        self.body = MIMEMultipart("alternative")
        self.body["Subject"] = subject
        self.body["From"] = self.sender
        self.body["To"] = ', '.join(self.receivers)
        today = datetime.today().strftime('%Y-%m-%d')
        self.message = f"""\
            <html>
            <body>
                <p>New listings found on {today}: </p>
                {message}
            </body>
            </html>
            """
        # Turn these into html MIMEText objects
        message = MIMEText(self.message, "html")
        self.body.attach(message)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.sender, self.password)
            server.sendmail(self.sender, self.receivers, self.body.as_string())