import smtplib
import random

class Email:
    def __init__(self):
        self.sender_email = "ecothrift@admin.com"
        self.password = "ecothrift123"
        self.smtp_server = "cp-wc02.sin02.ds.network"
        self.smtp_port = 465

    def send_email(self, receipient_email, subject, message):
        """
        Sends an email with the specified content.
        """
        with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
            # Create the email content
            msg = f"Subject: {subject}\n\n{message}"
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, receipient_email, msg.encode('utf-8'))
            print(f"Sent email with subject: {subject} to {receipient_email}")

    def send_otp(self, recipient_email):
        otp = self.generate_otp()
        message = f"Your OTP for EcoThrift login is: {otp}"
        try:
            self.send_email(recipient_email, "Your OTP for EcoThrift login", message)
        except:
            print("Cannot Send OTP")
            print(otp)
        return otp

    def generate_otp(self):
        otp = ''
        for x in range(6):
            otp += str(random.randint(0, 9))
        return otp
