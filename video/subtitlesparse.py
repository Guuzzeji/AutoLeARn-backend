import requests
import os
import json
from pydantic import BaseModel
from typing import List, Dict

from dotenv import load_dotenv
load_dotenv()

""" Example Output
{
    "id": "8af0e70b-eff1-42a9-b128-740f3daa0bbd",
    "model": "sonar-pro",
    "created": 1739671625,
    "usage": {
        "prompt_tokens": 13276,
        "completion_tokens": 646,
        "total_tokens": 13922,
        "citation_tokens": 4915,
        "num_search_queries": 1
    },
    "citations": [
        "https://www.youtube.com/watch?v=WR14xqOH-iQ",
        "https://discussions.apple.com/thread/7181680",
        "https://www.youtube.com/watch?v=b1Fo_M_tj6w",
        "https://sendshort.ai/guides/youtube-chapters/",
        "https://support.microsoft.com/en-us/office/create-closed-captions-for-a-video-b1cfb30f-5b00-4435-beeb-2a25e115024b",
        "https://forum.videohelp.com/threads/370460-How-to-auto-create-time-and-date-subtitle"
    ],
    "object": "chat.completion",
    "choices": [
        {
            "index": 0,
            "finish_reason": "stop",
            "message": {
                "role": "assistant",
                "content": "Here's the JSON file with timestamps for the steps and other segments of the video:\n\n{\n  \"introduction\": {\n    \"start\": \"00:00:00.030\",\n    \"end\": \"00:01:53.040\"\n  },\n  \"steps\": [\n    {\n      \"step\": 1,\n      \"title\": \"Gathering the Necessary Tools for the fix\",\n      \"start\": \"00:01:53.040\",\n      \"end\": \"00:03:04.499\"\n    },\n    {\n      \"step\": 2,\n      \"title\": \"Locating the Oil Drain Plug\",\n      \"start\": \"00:07:08.250\",\n      \"end\": \"00:08:05.420\"\n    },\n    {\n      \"step\": 3,\n      \"title\": \"Preparing to Drain the Oil\",\n      \"start\": \"00:08:21.240\",\n      \"end\": \"00:09:31.540\"\n    },\n    {\n      \"step\": 4,\n      \"title\": \"Draining the Oil\",\n      \"start\": \"00:09:31.540\",\n      \"end\": \"00:10:57.930\"\n    },\n    {\n      \"step\": 5,\n      \"title\": \"Changing the Oil Filter\",\n      \"start\": \"00:11:45.210\",\n      \"end\": \"00:15:32.709\"\n    },\n    {\n      \"step\": 6,\n      \"title\": \"Reinstalling the Drain Plug\",\n      \"start\": \"00:10:57.930\",\n      \"end\": \"00:11:37.980\"\n    },\n    {\n      \"step\": 7,\n      \"title\": \"Adding New Oil\",\n      \"start\": \"00:15:33.380\",\n      \"end\": \"00:18:57.160\"\n    },\n    {\n      \"step\": 8,\n      \"title\": \"Disposing of Used Oil Properly\",\n      \"start\": \"00:19:38.360\",\n      \"end\": \"00:20:18.189\"\n    }\n  ],\n  \"other_segments\": {\n    \"jacking_up_car\": {\n      \"start\": \"00:03:04.499\",\n      \"end\": \"00:07:08.250\"\n    },\n    \"checking_oil_level\": {\n      \"start\": \"00:18:57.160\",\n      \"end\": \"00:19:38.360\"\n    },\n    \"conclusion\": {\n      \"start\": \"00:19:17.200\",\n      \"end\": \"00:19:38.360\"\n    }\n  }\n}"
            },
            "delta": {
                "role": "assistant",
                "content": ""
            }
        }
    ]
}
"""

class TimeSegment(BaseModel):
    step: int
    title: str
    start: str
    end: str

class VideoSegments(BaseModel):
    steps: List[TimeSegment]
    unnecessary_segments: List[Dict[str, str]]

# Load the JSON files
with open('video.json', 'r') as f:
    video_data = json.load(f)

with open('instructions.json', 'r') as f:
    instructions_data = json.load(f)

BASE_URL = "https://api.perplexity.ai/chat/completions"

PAYLOAD_TEMPLATE = {
    "model": "sonar-pro",
    "messages": [
        {
            "role": "system",
            "content": 
            """
            You are being given 2 json files, video.json is a video subtitle file with timestamps of each thing said.
            The 2nd is a instructions.json file that contains the step-by-step instructions that we are attempting to demonstrate in the video.
            
            Split the video.json file by timestamp into the steps defined by the instructions.json, and any unnecessary portions like the introduction, sponsor messages, endings, and any other unrelated segments.
            Output the timestamps for the steps and other segments of the video as a json file.
            """
        },

        {
            "role": "user",
            "content": f"Analyse these video subtitles and instructions to create timestamp segments of the video: {json.dumps(video_data)} {json.dumps(instructions_data)}"
        }

    ],

    "response_format": {
        "type": "json_schema",
        "json_schema": {"schema": VideoSegments.model_json_schema()}
    },
    # "max_tokens": 123,
    "temperature": 0.2,
    # "top_p": 0.9,
    # "search_domain_filter": None,
    # "return_images": False,
    # "return_related_questions": False,
    # "search_recency_filter": "<string>",
    # "top_k": 0,
    # "stream": False,
    # "presence_penalty": 0,
    # "frequency_penalty": 1,
    # "response_format": None
}

HEADERS = {
    "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
    "Content-Type": "application/json"
}

# Make the API request
response = requests.request("POST", BASE_URL, json=PAYLOAD_TEMPLATE.copy(), headers=HEADERS)

# Parse the JSON response
if response.status_code == 200:
    result = response.json()
    print(result)

    # Define Output Path
    output_path = "./response.json"

    # Save response data to JSON file
    with open(output_path, "w") as file:
        json.dump(result, file, indent=4)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
