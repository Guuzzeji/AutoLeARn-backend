import requests
import os

from dotenv import load_dotenv
load_dotenv()

"""
Output example:
{
  "id": "3c90c3cc-0d44-4b50-8888-8dd25736052a",
  "model": "sonar-pro",
  "object": "chat.completion",
  "created": 1724369245,
  "citations": [
    "https://www.astronomy.com/science/astro-for-kids-how-many-stars-are-there-in-space/",
    "https://www.esa.int/Science_Exploration/Space_Science/Herschel/How_many_stars_are_there_in_the_Universe",
    "https://www.space.com/25959-how-many-stars-are-in-the-milky-way.html",
    "https://www.space.com/26078-how-many-stars-are-there.html",
    "https://en.wikipedia.org/wiki/Milky_Way"
  ],
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "The number of stars in the Milky Way galaxy is estimated to be between 100 billion and 400 billion stars. The most recent estimates from the Gaia mission suggest that there are approximately 100 to 400 billion stars in the Milky Way, with significant uncertainties remaining due to the difficulty in detecting faint red dwarfs and brown dwarfs."
      },
      "delta": {
        "role": "assistant",
        "content": ""
      }
    }
  ],
  "usage": {
    "prompt_tokens": 14,
    "completion_tokens": 70,
    "total_tokens": 84
  }
}
"""

BASE_URL = "https://api.perplexity.ai/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
    "Content-Type": "application/json"
}


def model_perplexity(nl: str) -> dict[str] or None:
    """
    model perplexity
    """
    payload = {
      "model": "sonar",
      "messages": [
          {
              "role": "system",
              "content":
              """
              You are an expert AI assistant for vehicle diagnostics, troubleshooting, and repair guidance. 
              Provide accurate, clear, and actionable advice for users of all skill levels.
              
              Core Functions:
              - Diagnosis & Troubleshooting: Ask clarifying questions, suggest step-by-step solutions, and rank fixes by likelihood and difficulty.
              - Repair Guidance: Offer detailed repair instructions, list necessary tools, and highlight safety precautions.
              - Parts & Maintenance: Recommend compatible parts, fluids, and preventive care tips.
              - Technical Accuracy: Use precise terminology but simplify when needed, tailoring responses to the user’s experience level.
              
              Limitations & Ethics:
              - Do not assist with illegal modifications or emissions bypassing.
              - Encourage safe practices and compliance with manufacturer guidelines.
              - If unsure, suggest consulting a certified mechanic.

              Your Response Should Include:
              - ALWAYS INCLUDE A YOUTUBE VIDEO AS PART OF OUR SOURCES
              - Help users diagnose and fix common issues.
              - Provide step-by-step instructions for repair.
              - (MOST IMPORTANT) Identify what step the user (base off the user prompt) is currently on and provide feedback and further instructions to help them complete the process.
                - Otherwise, assume the user is at the beginning of the process.

              Maintain a helpful, professional tone. Be detailed and thorough.
              """
          },
      ],
      # "max_tokens": 3000,
      "temperature": 0.5,
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

    user_prompt = {
        "role": "user",
        "content": ""
    }

    try:
        user_prompt["content"] = nl
        payload["messages"].append(user_prompt)

        response = requests.request(
            "POST", BASE_URL, json=payload, headers=HEADERS)
        return response.json()

    except Exception as e:
        print(e)
        return None


if __name__ == "__main__":
    print(model_perplexity("How do I change the oil in a 2014 Ford Explorer?"))
