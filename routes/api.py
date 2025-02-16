import os
from flask import Blueprint, request, jsonify
from langchain_core.messages import HumanMessage

from ai.whisper import whisper
from xr.screen_capture import window_screenshot, filename_table
from ai.nl_to_struct import STRUCTS_CONVERTER
from ai.agent import search_web, image_to_text


API_PATH = Blueprint("api", __name__, url_prefix="/api")

FILE_DUMP = "TEMP_SAVE_FOLDER"
os.makedirs(FILE_DUMP, exist_ok=True)


@API_PATH.route("/ping", methods=["GET"])
def handle_ping():
    return jsonify({"success": False, "message": "pong"}), 200


@API_PATH.route("/transcribe", methods=["POST"])
def handle_transcribe():
    if "audio" not in request.files:
        return jsonify({"success": False, "error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    file_path = os.path.join(FILE_DUMP, audio_file.filename)
    audio_file.save(file_path)

    response = whisper(file_path)

    if response == None:
        return jsonify({"success": False, "error": "Failed to transcribe audio"}), 500

    response["success"] = True
    return jsonify(response), 200


@API_PATH.route("/window_screenshot", methods=["POST"])
def handle_window_screenshot():
    # req_data = request.get_json()
    screenshot_data = window_screenshot("Oculus - Google Chrome", FILE_DUMP)
    if screenshot_data == None:
        return jsonify({"success": False, "error": "Failed to take screenshot"}), 500
    
    screenshot_data["success"] = True
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
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    text = req_data.get("text")
    struct_type = req_data.get("type")

    struct_converter = STRUCTS_CONVERTER.get(struct_type)
    if struct_converter is None:
        return jsonify({"success": False, "error": "Invalid struct type"}), 400

    struct = struct_converter(text)
    if struct == None:
        return jsonify({"success": False, "error": "Failed to convert text to struct"}), 500

    struct["success"] = True
    return jsonify(struct), 200


"""
{
    "image_file_name": "file name", (Required)
    "car_info": "CarInfo (Copy struct look in model)", (Rquired)
}
"""
@API_PATH.route("/agent", methods=["POST"])
def handle_agent():
    req_data = request.get_json()

    if req_data.get("image_file_name") is None or req_data.get("car_info") is None:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    car_info = request.json["car_info"]
    image_file_name = request.json.get("image_file_name")

    input_prompt = f"""
    User Car Issue Prompt: {car_info["issue_with_car"]}
    
    User provided Image as Text Description: {image_to_text(filename_table[image_file_name], car_info["issue_with_car"])}
    
    Car Background Information: 
        - make: {car_info["make"]}
        - model: {car_info["model"]}
        - year: {car_info["year"]}
    """

    try:
        response = search_web(input_prompt)
        struct_converter = STRUCTS_CONVERTER.get("StepsTutorial")
        steps_tutorial = struct_converter(response)

        if steps_tutorial == None:
            return jsonify({"success": False, "error": "Failed to convert text to struct"}), 500

        return jsonify({"success": True, "step_breakdown": steps_tutorial, "original_text": response}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500
