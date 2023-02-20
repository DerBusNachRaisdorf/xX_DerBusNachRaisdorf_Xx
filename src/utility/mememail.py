from email.message import EmailMessage
import ssl
import smtplib

def mememail_send(smtp_host, sender, password, receiver, subject, body):
    em = EmailMessage()
    em['From'] = sender
    em['To'] = receiver
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_host, 465, context=context) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, receiver, em.as_string())