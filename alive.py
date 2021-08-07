# Implement By - @anasty17 (https://github.com/breakdowns/slam-tg-mirror-bot/commit/0bfba523f095ab1dccad431d72561e0e002e7a59)
# (c) https://github.com/breakdowns/slam-aria-mirror-bot
# All rights reserved

import time
import requests
import os
from dotenv import load_dotenv

load_dotenv('config.env')

url = os.environ.get("BASE_URL_OF_BOT")
while True:
    time.sleep(1000)
    status = requests.get(url).status_code
