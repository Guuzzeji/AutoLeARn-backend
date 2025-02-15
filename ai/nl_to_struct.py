"""
natural language to struct
"""
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq

from .models.CarInfo import CarInfo
from .models.StepsTutorial import StepsTutorial

groq_llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.2
)

# NOTE (Gabe): if nl is "" it will default to 
# {"make": "Toyota","model": "Corolla","year": 2015},
#  but works with nothing related information
def nl_to_CarInfo(nl: str) -> dict[str]:
    car_info_model =  groq_llm.with_structured_output(CarInfo)
    return car_info_model.invoke(nl)

def nl_to_StepsTutorial(nl: str) -> dict[str]:
    car_info_model =  groq_llm.with_structured_output(StepsTutorial)
    return car_info_model.invoke(nl)

STRUCTS_CONVERTER = {
    "CarInfo": nl_to_CarInfo,
    "StepsTutorial": nl_to_StepsTutorial
}

if __name__ == "__main__":
    print(nl_to_CarInfo("I own a Tesla Model 3 from 2020"))
    print(nl_to_CarInfo("I have a 2021 Ford Explorer and I hate it."))
    # print(nl_to_CarInfo("I don't own a car.")) # will raise error, just handle it and we should be good

