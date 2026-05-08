from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = "V5-FINAL-REBUILD"

@app.route("/")
def home():
    return "TITANIUM OK", 200

@app.route("/version")
def version():
    return jsonify({
        "status": "online",
        "version": VERSION
    }), 200

@app.route("/admin/stats")
def stats():
    return jsonify({
        "status": "ok",
        "route": "admin working",
        "version": VERSION
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
