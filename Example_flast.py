from flask import Flask, render_template_string, jsonify, render_template
import json
import random
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

if __name__ == "__main__":
    app.run(debug=True)
