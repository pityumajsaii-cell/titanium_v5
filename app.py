from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = "V6-STABLE"

@app.route("/")
def home():
    return "TITANIUM LIVE OK", 200

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
        "service": "titanium",
        "version": VERSION
    }), 200


# IMPORTANT: Render uses gunicorn, this is only local fallback
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
