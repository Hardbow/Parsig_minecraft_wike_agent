# from fastapi import FastAPI, UploadFile, HTTPException, File
# from fastapi.middleware.cors import CORSMiddleware
import dotenv
import os
import logging
import warnings

from openai import OpenAI
from langsmith import traceable

from models import Query, SearchFormat
from utils import get_context_of_the_page, get_links

dotenv.load_dotenv()
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
SMART_LLM = os.getenv("SMART_LLM", "gpt-4o-mini")

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(filename="app.log", encoding='utf-8'),  # Logs will be saved in app.log
        logging.StreamHandler()  # Contitue showing logs in the console
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug("Initialize logger")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@traceable(name="agent_core")
def agent_core():
    logger.debug(f"agent_core has started")
    system_prompt = [
        {"role": "system",
         "content": "You are a helpful assistant who helps create basic tutorial about play minecraft for novice gamer."},
        {"role": "system",
         "content": "You get information in raw html code and parse it. You collect text information related to playing in minecraft."},
    ]

    user_message = [
        {"role": "user",
         "content": "Now you get new data in html-format. Find in this data information about minecraft gaming useful for novice player and briefly tell what this information says."},
    ]
    information_on_how_to_play_minecraft = ""
    links = get_links()
    for link in links:
        logger.debug(f"Link for data is: {link}")
        new_data = get_context_of_the_page(url=f"{link}")
        new_data_info = [{"role": "user", "content": f"{new_data}"}]
        messages = system_prompt + user_message + new_data_info
        logger.debug(f"messages - {messages}")

        completion = client.chat.completions.create(
            model=SMART_LLM,
            messages=messages
        )

        add_information_on_how_to_play_minecraft = completion.choices[0].message.content.strip()

        logger.debug(f"""##################################################
add_information_on_how_to_play_minecraft:\n{add_information_on_how_to_play_minecraft}
##################################################""")
        information_on_how_to_play_minecraft += f"\n{add_information_on_how_to_play_minecraft}\n"

    # completion = client.chat.completions.create(model=SMART_LLM, messages=messages)
    # final_answer = completion.choices[0].message.content.strip()
    # logger.debug(f"#######################################\nfinal answer - {messages}")

    with open(file = 'recommendation.txt', mode="w", encoding="utf-8") as file:
        file.write(information_on_how_to_play_minecraft)

    return information_on_how_to_play_minecraft


if __name__ == "__main__":
    agent_core()
