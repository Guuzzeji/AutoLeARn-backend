import json
import os
import ffmpeg

json_path = "processed_response.json"
video_path = "video.mp4"
output_dir = "video_steps"
os.makedirs(output_dir, exist_ok=True)

def time_to_seconds(timestamp):
    h, m, s = timestamp.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

with open(json_path, "r") as f:
    data = json.load(f)

# uses ffmpeg to split video into individuual segments
for step in data["steps"]:
    step_number = f"{step['step']:02}"
    title = step["title"].replace(" ", "_").replace("/", "_")
    start_time = step["start"]
    end_time = step["end"]
    start_sec = time_to_seconds(start_time)
    end_sec = time_to_seconds(end_time)
    duration = end_sec - start_sec

    output_filename = f"{step_number}_{title}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"Processing {output_filename} (ffmpeg-python)...")
    (
        ffmpeg
        .input(video_path, ss=start_time, t=duration)
        .output(output_path, c="copy")
        .overwrite_output()
        .run(quiet=True)
    )

print(f"ffmpeg-python: Video segments saved in '{output_dir}'")
