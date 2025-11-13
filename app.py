from flask import Flask, request
import requests
import os
import json

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8340154581:AAFgjGv-KZ64kr-KcqmeeFtNJEJhvu-kRcw")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route('/')
def home():
    return "Render Stream Bot is Live 🎥"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    print("📩 Incoming update:", json.dumps(update, indent=2))  # debug log

    if not update or 'message' not in update:
        return "ok"

    message = update['message']
    chat_id = message['chat']['id']

    if 'video' in message:
        file_id = message['video']['file_id']
        print(f"🎞 Got video file_id: {file_id}")

        file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        print("📦 getFile response:", json.dumps(file_info, indent=2))

        if 'result' in file_info:
            file_path = file_info['result']['file_path']
            stream_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"

            text = f"🎬 Stream Link (Direct Telegram CDN):\n{stream_url}"
        else:
            text = f"⚠️ Error fetching file info.\n\nTelegram Response:\n{json.dumps(file_info, indent=2)}"

        requests.post(f"{TELEGRAM_API_URL}/sendMessage", data={'chat_id': chat_id, 'text': text})

    else:
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", data={
            'chat_id': chat_id,
            'text': "❌ Please forward a video file to get the stream link."
        })

    return "ok"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
