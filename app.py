import os
import tempfile
from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from google.cloud import storage
from uuid import uuid4

app = Flask(__name__)

# Replace with your actual bucket name
BUCKET_NAME = "music-converter-6dc2b.appspot.com"

# Initialize GCS client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

@app.route('/', methods=['POST'])
def convert_video():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"success": False, "message": "Missing URL"}), 400

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_template = os.path.join(temp_dir, '%(title)s.%(ext)s')

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': output_template,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info_dict).replace(".webm", ".mp3").replace(".m4a", ".mp3")

            blob_name = f"mp3s/{uuid4().hex}.mp3"
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(filename)
            blob.make_public()

            return jsonify({"success": True, "url": blob.public_url})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Export for Cloud Functions entry point
def convert_video_to_mp3(request):
    with app.app_context():
        return convert_video()
