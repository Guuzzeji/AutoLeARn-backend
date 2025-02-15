import os
from flask import Blueprint, request, jsonify

from ai.whisper import whisper
from xr.screen_capture import get_windows, window_screenshot
from ai.nl_to_struct import STRUCTS_CONVERTER

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


@API_PATH.route("/windows", methods=["GET"])
def handle_windows():
    windows = get_windows()

    if windows == None:
        return jsonify({"error": "Failed to get windows"}), 500

    return jsonify({windows: windows}), 200


@API_PATH.route("/window_screenshot", methods=["POST"])
def handle_window_screenshot():
    req_data = request.get_json()
    window_title = req_data.get("window_title", "")

    screenshot_data = window_screenshot(window_title, FILE_DUMP)

    if screenshot_data == None:
        return jsonify({"error": "Failed to take screenshot"}), 500

    return jsonify(screenshot_data), 200

"""
Request: 
{
    "text": "User text", (Required)
    "type": "CarInfo" (Required)
}
"""

@API_PATH.route("/lang_to_struct", methods=["POST"])
def handle_lang_to_struct():
    req_data = request.get_json()

    if req_data.get("text") is None or req_data.get("type") is None:
        return jsonify({"error": "Missing required fields"}), 400

    text = req_data.get("text")
    struct_type = req_data.get("type")

    struct_converter = STRUCTS_CONVERTER.get(struct_type)
    if struct_converter is None:
        return jsonify({"error": "Invalid struct type"}), 400

    struct = struct_converter(text)
    if struct == None:
        return jsonify({"error": "Failed to convert text to struct"}), 500

    return jsonify(struct), 200


@API_PATH.route("/agent", methods=["POST"])
def handle_agent():
    pass


