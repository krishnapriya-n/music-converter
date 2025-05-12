from flask import Flask, request, render_template, send_from_directory
import yt_dlp
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Method to download the YouTube video using yt-dlp with cookies
def download_video(youtube_url, download_path, cookies_path=None):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        if cookies_path:
            ydl_opts['cookiefile'] = cookies_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            video_path = ydl.prepare_filename(info_dict)
            return video_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        cookies_file = request.files.get('cookies_file')
        cookies_path = None
        if cookies_file:
            cookies_path = os.path.join(app.config['UPLOAD_FOLDER'], cookies_file.filename)
            cookies_file.save(cookies_path)

        video_path = download_video(youtube_url, app.config['UPLOAD_FOLDER'], cookies_path)
        if video_path:
            mp3_path = video_path.replace(".webm", ".mp3")  
            return render_template('index.html', download_url=mp3_path)
        else:
            return "Error: Unable to download the video. Please check the URL or cookies file."

    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
