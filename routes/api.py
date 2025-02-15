import os
from flask import Blueprint, request, jsonify

from ai.whisper import whisper

API_PATH = Blueprint("api", __name__, url_prefix="/api")

FILE_DUMP = "TEMP_SAVE_FOLDER"
os.makedirs(FILE_DUMP, exist_ok=True)

@API_PATH.route("/ping", methods=["GET"])
def handle_ping():
    return jsonify({"message": "pong"}), 200


@API_PATH.route("/transcribe", methods=["POST"])
def handle_transcribe():
    if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join(FILE_DUMP, audio_file.filename)
    audio_file.save(file_path)

    response = whisper(file_path)

    if response == None:
        return jsonify({"error": "Failed to transcribe audio"}), 500
    
    return jsonify(response), 200