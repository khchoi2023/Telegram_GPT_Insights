import time
import subprocess


def run():
    subprocess.run(['python', 'C:/tele_bot/gpt_insights.py'])


print()
print('telegram bot start!')
print()


while True:
    run()
    print()
    print('wait 10 min...')
    print()
    time.sleep(600)
