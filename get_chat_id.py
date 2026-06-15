import os
import requests

token = os.environ["TELEGRAM_BOT_TOKEN"]

url = f"https://api.telegram.org/bot{token}/getUpdates"
response = requests.get(url, timeout=20)

print(response.text)