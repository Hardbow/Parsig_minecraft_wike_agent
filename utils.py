import requests
import os
from bs4 import BeautifulSoup
import dotenv
from time import sleep

dotenv.load_dotenv()

def get_context_of_the_page(url: str ='https://minecraft.wiki/') -> str:
    headers = {'User-Agent': f'{os.getenv("USER_AGENT")}'}
    text_raw = requests.get(url, headers=headers)
    soup = BeautifulSoup(text_raw.text, 'html.parser')
    links_parsed = soup.find('div', id="fp-2")
    text_parsed_list = soup.find('div', class_='mw-parser-output').findAll("p")
    text_parsed_str = ""
    for item in text_parsed_list:
        text_parsed_str += str(item) + "\n"
    sleep(5)
    return text_parsed_str + "\n\n" + str(links_parsed)

