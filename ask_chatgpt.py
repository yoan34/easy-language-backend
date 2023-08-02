import os
from pathlib import Path
import openai
import csv
import time
import ast
from typing import List, TextIO
from dotenv import load_dotenv


from models.computer import Computer
from models.generator import Generator
from models.logger import Logger
from models.chatGPT import ChatGPT

# https://universaldependencies.org/u/dep/
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

# N_VERBS_ADJ_BY_REQUEST = 50
# N_NOUNS_BY_REQUEST = 100
# N_ADVERBS_BY_REQUEST = 20
N_VERBS_ADJ_BY_REQUEST = 15
N_NOUNS_BY_REQUEST = 15
N_ADVERBS_BY_REQUEST = 15
all_tokens = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}
all_words = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}

native_lang = "french"
target_lang = "english"
logger = Logger(f"{native_lang}_{target_lang}.log")
chatGPT = ChatGPT(logger)
computer = Computer(f"../data/{native_lang}_{target_lang}", logger)
generator = Generator(computer, native_lang, target_lang, logger, chatGPT)
generator.create_all_word_files()
generator.fix_word_files_errors()

print(generator.computer.path)
print(generator.computer.base_path)
input()
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
    global all_tokens
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
    all_tokens[type_word] += completion.usage['completion_tokens']
    return answer

# ---------------------------------------------------------------------------------------------------

def add_article_or_to_before_word(words: List[str], letter: str, folder: str):
    vowels = ['A', 'E', 'I', 'O', 'U', 'Y']
    words = [word.strip() for word in words]
    if folder == 'nouns':
        words = [f"an {line}" for line in words] if letter.upper() in vowels else [f"a {line}" for line in words]
    if folder == 'verbs':
        words = [f"to {word}" for word in words]
    return words


def remove_numeration_and_bad_word_from_file(file: Path):
    new_content = []
    for line in computer.read_file(file.name):
        if line[0].isdigit():
            word = line.split('. ')[1]
            word_formatted = f"{word.replace('.', '').strip()}\n"
            new_content.append(word_formatted)
            continue
        if 'Sorry,' in line:
            continue
        # CREER CONDITION POUR LES NOUN QUI SONT PAS INTEGRER CAR "a cat", "a" == "c"
        letter = file.stem[-1]
        if line.startswith(letter) or line.startswith(letter.capitalize()):
            line_formatted = f"{line.replace('.', '').strip()}\n"
            new_content.append(line_formatted)

    computer.write_file(file.name, sorted(new_content))
        

def remove_duplicate_word_from_file(filename: str):
    content = computer.read_file(filename)
    computer.write_file(filename, list(dict.fromkeys(content)))
  

def remove_compose_word_from_file(filename: str):
    new_content = [] 
    content = computer.read_file(filename)
        
    for word in content:
        if len(word.split(' ')) == 1:
            new_content.append(word)

    computer.write_file(filename, new_content)
      

def remove_conjugated_verb_from_file(filename: str):
    new_content = []
    content = computer.read_file(filename)
        
    for verb in content:
        if not verb.replace('\n', '').endswith('ed') or verb == 'need\n':
            new_content.append(verb)
        if verb.replace('\n', '').endswith('ing'):
            pass
            # print(f"{verb}  -> {path}")
    computer.write_file(filename, list(dict.fromkeys(new_content)))
        
# PURE FUNCTIONAL      
def check_and_update_all_list_of_word(native:str , to_learn: str, logfile: TextIO):
    global all_words
    path = f"{native}_{to_learn}"
    for folder in computer.change_directory(path).list_folders:
        for file in computer.change_directory(f"{folder.name}/list").list_files:
            remove_numeration_and_bad_word_from_file(file)
            remove_duplicate_word_from_file(file.name)
            remove_compose_word_from_file(file.name)
            if folder == 'verbs':
                remove_conjugated_verb_from_file(file.name)
            all_words[folder] += len(computer.read_file(file.name))



def create_all_list_of_word(native: str, to_learn: str, logfile: TextIO):
    global all_words
    type_of_words = ['verbs', 'nouns', 'adjectives', 'adverbs']
    
    for type_word in type_of_words:
        path = f'data/{native}_{to_learn}/{type_word}'
        os.makedirs(path)
        print_all(f"{' '*4}[CREATE_FOLDER]: {path}", logfile)
            
        for letter_code in range(ord('a'), ord('c')+1):
            letter = chr(letter_code)
            file_path = f"{path}/list/start_by_{letter}.txt"
            if os.path.exists(file_path):
                print_all(f"{' '*4}[ALREADY_EXIST] {file_path}", logfile)
                continue
            all_words[type_word] += create_list_of_word(type_word, letter, file_path, to_learn, logfile)
            print_all(f"{' '*4}[CREATE_FILE] {type_word}list/start_by_{letter}.txt sucessfully", logfile)
            print_all(' '*4 + "-"*80, logfile)


