
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

VERSION = "FIXED-V1"

@app.route("/")
def home():
    return "TITANIUM OK", 200

@app.route("/version")
def version():
    return jsonify({"status": "ok", "version": VERSION}), 200

@app.route("/admin/stats")
def stats():
    token = request.headers.get("Authorization", "")
    if token != "Bearer admin":
        return jsonify({"error": "unauthorized"}), 401
    return jsonify({"status": "ok", "version": VERSION}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

