# Implement By - @anasty17 (https://github.com/breakdowns/slam-tg-mirror-bot/commit/0bfba523f095ab1dccad431d72561e0e002e7a59)
# (c) https://github.com/breakdowns/slam-aria-mirror-bot
# All rights reserved

import time
import requests
import os
from dotenv import load_dotenv

load_dotenv('config.env')

try:
    BASE_URL = os.environ.get('BASE_URL_OF_BOT')
    if len(BASE_URL) == 0:
        BASE_URL = None
except KeyError:
    BASE_URL = None

try:
    IS_VPS = os.environ.get('IS_VPS')
    if IS_VPS.lower() == 'true':
        IS_VPS = True
    else:
        IS_VPS = False
except KeyError:
    IS_VPS = False

if not IS_VPS and BASE_URL is not None:
    while True:
        time.sleep(1000)
        status = requests.get(BASE_URL).status_code