def create_list_of_word(type_word: str, letter: str, file_path: str, language: str, logfile: TextIO):
    info = "always in infinitive form" if type_word == "verbs" else ""
    number = N_VERBS_ADJ_BY_REQUEST if type_word in ['verbs', 'adjectives'] else N_NOUNS_BY_REQUEST if type_word == 'nouns' else N_ADVERBS_BY_REQUEST
    context = f"""Do not comment, just write one word per line without numbered it.
    Create a python list containing a minimum of {number} {language} {type_word} {info}, if possible, otherwise include as many as possible. Never comments, juste write {type_word}"""
    if type_word == 'nouns':
        context += "don't forget to put the appropriate article before the noun."
    question = f"Write {type_word} that start by the letter '{letter}'."
    response = answer_to_the_sentence(question, context, type_word, logfile)
    
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    total_words = 0
    with open(file_path, 'w', newline='') as file:
        file.write(response)
    with open(file_path, 'r') as file:  
        total_words = len(file.readlines())
            
    return total_words


def manage_incorrect_answer(question: str, context: str, type_word: str, logfile: TextIO):
    flag, tries, answer = True, 0, ''
    while flag:
        try:
            if tries:
                print_all(f"{' ' * 8}TRIES: {tries}", logfile)
                question = f"You answer is not correct, please use double quote.{question}"
            answer = answer_to_the_sentence(question, context, type_word, logfile, temperature=0.1)
            answer = ast.literal_eval(answer[answer.find('['):answer.rfind(']') + 1] )
            flag = False
            print_all(f"{' ' * 8}[GOOD_LITERAL_EVAL]", logfile)
        except Exception as e:
            tries += 1
            print_all(f"{' ' * 8}[ERROR_LITERAL_EVAL]: {e}", logfile)
            print_all(f"{' ' * 8}[ERROR_LITERAL_EVAL_ANSWER]: {answer}", logfile)
            time.sleep(1)
    return answer
    

def create_csv(native: str, to_learn: str, folder: str, filename: str, base_path:str, logfile: TextIO):
    letter = filename.split('.')[0][-1]
    words, new_content = [], []
    with open(f"{base_path}/list/{filename}", 'r') as f:
        words = f.readlines()
        
    words = add_article_or_to_before_word(words, letter, folder)

    for i in range(0, len(words), 10):
        info_to_add = get_more_info_for_context(folder)
        question = QUESTION_FOR_LIST_FORMAT.format(folder, folder, words[i:i+10])
        context = CONTEXT_FOR_LIST_FORMAT.format(folder, native, to_learn, folder, info_to_add)
        answer = manage_incorrect_answer(question, context, folder, logfile)
        new_content += answer

    with open(f"{base_path}/csv/{letter}.csv", "w", newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(HEADERS_CSV(native, to_learn)[folder])
        writer.writerows(new_content)
        print_all(f"{' '*2}[CREATE_CSV] File {base_path}/csv/{letter}.csv", logfile)


def create_all_csv(native: str, to_learn: str, logfile: TextIO):
    folders = os.listdir(f"data/{native}_{to_learn}")
    for folder in folders:
        base_path = f"data/{native}_{to_learn}/{folder}"
        files = os.listdir(f"{base_path}/list")
        if not os.path.exists(f"{base_path}/csv"):
            os.mkdir(f"{base_path}/csv")
            
        for file in files:
            if os.path.exists(f"{base_path}/csv/{file.split('.')[0][-1]}.csv"):
                print_all(f"{' '*4}[ALREADY_EXIST] {base_path}/csv/{file.split('.')[0][-1]}.csv.", logfile)
                continue
            create_csv(native, to_learn, folder, file, base_path, logfile)


def print_all(sentence: str, file: TextIO):
    print(sentence)
    print(sentence, file=file)


def create_data_for_language(native: str, to_learn: str):
    global all_tokens, all_words
    logfile = open(f"logs/{native}_{to_learn}_logs.txt", "w")
    print_all("[CREATE_ALL_LIST_OF_WORD]", logfile)
    create_all_list_of_word(native, to_learn, logfile)
    print_all("[CHECK_AND_UPDATE_ALL_LIST_OF_WORD]", logfile)
    check_and_update_all_list_of_word(native, to_learn, logfile)
    print_all("[CREATE_ALL_CSV]", logfile)
    create_all_csv(native, to_learn, logfile)
    print_all(f"[TOTAL_WORDS_BY_TYPE] {all_words}", logfile)
    print_all(f"[TOTAL_WORDS] {sum([all_words[key] for key in all_words])}", logfile)
    print_all(f"[TOTAL_TOKENS_BY_TYPE] {all_tokens}", logfile)
    print_all(f"[TOTAL_TOKENS] {sum([all_tokens[key] for key in all_tokens])}", logfile)
    print_all("[FINISH]", logfile)
    logfile.close()


if __name__ == "__main__":
    create_data_for_language("french", "english")

 

        
        