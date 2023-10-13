import smtplib
from email.mime.text import MIMEText

class EmailClient:
    def __init__(self, smtp_server, smtp_port, login, password):
        self.server = smtplib.SMTP(smtp_server, smtp_port)
        self.server.starttls()  # 使用TLS
        self.server.login(login, password)
        self.from_address = login

    def send_email(self, to_address, subject, body, from_address=None):
        if not from_address:
            from_address = self.from_address
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = from_address
        msg['To'] = to_address

        try:
            self.server.sendmail(from_address, to_address, msg.as_string())
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def close(self):
        self.server.quit()

# client = EmailClient("smtp.gmail.com", 587, "YOUR_LOGIN@gmail.com", "YOUR_PASSWORD")
# client.send_email("receiver@example.com", "Hello", "This is a test email.")
# client.close()


