import subprocess
import sys
import time

restart = False

def start_bot():
    return subprocess.Popen([sys.executable, "bot.py"])


while True:
    bot = start_bot()

    try:
        exit_code = bot.wait()
    except KeyboardInterrupt:
        break

    if exit_code == 42:
        time.sleep(15)
        continue

    break