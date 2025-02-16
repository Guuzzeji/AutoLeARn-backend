"""
natural language to struct
"""
from .models.StepsTutorial import StepsTutorial
from .models.CarInfo import CarInfo
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()


groq_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.5
)

# NOTE (Gabe): if nl is "" it will default to
# {"make": "Toyota","model": "Corolla","year": 2015},
#  but works with nothing related information


def nl_to_CarInfo(nl: str) -> dict[str]:
    try:
        car_info_model = groq_llm.with_structured_output(CarInfo)
        return car_info_model.invoke(nl)
    except Exception as e:
        print(e)
        return None


def nl_to_StepsTutorial(nl: str) -> dict[str]:
    try:
        steps_tutorial_model = groq_llm.with_structured_output(StepsTutorial)
        return steps_tutorial_model.invoke(nl)
    except Exception as e:
        print(e)
        return None


STRUCTS_CONVERTER = {
    "CarInfo": nl_to_CarInfo,
    "StepsTutorial": nl_to_StepsTutorial
}

if __name__ == "__main__":
    print(nl_to_CarInfo("I own a Tesla Model 3 from 2020"))
    print(nl_to_CarInfo("I have a 2021 Ford Explorer and I hate it."))
    # print(nl_to_CarInfo("I don't own a car.")) # will raise error, just handle it and we should be good
