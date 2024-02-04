import smtplib, sys

def run():
    pass

smtp = smtplib.SMTP('smtp.gmail.com', port='587')
smtp.ehlo()
smtp.starttls()
smtp.login('kyuds.bot@gmail.com', sys.argv[1])

smtp.sendmail('kyuds.bot@gmail.com',
              'kyuseung1016@gmail.com',
              "Hi!")
              
smtp.quit()

# if __name__ == "__main__":
#     run()

