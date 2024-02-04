import sys
from client import Client

def run():
    print(sys.argv[1], sys.argv[2])
    client = Client(sys.argv[1], sys.argv[2])
    client.smtp.sendmail('kyuds.bot@gmail.com',
              'kyuseung1016@gmail.com',
              "Hi!")
    client.quit()

if __name__ == "__main__":
    run()

