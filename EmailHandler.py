import smtplib, ssl
import os
from dotenv import load_dotenv
load_dotenv()

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = os.getenv('senderemail', "")  # Enter your address
receiver_email = os.getenv('receiveremail', "")  # Enter receiver address
password = os.getenv('senderpw', "")

def sendEmail(subject, body, errorHandle=False):
    message = "Subject: {} \n\n {}"
    message = message.format(subject, body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        if(errorHandle):
            server.sendmail(sender_email, sender_email, message)
        else:
            server.sendmail(sender_email, receiver_email, message)
