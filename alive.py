# Implement By - @anasty17 (https://github.com/SlamDevs/slam-mirrorbot/commit/0bfba523f095ab1dccad431d72561e0e002e7a59)
# (c) https://github.com/SlamDevs/slam-mirrorbot
# All rights reserved

import time
import requests
import os

BASE_URL = os.environ.get('BASE_URL_OF_BOT', None)
if len(BASE_URL) == 0:
    BASE_URL = None

IS_VPS = os.environ.get('IS_VPS', 'False')
if IS_VPS.lower() == 'true':
    IS_VPS = True
else:
    IS_VPS = False

if not IS_VPS and BASE_URL is not None:
    while True:
        time.sleep(600)
        status = requests.get(BASE_URL).status_code
