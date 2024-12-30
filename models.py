from pydantic import BaseModel

class Query(BaseModel):
    question: str
    context: str
    history: str

# class Models(str, Enum):
#     smart_llm = os.getenv('SMART_LLM', "gpt-4o-mini")
#     simple_llm = os.getenv('SIMPLE_LLM', "gpt-3.5-turbo")

class SearchFormat(BaseModel):
    information_on_how_to_play_minecraft: str
    links_you_what_to_check_and_their_description: str
    need_additional_search_on_another_page: bool
    link_to_page_with_required_information_we_will_now_receive: str