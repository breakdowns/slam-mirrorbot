# Implement By - @anasty17 (https://github.com/Slam-Team/slam-mirrorbot/commit/0bfba523f095ab1dccad431d72561e0e002e7a59)
# (c) https://github.com/Slam-Team/slam-mirrorbot
# All rights reserved

import time
import requests
import os
import subprocess
from dotenv import load_dotenv

CONFIG_FILE_URL = os.environ.get('CONFIG_FILE_URL', None)
if CONFIG_FILE_URL is not None:
    out = subprocess.run(["wget", "-q", "-O", "config.env", CONFIG_FILE_URL])
load_dotenv('config.env')


IS_VPS = os.environ.get('IS_VPS', 'False')
if IS_VPS.lower() == 'true':
    IS_VPS = True
else:
    IS_VPS = False

try:
    HEROKU_APP_NAME = os.environ.get('HEROKU_APP_NAME', None)
    if len(HEROKU_APP_NAME) == 0:
        raise KeyError
except KeyError:
    HEROKU_APP_NAME = None

try:
    BASE_URL = os.environ.get('BASE_URL_OF_BOT', None)
    if not IS_VPS and len(BASE_URL) == 0:
        if HEROKU_APP_NAME is not None:
            BASE_URL = "https://"+HEROKU_APP_NAME.lower()+".herokuapp.com"
        if HEROKU_APP_NAME is None:
            raise KeyError
    if IS_VPS and len(BASE_URL) == 0:
        raise KeyError
except KeyError:
    BASE_URL = None

if not IS_VPS and BASE_URL is not None:
    while True:
        time.sleep(1000)
        status = requests.get(BASE_URL).status_code
