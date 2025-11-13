@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"ok": False, "error": "No JSON"}), 400

    try:
        chat_id = data["message"]["chat"]["id"]

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

        res = requests.get(f"{BASE_URL}/getFile?file_id={file_id}")
        file_info = res.json()

        if not file_info.get("ok"):
            # Detect file too big
            if "too big" in file_info.get("description", "").lower():
                msg = (
                    "🚫 The file is larger than Telegram’s direct download limit (≈20MB).\n\n"
                    "👉 To fix:\n"
                    "1. Upload the video to a **private Telegram channel**.\n"
                    "2. Add this bot as an **admin** in that channel.\n"
                    "3. Forward the video again here."
                )
            else:
                msg = f"❌ Telegram API error:\n{file_info}"

            requests.post(f"{BASE_URL}/sendMessage", json={
                "chat_id": chat_id,
                "text": msg
            })
            return jsonify({"ok": True})

        file_path = file_info["result"]["file_path"]
        file_url = FILE_URL + file_path
        stream_link = f"https://{request.host}/watch?url={file_url}"

        requests.post(f"{BASE_URL}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"🎬 Your stream link:\n{stream_link}"
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"ok": False, "error": str(e)}), 500

    return jsonify({"ok": True})
