import requests
from bs4 import BeautifulSoup
import os
import dotenv
from time import sleep
import sys

dotenv.load_dotenv()

def get_context_of_the_page(url: str) -> str:
    headers = {'User-Agent': f'{os.getenv("USER_AGENT")}'}
    res = requests.get(url, headers=headers)
    sleep(1)
    return res.text

text_raw = get_context_of_the_page(url='https://minecraft.wiki/')
soup = BeautifulSoup(text_raw, 'html.parser')
parsed_text_list = soup.find('div', id="fp-2") #= soup.find('div', class_='mw-parser-output').findAll("p")
parsed_str = ""
for item in parsed_text_list:
    parsed_str += str(item) + "\n"
print(parsed_str)
sys.exit()
parsed_main_links = soup.find('div', class_=mcw-mainpage-icons)
parsed_main_links = soup.find('div', id="fp-2")