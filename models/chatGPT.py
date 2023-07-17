from models.logger import Logger
import os
import openai
from dotenv import load_dotenv

from tools.categories import CATEGORIES, CONTEXT
from tools.decorators import chatgpt_log

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

class ChatGPT:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.category_tokens = {'verb': 0, 'adverb': 0, 'noun': 0, 'adjective': 0}

    @chatgpt_log
    def answer_to_generate_lexicon(self, question: str, context: str, type_word: str, temperature: float = 0.2):
        answer, tokens = ChatGPT.answer(question, context, temperature)
        self.category_tokens[type_word] += tokens
        return answer, tokens

    @staticmethod
    def answer(question: str, context: str, temperature: float = 0.2):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
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
    def get_context_to_generate_lexicon(target_lang: str, category: str):
        info = CATEGORIES[target_lang][category]['info']
        number = CATEGORIES[target_lang][category]['number']
        return CONTEXT.format(number, target_lang,  category, info)

    @staticmethod
    def get_question_to_generate_lexicon(category: str, letter: str):
        return f"Write {category} that start by the letter '{letter}'."
