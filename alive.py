import time
import requests
import os
from dotenv import load_dotenv

load_dotenv('config.env')

url = os.environ.get("BASE_URL_OF_BOT")
while True:
    time.sleep(1000)
    status = requests.get(url).status_code
