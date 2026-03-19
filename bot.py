import requests
import os

def send_telegram_msg(message):
    # These 'secrets' keep your bot token safe from hackers
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload)

# For now, let's send a test message to ensure the connection works
news_update = "🚀 Forex Bot is Online! High-impact news tracking starting soon."
send_telegram_msg(news_update)
