from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "TITANIUM LIVE OK", 200

@app.route("/admin/stats")
def stats():
    return jsonify({"status": "ok", "service": "titanium", "route": "/admin/stats working"}), 200

@app.route("/version")
def version():
    return jsonify({"version": "V5-FIX", "status": "stable"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
