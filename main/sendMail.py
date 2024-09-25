import smtplib, ssl
from email.utils import formataddr

class EmailClient:
    def __init__(self, smtp_server, port, sender_email, sender_name, password):
        self.smtp_server = smtp_server
        self.port = port
        self.sender_email = sender_email  # Default sender email
        self.sender_name = sender_name  # Display name for the sender
        self.password = password
        self.context = ssl.create_default_context()

    def send_email(self, receiver_email, subject, body):
        # Format the From field to include the sender name and email
        from_header = formataddr((self.sender_name, self.sender_email))

        # Message with formatted from, to, subject, and body
        message = f"""\
From: {from_header}
To: {receiver_email}
Subject: {subject}

{body}"""

        try:
            # Connect to the server
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=self.context)  # Secure the connection
                server.ehlo()  # Can be omitted
                server.login(self.sender_email, self.password)

                # Send the email
                server.sendmail(self.sender_email, receiver_email, message)
                print('Email sent successfully')
        except Exception as e:
            print(f"Failed to send email: {e}")

# Create an instance of the EmailClient class
email_client = EmailClient(
    smtp_server="smtp.gmail.com", 
    port=587, 
    sender_email="jimlestonosoi42@gmail.com", 
    sender_name="SKILLMATE",  # Display name
    password="cxvs sdvg ayek jxbk"
)

# # Send an email using the object
# receiver_email = "jimleston35@gmail.com"
# subject = "Welcome to Udemy Academy!"
# body = "Thank you for signing up for Udemy Academy!"
# email_client.send_email(receiver_email, subject, body)
