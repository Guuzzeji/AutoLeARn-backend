from .perplexity import model_perplexity
from .vlm import vlm
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
import PIL.Image

gemini_model = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))


# groq_llm = ChatGroq(
#     # NOTE (Gabe): So of the models fuck with the agent system
#     model_name="qwen-2.5-32b",
#     temperature=0
# )


# @tool
def image_to_text(image_local_file_path: str, additional_context_for_image: str) -> str:
    """
    Call to convert a image to descriptive text that explains what the image is.
    """
    print("Called image to text from image path=", image_local_file_path,
          "context=", additional_context_for_image)
    
    vlm_response = vlm(image_local_file_path, additional_context_for_image)   

    if vlm_response is None:
        print("VLM response", "FAILED TO GENERATE IMAGE TEXT", "TRY GEMINI")
        try:        
            # When Groq FUCKS UP
            image = PIL.Image.open(image_local_file_path)
            response = gemini_model.models.generate_content(
                model="gemini-2.0-flash",
                contents=[
                    """
                    You are an AI automotive repair assistant with visual recognition capabilities. 
                    Your role is to analyze user-submitted images and provide clear, objective descriptions 
                    to assist in vehicle diagnostics and repair. All images given to you is the user's car.

                    Your goal is to describe the user's vehicle's condition, identify potential issues within 
                    the image, focus on key details.

                    Use the user additional context to provide context about the user's vehicle. 
                    If it align with the image given to you.
                    """,
                    f"USER ADDITIONAL CONTEXT: {additional_context_for_image}",
                    image
                    ])
            
            print("Gemini response", response)
            return response.text
        except Exception as e:
            print(e)
            return "Error could not understand image"

    print("VLM response", vlm_response)
    return vlm_response.choices[0].message.content


# @tool
def search_web(prompt: str) -> str:
    """
    Call to use AI to search the web and generate a summary of what it found.
    """
    print("Called search web")
    response = model_perplexity(prompt)
    print("Search web response", response)
    if response is None:
        return "Error could not generate response"
    return f"""
    {response["choices"][0]["message"]["content"]}
    
    resources: {response["citations"]}
    """

# tools = [search_web]

# # Initialize memory to persist state between graph runs
# checkpointer = MemorySaver()
# AGENT_MODEL = create_react_agent(groq_llm, tools, checkpointer=checkpointer)

# if __name__ == "__main__":
#     # Use the agent
#     config = {"configurable": {"thread_id": 42}}
#     for chunk in AGENT_MODEL.stream(
#         {"messages": [HumanMessage(
#             content="How do I change the oil in my 2014 Ford Explorer? Give me step by step instructions and sources")]}, config
#     ):
#         print(chunk)
#         print("----")
