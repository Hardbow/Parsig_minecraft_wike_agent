# from fastapi import FastAPI, UploadFile, HTTPException, File
# from fastapi.middleware.cors import CORSMiddleware
import dotenv
import os
import logging
import warnings

from openai import OpenAI
from langsmith import traceable

from models import Query, SearchFormat
from utils import get_context_of_the_page

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
    system_prompt = [{"role": "system",
                      "content": "You are a helpful assistant who helps create basic tutorial about play minecraft for novice gamer."},
                     # {"role": "system",
                     #  "content": "You start to get information from pages of the site 'https://minecraft.wiki' and its sub-pages"},
                     {"role": "system",
                      "content": "You get information in raw condition and parse it. You collect text information related to playing in minecraft and links for additional information"},
                     {"role": "system",
                      "content": "You can use function 'get_context_of_the_page' for getting necessary information by following links."},
                     {"role": "system",
                      "content": "You decide do you need additional information which is situated on another pages through the links. If you need this information use function 'get_context_of_the_page'to get it."}
                     ]

    user_message = [
        {"role": "user",
         "content": "Now you get new information in html-format. Find in this data information about minecraft gaming useful for novice player and briefly tell what this information says. Put you answer in 'information_on_how_to_play_minecraft' filed."},
        {"role": "user",
         "content": "Now you get new information in html-format. Find in this data information about links that may be most useful for combining information for minecraft tutorial. Put this links and its short description into 'links_you_what_to_check_and_their_description' field."},
        {"role": "user",
         "content": "Decide do you need more information for minecraft tutorial for very novice player. Decide Yes (True) or No (False) and put answer into 'need_additional_search_on_another_page' field."},
        {"role": "user",
         "content": "If you need more information choose the most useful links for information and put in into 'link_to_page_with_required_information_we_will_now_receive' field"},
    ]

    new_information_prompt = [{"role": "assistant",
                               "content": "You have got new information in html format from web-page."}
                              ]

    # history_game_prompt = [
    #     {"role": "assistant", "content": "You have previously collected this information for minecraft tutorial"}
    # ]

    history_links_prompt = [{"role": "assistant",
                             "content": "You have previously collected this information about links that can be useful for combining information for minecraft tutorial"}
                            ]
    visited_links_prompt = [{"role": "assistant",
                             "content": "Don't choose the following links for searching"}
                            ]

    information_on_how_to_play_minecraft = ""
    links_you_what_to_check_and_their_description = ""
    links_you_have_visited = ""
    is_information_enough = False
    messages = []
    round_number = 0
    new_data = get_context_of_the_page()
    logger.debug(f"Basic Data is: {new_data}")

    while not is_information_enough and round_number < 5:
        logger.debug(f"Round number: {round_number}")
        # game_info = [{"role": "assistant", "content": f"{information_on_how_to_play_minecraft}"}]
        links_info = [{"role": "assistant", "content": f"{links_you_what_to_check_and_their_description}"}]
        visited_links_info = [{"role": "assistant", "content": f"{links_you_have_visited}"}]
        new_data_info = [{"role": "assistant", "content": f"This is a new information in html format:\n{new_data}"}]
        messages = system_prompt + user_message + new_information_prompt + new_data_info + history_links_prompt + links_info + visited_links_prompt + visited_links_info

        logger.debug(f"messages - {messages}")

        completion = client.beta.chat.completions.parse(
            model=SMART_LLM,
            messages=messages,
            response_format=SearchFormat
        )

        add_information_on_how_to_play_minecraft = completion.choices[0].message.parsed.information_on_how_to_play_minecraft
        links_you_what_to_check_and_their_description = completion.choices[
            0].message.parsed.links_you_what_to_check_and_their_description
        need_additional_search_on_another_page = completion.choices[
            0].message.parsed.need_additional_search_on_another_page
        link_to_page_with_required_information_we_will_now_receive = completion.choices[
            0].message.parsed.link_to_page_with_required_information_we_will_now_receive

        information_on_how_to_play_minecraft += "\n" + str(add_information_on_how_to_play_minecraft)

        # game_info += [{"role": "assistant", "content": f"{information_on_how_to_play_minecraft}"}]
        links_info += [{"role": "assistant", "content": f"{links_you_what_to_check_and_their_description}"}]

        logger.debug(f"""##################################################
\nadd_information_on_how_to_play_minecraft:\n{add_information_on_how_to_play_minecraft},
\nlinks_you_what_to_check_and_their_description:\n{links_you_what_to_check_and_their_description},
\nneed_additional_search_on_another_page:\n{need_additional_search_on_another_page},
\nlink_to_page_with_required_information_we_will_now_receive:\n{link_to_page_with_required_information_we_will_now_receive}\n""")

        if need_additional_search_on_another_page:
            new_data = get_context_of_the_page(url=link_to_page_with_required_information_we_will_now_receive)
            links_you_have_visited += f"\n{link_to_page_with_required_information_we_will_now_receive}"
            # messages.append({"role": "assistant",
            #                  "content": f"This is html information in link {link_to_page_with_required_information_we_will_now_receive}\n{data}"})

        round_number += 1


    # completion = client.chat.completions.create(model=SMART_LLM, messages=messages)
    # final_answer = completion.choices[0].message.content.strip()
    logger.debug(f"#######################################\nfinal answer - {messages}")

    with open(file = 'recommendation.txt', mode="w", encoding="utf-8") as file:
        file.write(information_on_how_to_play_minecraft)

    return messages


if __name__ == "__main__":
    query = Query(
        question="question",
        context="context",
        history="history"
    )

    agent_core()
    url = 'https://minecraft.wiki/w/Mob'
