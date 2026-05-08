from flask import Flask, jsonify, request
import os

app = Flask(__name__)

VERSION = "STABLE-V1"

# =====================
# HEALTH CHECK
# =====================
@app.route("/")
def home():
    return "TITANIUM SAAS ONLINE", 200

# =====================
# VERSION
# =====================
@app.route("/version")
def version():
    return jsonify({
        "status": "online",
        "version": VERSION
    }), 200

# =====================
# ADMIN (TEMP SIMPLE SECURITY)
# =====================
@app.route("/admin/stats")
def admin_stats():
    token = request.headers.get("Authorization", "")
    expected = os.getenv("ADMIN_TOKEN", "dev-token")

    if token != f"Bearer {expected}":
        return jsonify({"error": "unauthorized"}), 401

    return jsonify({
        "status": "ok",
        "service": "titanium",
        "version": VERSION
    }), 200


# =====================
# ENTRYPOINT (RENDER SAFE)
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
