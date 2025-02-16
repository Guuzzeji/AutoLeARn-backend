import os
import json
import requests
from typing import List, Dict
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
FILE_DUMP = "TEMP_SAVE_FOLDER"
BASE_URL = "https://api.perplexity.ai/chat/completions"

class TimeSegment(BaseModel):
    """Represents a timestamped step in the video."""
    step: int
    title: str
    start: str
    end: str

class VideoSegments(BaseModel):
    """Defines the structure for video segmentation output."""
    steps: List[TimeSegment]
    unnecessary_segments: List[Dict[str, str]]

def ensure_directory_exists():
    """Ensures the temporary save folder exists."""
    os.makedirs(FILE_DUMP, exist_ok=True)

def load_json_files():
    """Loads video.json and instructions.json files."""
    try:
        with open(f"{FILE_DUMP}/video.json", 'r') as f:
            video_data = json.load(f)

        return video_data
    except FileNotFoundError as e:
        print(f"Error: Missing JSON file - {e}")
        return None, None

def generate_payload(video_data):
    """Generates the API payload for video segmentation."""
    return {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": """
                You are being given 2 JSON files: 
                - `video.json` contains video subtitle timestamps.
                - `instructions.json` contains step-by-step instructions demonstrated in the video.

                Your task is to analyze these files and split `video.json` into timestamped segments based on the steps in `instructions.json`, while also identifying unnecessary segments like introductions, sponsor messages, and unrelated sections.

                Output the timestamps for all relevant segments as a structured JSON response. Split into 2 main parts steps and unnecessary outputted in the following format:
                {
                  "steps": [
                    {
                      "step": X,
                      "title": "XXXX",
                      "start": "XX:XX:XX.XXX",
                      "end": "XX:XX:XX.XXX"
                    },
                    ...
                  ],
                    "unnecessary_segments": [
                      {
                        "title": "Introduction",
                        "start": "XX:XX:XX.XXX",
                        "end": "XX:XX:XX.XXX"
                      },
                      ...
                    }
                  ]
                } 
                """
            },
            {
                "role": "user",
                "content": f"Analyze these subtitles and instructions: {json.dumps(video_data)}"
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": VideoSegments.model_json_schema()}
        },
        "temperature": 0.2
    }

def send_request(payload):
    """Sends the API request and returns the response JSON."""
    headers = {
        "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}\n{response.text}")
        return None

def save_response(result):
    """Saves the API response to a JSON file."""
    output_path = f"{FILE_DUMP}/response.json"
    with open(output_path, "w") as file:
        json.dump(result, file, indent=4)
    print(f"Response saved to {output_path}")

# def main():
#     """Main function that executes the script."""
#     ensure_directory_exists()
#     video_data, instructions_data = load_json_files()

#     if video_data is None or instructions_data is None:
#         print("Error: JSON files could not be loaded.")
#         return

#     payload = generate_payload(video_data)
#     result = send_request(payload)

#     if result:
#         save_response(result)

# if __name__ == "__main__":
#     main()

