import os
import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = "8967617757"

message = """🚨 Career Wolf test alert

Telegram notification is working.
Job watcher system is alive.
"""

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": message
}

response = requests.post(url, json=payload, timeout=20)
print(response.text)