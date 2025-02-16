import os
import json
import ffmpeg
from flask import Blueprint, request, jsonify
from langchain_core.messages import HumanMessage

from ai.whisper import whisper
from xr.screen_capture import window_screenshot, filename_table
from ai.nl_to_struct import STRUCTS_CONVERTER
from ai.agent import search_web, image_to_text

import video.videoseg as video_seg
import video.extractJSONsplits as extractJSONsplits
import video.parsevtt as parsevtt
import video.subtitlesparse as subtitlesparse
import video.ytdown as ytdown


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
    req_data = request.get_json()

    if req_data.get("debug"):
        screenshot_data = window_screenshot("", FILE_DUMP)
        return jsonify(screenshot_data), 200 

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
    "filename": "file name", (Required)
    "car_info": "CarInfo (Copy struct look in model)", (Rquired)
}
"""
@API_PATH.route("/agent", methods=["POST"])
def handle_agent():
    req_data = request.get_json()

    if req_data.get("filename") is None or req_data.get("car_info") is None:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    car_info = request.json["car_info"]
    filename = request.json.get("filename")

    input_prompt = f"""
    User Car Issue Prompt: {car_info["issue_with_car"]}
    
    User provided Image as Text Description: {image_to_text(filename_table[filename], car_info["issue_with_car"])}
    
    Car Background Information: 
        - make: {car_info["make"]}
        - model: {car_info["model"]}
        - year: {car_info["year"]}
    """

    try:
        video_path = os.path.join(FILE_DUMP, "video.mp4")
        if os.path.isfile(video_path):
            os.remove(video_path)
            
        response = search_web(input_prompt)
        struct_converter = STRUCTS_CONVERTER.get("StepsTutorial")
        steps_tutorial = struct_converter(response)

        if steps_tutorial == None:
            return jsonify({"success": False, "error": "Failed to convert text to struct"}), 500
        
        sources = [weblink for weblink in steps_tutorial.get("sources", []) if "youtube.com" in weblink]

        if len(sources) > 0:
            ytdown.download_full_video_with_captions(sources[0], FILE_DUMP)
            sources = os.path.abspath(f"{FILE_DUMP}/video.mp4")
        else:
            sources = ""

        return jsonify({"success": True, "step_breakdown": steps_tutorial, "original_text": response, "youtube_link": sources}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500

# @API_PATH.route("/yt_dl", methods=["POST"])
# def handle_yt_dl():
#     req_data = request.get_json()

#     if req_data.get("url") is None:
#         return jsonify({"success": False, "error": "Missing required fields"}), 400
    
#     # download video
#     url = req_data.get("url")
#     ytdown.download_full_video_with_captions(url, FILE_DUMP)

#     return jsonify({"success": True, "video_path": os.path.abspath(f"{FILE_DUMP}/video.mp4")}), 200

@API_PATH.route("/segment_cleanup", methods=["POST"])
def handle_segment_cleanup():
    try:
        # Remove all video files from video_steps folder
        video_steps_path = os.path.join(FILE_DUMP)
        for file in os.listdir(video_steps_path):
            if file.endswith(".mp4"):
                os.remove(os.path.join(video_steps_path, file))

        print("All video files have been removed from the video_steps folder.")
        return jsonify({"success": True,}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500
