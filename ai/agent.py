from .perplexity import model_perplexity
from .vlm import vlm
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
load_dotenv()


groq_llm = ChatGroq(
    # NOTE (Gabe): So of the models fuck with the agent system
    model_name="qwen-2.5-32b",
    temperature=0
)


# @tool
def image_to_text(image_local_file_path: str, additional_context_for_image: str) -> str:
    """
    Call to convert a image to descriptive text that explains what the image is.
    """
    print("Called image to text from image path=", image_local_file_path,
          "context=", additional_context_for_image)
    vlm_response = vlm(image_local_file_path, additional_context_for_image)
    print("VLM response", vlm_response.choices[0].message.content)
    if vlm_response is None:
        return "Error could not understand image"
    return vlm_response.choices[0].message.content


@tool
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

tools = [search_web]

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()
AGENT_MODEL = create_react_agent(groq_llm, tools, checkpointer=checkpointer)

if __name__ == "__main__":
    # Use the agent
    config = {"configurable": {"thread_id": 42}}
    for chunk in AGENT_MODEL.stream(
        {"messages": [HumanMessage(
            content="How do I change the oil in my 2014 Ford Explorer? Give me step by step instructions and sources")]}, config
    ):
        print(chunk)
        print("----")
