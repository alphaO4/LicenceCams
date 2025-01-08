from flask import Flask, jsonify, render_template, request, Response
import json
import random
import requests
app = Flask(__name__)

# Read JSON data
with open("sum-streams.json", "r") as file:
    sum_streams = json.load(file)

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
    return random_cams
@app.route("/proxy")
def proxy():
    url = request.args.get('url')
    if not url:
        return "No URL specified", 400
    response = requests.get(url, stream=True)
    return Response(response.iter_content(chunk_size=1024), content_type=response.headers.get('Content-Type'))


if __name__ == "__main__":
    app.run(debug=True)
