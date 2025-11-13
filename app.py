from flask import Flask, request
import requests
import os

# Initialize Flask app
app = Flask(__name__)

# Telegram bot token
BOT_TOKEN = os.getenv("BOT_TOKEN", "8340154581:AAFgjGv-KZ64kr-KcqmeeFtNJEJhvu-kRcw")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route('/')
def home():
    return "Render Stream Bot is Live 🎥"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()

    if not update or 'message' not in update:
        return "ok"

    message = update['message']
    chat_id = message['chat']['id']

    # If a video file is received
    if 'video' in message:
        file_id = message['video']['file_id']
        file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']
        stream_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

        text = f"🎬 Stream Link:\n{stream_url}"
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", data={'chat_id': chat_id, 'text': text})

    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
