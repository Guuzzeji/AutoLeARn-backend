import os
from flask import Blueprint, request, jsonify

from ai.whisper import whisper

API_PATH = Blueprint("api", __name__, url_prefix="/api")

FILE_DUMP = "TEMP_SAVE_FOLDER"
os.makedirs(FILE_DUMP, exist_ok=True)


@API_PATH.route("/ping", methods=["GET"])
def handle_ping():
    return jsonify({"message": "pong"}), 200
