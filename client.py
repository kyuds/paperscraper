import smtplib

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT_TLS = "587"

class Client:
    def __init__(self, smtp_id, smtp_pw):
        self.address = smtp_id
        self.smtp = smtplib.SMTP(SMTP_SERVER, SMTP_PORT_TLS)
        self.smtp.ehlo()
        self.smtp.starttls()
        self.smtp.login(self.address, smtp_pw)
    
    def quit(self):
        self.smtp.quit()
