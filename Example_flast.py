from flask import Flask, jsonify, render_template, request, Response
import json
import random
import requests
app = Flask(__name__)

# Read JSON data
with open("sum-streams.json", "r") as file:
    sum_streams = json.load(file)

# Extract allowed URLs based on camera names
ALLOWED_URLS = {camera['color_stream'] for camera in sum_streams} | {camera['ir_stream'] for camera in sum_streams}

@app.route("/")
def index():
    random_cams = random.sample(sum_streams, 2)
    return render_template("index.html", cameras=random_cams)

@app.route("/api/streams")
def api_streams():
    return jsonify(sum_streams)

@app.route("/api/random")
def api_random():
    random_cams = random.sample(sum_streams, 2)
    return jsonify(random_cams)

@app.route("/proxy")
def proxy():
    url = request.args.get('url')
    if not url or url not in ALLOWED_URLS:
        return "Forbidden", 403
    try:
        response = requests.get(url, stream=True)
        return Response(response.iter_content(chunk_size=1024), content_type=response.headers.get('Content-Type'))
    except requests.RequestException:
        return "Error fetching the URL", 500

if __name__ == "__main__":
    app.run(debug=True)
