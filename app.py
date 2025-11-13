from flask import Flask, request, send_file, render_template, abort
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{BOT_TOKEN}/"

videos = {}  # {id: file_path}

@app.route("/")
def home():
    return "Render Stream Bot Active!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if not data:
        return "no data"
    if "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]

        # If message has video or document
        if "video" in msg:
            file_id = msg["video"]["file_id"]
        elif "document" in msg:
            file_id = msg["document"]["file_id"]
        else:
            return "no video"

        # Get file info from Telegram
        file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]

        # Store for later streaming
        video_id = file_id[-10:]  # short id
        videos[video_id] = file_path

        # Send back stream link
        stream_link = f"https://{os.getenv('RENDER_URL')}/watch?id={video_id}"
        requests.get(f"{BASE_URL}/sendMessage", params={
            "chat_id": chat_id,
            "text": f"🎬 Stream link:\n{stream_link}"
        })

    return "ok"

@app.route("/watch")
def watch():
    video_id = request.args.get("id")
    if not video_id or video_id not in videos:
        return abort(404)
    return render_template("player.html", id=video_id)

@app.route("/stream/<id>")
def stream(id):
    if id not in videos:
        return abort(404)
    file_path = videos[id]
    stream_url = FILE_URL + file_path
    r = requests.get(stream_url, stream=True)
    return send_file(
        r.raw,
        mimetype="video/mp4"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
