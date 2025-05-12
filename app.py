from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        youtube_url = request.form.get("youtube_url")
        # You can handle the link here if needed
    return render_template("index.html")

if __name__ == '__main__':
    app.run(debug=True)