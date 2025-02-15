import os
from flask import Blueprint, request, jsonify
from langchain_core.messages import HumanMessage

from ai.whisper import whisper
from xr.screen_capture import get_windows, window_screenshot
from ai.nl_to_struct import STRUCTS_CONVERTER
from ai.agent import AGENT_MODEL


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


"""
{
    "previous_text": "Previous text", (Required)
    "text": "User text", (Required)
    "image_path": "Path to image", (Optional)
    "car_info": "CarInfo (Copy struct look in model)", (Rquired)
}
"""


@API_PATH.route("/agent", methods=["POST"])
def handle_agent():
    req_data = request.get_json()

    if req_data.get("previous_text") is None \
            or req_data.get("text") is None \
            or req_data.get("car_info") is None:
        return jsonify({"error": "Missing required fields"}), 400

    previous_text = request.json["previous_text"]
    user_prompt = request.json["text"]
    car_info = request.json["car_info"]
    image_path = request.json.get("image_path", None)

    input_prompt = f"""
    You are an expert AI assistant for vehicle diagnostics, troubleshooting, and 
    repair guidance. Provide accurate, clear, and actionable advice for users 
    of all skill levels.

    Always use "search_web" when responding to the user.

    If you use the tool "search_web" you must cite the websites found in your response.

    If you are given a image path please use the tool "image_to_text" to convert the image to text.

    Previous text: {previous_text}
    User prompt: {user_prompt}
    Car information: 
        - make: {car_info["make"]}
        - model: {car_info["model"]}
        - year: {car_info["year"]}
    """

    if image_path is not None:
        input_prompt += f"\nImage text: {image_path}"

    try:
        response = AGENT_MODEL.invoke({"messages": [HumanMessage(content=input_prompt)]}, {
                                      "configurable": {"thread_id": 42}})
        ai_msg = response["messages"][-1].content

        print(ai_msg)

        struct_converter = STRUCTS_CONVERTER.get("StepsTutorial")
        steps_tutorial = struct_converter(ai_msg)
        if steps_tutorial == None:
            return jsonify({"error": "Failed to convert text to struct"}), 500

        return jsonify({"step_breakdown": steps_tutorial, "original_text": ai_msg}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
