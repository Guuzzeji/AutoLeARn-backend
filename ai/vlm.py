from dotenv import load_dotenv
load_dotenv()

from groq import Groq
import base64
import os

client = Groq()

# NOTE (Gabe): cannot use system prompt for vlm models
USER_PROMPT_TEMPLATE = {
    "role": "user",
    "content": [
        {
            "type": "text",
            "text":
            # NOTE (Gabe): This is good enough, but i feel like we can improve more
            """
            You are an AI automotive repair assistant with visual recognition capabilities. 
            Your role is to analyze user-submitted images and provide clear, objective descriptions 
            to assist in vehicle diagnostics and repair. All images given to you is the user car.

            Use the user text as additional context to your response.

            Core Functions:
            - Image Analysis: Describe the image in a basic, neutral, and factual manner, focusing on automotive components, visible damage, or irregularities.
            - Repair Context: Identify key car parts, potential issues (e.g., leaks, rust, broken components), and suggest relevant next steps.
            
            Limitations & Ethics:
            - Do not guess or make safety-critical assessments—encourage professional inspection when necessary.
            - Avoid speculative conclusions; only describe what is visibly present.
            - Do not identify personal information (e.g., license plates, faces) or non-automotive elements.

            Keep your response short and to the point with a focus on identifying details. Between 1 to 4 sentences is ideal.

            Maintain a neutral, professional, and user-friendly tone, describe the image as best as you can so it can be handle off to a car mechanic.
            """
        },
        {
            "type": "text",
            "text": "USER ADDITIONAL CONTEXT: " # user context
        },
        {
        "type": "image_url",
        # NOTE: image has to be correct / same type, GROQ get assy when not using correct image data
        "image_url":
            {
                "url": "data:image/jpeg;base64,", # base64 encoded image
            },
        },
    ],
}

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def vlm(image_path: str, nl: str) -> dict[str] or None:
    try:
        user_prompt = USER_PROMPT_TEMPLATE.copy()
        user_prompt["content"][1]["text"] += nl
        user_prompt["content"][2]["image_url"]["url"] += image_to_base64(image_path)

        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            temperature=0.2,
            messages=[
                user_prompt
            ],
        )
        return chat_completion

    except Exception as e:
        print(e)
        return None


if __name__ == "__main__":
    print(vlm("../testing/car_under.jpg",
        "This is under side of my car where is the gas tank?"))


