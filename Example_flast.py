from flask import Flask, render_template_string, jsonify, render_template
import json

app = Flask(__name__)

# Read JSON data
with open("sum-streams.json", "r") as file:
    sum_streams = json.load(file)

@app.route("/")
def index():
    return render_template("index.html", cameras=sum_streams)

@app.route("/api/streams")
def api_streams():
    return jsonify(sum_streams)

if __name__ == "__main__":
    app.run(debug=True)
