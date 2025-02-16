import os
import base64
from groq import Groq
from dotenv import load_dotenv
load_dotenv()


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
            to assist in vehicle diagnostics and repair. All images given to you is the user's car.

            Your goal is to describe the user's vehicle's condition, identify potential issues within 
            the image, focus on key details.

            Use the user additional context to provide context about the user's vehicle. 
            If it align with the image given to you.
            """
        },
        {
            "type": "text",
            "text": "USER ADDITIONAL CONTEXT: "  # user context
        },
        {
            "type": "image_url",
            # NOTE: image has to be correct / same type, GROQ get assy when not using correct image data
            "image_url":
            {
                "url": "data:image/jpeg;base64,",  # base64 encoded image
            },
        },
    ],
}


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def vlm(image_path: str, nl: str) -> dict[str] or None:
    try:
        user_prompt = dict(USER_PROMPT_TEMPLATE)
        user_prompt["content"][1]["text"] += nl
        user_prompt["content"][2]["image_url"]["url"] += image_to_base64(
            image_path)

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
