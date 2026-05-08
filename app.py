from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = "STABLE-1.0"

@app.route("/")
def home():
    return "TITANIUM LIVE OK", 200

@app.route("/version")
def version():
    return jsonify({"version": VERSION, "status": "online"}), 200

@app.route("/admin/stats")
def stats():
    return jsonify({
        "status": "ok",
        "route": "working",
        "version": VERSION
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
