import os
import socket
from flask import Flask, jsonify

app = Flask(__name__)

VERSION = os.environ.get("APP_VERSION", "1.0.0")
FEATURE_NEW_GREETING = os.environ.get("FEATURE_NEW_GREETING", "false").lower() == "true"


@app.route("/")
def index():
    return jsonify(
        {
            "service": "devops-cicd-lab",
            "version": VERSION,
            "hostname": socket.gethostname(),
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/greeting")
def greeting():
    if FEATURE_NEW_GREETING:
        return jsonify({"message": "Hello from the shiny new greeting endpoint! 🚀"})
    return jsonify({"message": "Hello, World!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
