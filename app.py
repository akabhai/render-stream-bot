from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

# Homepage
@app.route('/')
def home():
    return "Render Stream Bot is live!"

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"ok": False, "error": "No JSON"}), 400

    try:
        # Get chat info
        chat_id = data["message"]["chat"]["id"]

        # Check if message has a video or document
        file_id = None
        if "video" in data["message"]:
            file_id = data["message"]["video"]["file_id"]
        elif "document" in data["message"]:
            file_id = data["message"]["document"]["file_id"]
        else:
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": "⚠️ Please send or forward a *video* file only."
            })
            return jsonify({"ok": True})

        # Get file info from Telegram
        res = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
        file_info = res.json()

        # Check response correctness
        if "result" not in file_info:
            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": f"❌ Telegram API error:\n{file_info}"
            })
            return jsonify({"ok": True})

        file_path = file_info["result"]["file_path"]
        file_url = FILE_URL + file_path

        # Generate a watch link (simple stream page)
        stream_link = f"https://{request.host}/watch?url={file_url}"

        # Send link to user
        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"🎬 Your stream link:\n{stream_link}"
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

    return jsonify({"ok": True})


# Video player route
@app.route('/watch')
def watch():
    url = request.args.get('url', '')
    html = f"""
    <html>
      <head><title>Video Stream</title></head>
      <body style='background:#000;margin:0;'>
        <video controls autoplay style='width:100%;height:100vh;object-fit:contain;'>
          <source src='{url}' type='video/mp4'>
          Your browser does not support video playback.
        </video>
      </body>
    </html>
    """
    return render_template_string(html)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
