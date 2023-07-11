from typing import List, TextIO
import time
import os
from dotenv import load_dotenv
import openai

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

QUESTION_FOR_LIST_FORMAT = "Transform the following list of {} into the expected list of lists of {} without comments. {}"
CONTEXT_FOR_LIST_FORMAT = """
I'm giving you a list of {} and guidelines, you have to create a list of list. For each {}, you have to create list with:
- first element, the {} word.
- second element, the translation in {}. You can use two word for a better comprehension seperate by a '-'.
- third element, the CEFR level between A1 and C2.
- fourth element, the frequency of the word scored ranging from 1 for rarely used to 10 for very commonly used.
{}
return only the list of the lists in python format. Use double quote for elements of list."""


HEADERS_CSV = lambda native, to_learn: {
    'verbs': [to_learn, native, 'level', 'frequency', 'type', 'info'],
    'adverbs': [to_learn, native, 'level', 'frequency', 'type'],
    'nouns': [to_learn, native, 'level', 'frequency', 'type'],
    'adjectives': [to_learn, native, 'level', 'frequency'],
}

def print_all(sentence: str, file: TextIO):
    print(sentence)
    print(sentence, file=file)

def get_more_info_for_context(folder: str):
    if folder == 'verbs':
        return """
        - fifth element, the type of verb choice the appropriate value between ACTION and STATE.
        - sixth element, choice the appropriate value between REGULAR and IRREGULAR.
        """
    if folder == 'adverbs':
        return "- fifth element, determine the appropriate type of adverb."
    if folder == 'nouns':
        return "- fifth element, determine the appropriate type of noun between ABSTRACT and CONCRETE."
    
def retry_api_call(max_attempts=10, delay=1):
    def decorator(api_call_func):
        def wrapper(*args, **kwargs):
            logfile = args[3]
            attempts = 0
            success = False

            while attempts < max_attempts and not success:
                try:
                    response = api_call_func(*args, **kwargs)
                    success = True  # L'appel API a réussi, sortir de la boucle while
                except Exception as e:
                    print_all(f"[ERROR_API] Error when call API: {e}", logfile)
                    attempts += 1
                    time.sleep(delay)

            if not success:
                print_all(f"[FATAL_ERROR] Échec de l'appel API après {max_attempts} tentatives.", logfile)
            return response
        return wrapper
    return decorator


@retry_api_call(max_attempts=10, delay=2)
def answer_to_the_sentence(question: str, context: str, type_word: str, logfile: TextIO, temperature=0.2):
    print_all(f"{' '*8}[API_CONTEXT] {context}", logfile)
    print_all(f"{' '*8}[API_QUESTION] {question}", logfile)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role':'system', 'content': context},
            {"role": "user", "content": question},    
        ],
        temperature=temperature,
    )
    answer = completion.choices[0].message.content
    answer_to_show = answer.split('\n')
    print_all(f"{' '*8}[API_ANSWER] {answer_to_show}", logfile)
    print_all(f"{' '*8}[API_TOKENS] {completion.usage['completion_tokens']}", logfile)
    tokens =  completion.usage['completion_tokens']
    return answer, tokens