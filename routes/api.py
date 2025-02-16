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
        response = search_web(input_prompt)
        struct_converter = STRUCTS_CONVERTER.get("StepsTutorial")
        steps_tutorial = struct_converter(response)

        if steps_tutorial == None:
            return jsonify({"success": False, "error": "Failed to convert text to struct"}), 500

        return jsonify({"success": True, "step_breakdown": steps_tutorial, "original_text": response}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500

@API_PATH.route("/yt_dl", methods=["POST"])
def handle_yt_dl():
    req_data = request.get_json()

    if req_data.get("url") is None:
        return jsonify({"success": False, "error": "Missing required fields"}), 400

    # download video
    url = req_data.get("url")
    ytdown.download_full_video_with_captions(url, FILE_DUMP)

    # parse vtt
    cues = parsevtt.parse_vtt(f"{FILE_DUMP}/video.en.vtt")
    groups = parsevtt.merge_cues(cues)
    json_output = parsevtt.export_to_json(groups, f"{FILE_DUMP}/video.json")

    # subtitles
    video_data = subtitlesparse.load_json_files()
    if video_data is None:
        print("Error: JSON files could not be loaded.")
        return jsonify({"success": False, "error": "JSON files could not be loaded"}), 500

    # send request
    payload = subtitlesparse.generate_payload(video_data)
    result = subtitlesparse.send_request(payload)
    if result:
        subtitlesparse.save_response(result)

    # extract json
    data = None
    with open(f"{FILE_DUMP}/response.json", 'r', encoding='utf-8') as file:
        data = json.load(file)

    if data is None:
        return jsonify({"success": False, "error": "Failed to extract JSON"}), 500

    if isinstance(data, dict) and "choices" in data:
        text_content = data["choices"][0]["message"]["content"]  # Adjust this based on actual structure
    else:
        text_content = json.dumps(data)
        
    stuff = extractJSONsplits.extract_json_from_text(text_content)
    
    with open(f"{FILE_DUMP}/processed_response.json", "w", encoding='utf-8') as file:
        #json.dump(extracted_json, file, indent=4)
        file.write(stuff)

    # video segments
    with open(f"{FILE_DUMP}/processed_response.json", "r") as f:
        data = json.load(f)

    # uses ffmpeg to split video into individuual segments
    for step in data["steps"]:
        step_number = f"{step['step']:02}"
        title = step["title"].replace(" ", "_").replace("/", "_")
        start_time = step["start"]
        end_time = step["end"]
        start_sec = video_seg.time_to_seconds(start_time)
        end_sec = video_seg.time_to_seconds(end_time)
        duration = end_sec - start_sec

        output_filename = f"{step_number}_{title}.mp4"
        output_path = os.path.join(FILE_DUMP, "video_steps",output_filename)
        
        print(f"Processing {output_filename} (ffmpeg-python)...")
        (
            ffmpeg
            .input(f"{FILE_DUMP}/video.mp4", ss=start_time, t=duration)
            .output(output_path, c="copy")
            .overwrite_output()
            .run(quiet=True)
        )

    # read folder
    files = os.listdir(f"{FILE_DUMP}/video_steps")
    file_list = []
    for file in files:
        if file.endswith(".mp4"):
            file_list.append({
                "file_path": os.path.join(f"{FILE_DUMP}/video_steps", file),
                "step_number": int(file.split("_")[0]),
            })

    print(f"Found {len(file_list)} video segments in video_steps folder.")

    return jsonify({"success": True, "video_segments": file_list}), 200

@API_PATH.route("/segment_cleanup", methods=["POST"])
def handle_segment_cleanup():
    try:
        # Remove all video files from video_steps folder
        video_steps_path = os.path.join(FILE_DUMP, "video_steps")
        for file in os.listdir(video_steps_path):
            if file.endswith(".mp4"):
                os.remove(os.path.join(video_steps_path, file))

        print("All video files have been removed from the video_steps folder.")
        return jsonify({"success": True,}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False, "error": str(e)}), 500
