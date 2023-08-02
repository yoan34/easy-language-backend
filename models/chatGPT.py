from models.logger import Logger
import os
import openai
from dotenv import load_dotenv

from tools.categories import (
    CATEGORIES,
    QUESTION_FOR_GENERATE_LIST_WORD,
    QUESTION_GENERATE_CSV_ROWS,
    get_more_info_for_context
)
from tools.decorators import chatgpt_log, retry_api_call

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

class ChatGPT:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.category_tokens = {'verb': 0, 'adverb': 0, 'noun': 0, 'adjective': 0}

    
    @chatgpt_log
    @retry_api_call(max_attempts=10, delay=2)
    def answer_to_generate_lexicon(self, question: str, context: str, type_word: str, temperature: float = 0.2):
        answer, tokens = ChatGPT.answer(question, context, temperature)
        self.category_tokens[type_word] += tokens
        return answer, tokens

    @staticmethod
    def answer(question: str, context: str, temperature: float = 0.2):
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {'role': 'system', 'content': context},
                {"role": "user", "content": question},
            ],
            temperature=temperature,
        )
        answer = completion.choices[0].message.content
        tokens = completion.usage['completion_tokens']
        return answer, tokens

    @staticmethod
    def get_context_to_generate_lexicon(target_lang: str, category: str, letter: str) -> str:
        info = CATEGORIES[target_lang][category]['info']
        number = CATEGORIES[target_lang][category]['number']
        return QUESTION_FOR_GENERATE_LIST_WORD.format(number, category, target_lang, letter)

    @staticmethod
    def get_question_to_generate_lexicon(target_lang:str, category: str, letter: str) -> str:
        number = CATEGORIES[target_lang][category]['number']
        return f"Write {number} {category}s that start only by the letter '{letter}'."

    @staticmethod
    def get_question_to_generate_csv(target_lang: str, native_lang: str, category: str, words: list[str]) -> str:
        info = get_more_info_for_context(category)
        return QUESTION_GENERATE_CSV_ROWS.format(category, category, target_lang, native_lang, info, category, words)