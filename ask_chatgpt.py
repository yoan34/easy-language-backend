import os
import openai
import csv
import time
import ast
from typing import List, TextIO
from dotenv import load_dotenv

from constants import QUESTION_FOR_LIST_FORMAT, CONTEXT_FOR_LIST_FORMAT, HEADERS_CSV, get_more_info_for_context

# https://universaldependencies.org/u/dep/
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

N_VERBS_ADJ_BY_REQUEST = 5
N_NOUNS_BY_REQUEST = 10
N_ADVERBS_BY_REQUEST = 2
all_tokens = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}
all_words = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}

def retry_api_call(max_attempts=5, delay=1):
    def decorator(api_call_func):
        def wrapper(*args, **kwargs):
            log_file = args[2]
            attempts = 0
            success = False

            while attempts < max_attempts and not success:
                try:
                    response = api_call_func(*args, **kwargs)
                    success = True  # L'appel API a réussi, sortir de la boucle while
                except Exception as e:
                    print_all(f"Error when call API: {e}", log_file)
                    attempts += 1
                    time.sleep(delay)

            if not success:
                print_all(f"Échec de l'appel API après {max_attempts} tentatives.", log_file)
            return response
        return wrapper
    return decorator


@retry_api_call(max_attempts=5, delay=2)
def answer_to_the_sentence(question: str, context: str, type_word: str, log_file: TextIO, temperature=0.2):
    global all_tokens
    print_all(f"[CONTEXT] {context}", log_file)
    print_all(f"[QUESTION] {question}", log_file)
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role':'system', 'content': context},
            {"role": "user", "content": question},    
        ],
        temperature=temperature,
    )
    answer = completion.choices[0].message.content
    print_all(f"[TOKENS] {completion.usage['completion_tokens']}", log_file)
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


def remove_numeration_and_bad_word(path: str, letter: str):
    content = []
    new_content = []
    with open(path, 'r') as file:
        content = file.readlines()
    
    for line in content:
        if line[0].isdigit():
            word = line.split('. ')[1]
            word_formatted = f"{word.replace('.', '').strip()}\n"
            new_content.append(word_formatted)
            continue
        if 'Sorry,' in line:
            continue
        if line.startswith(letter) or line.startswith(letter.capitalize()):
            line_formatted = f"{line.replace('.', '').strip()}\n"
            new_content.append(line_formatted)
            
    new_content.sort()
    with open(path, 'w') as file:
        file.writelines(new_content)
        

def remove_duplicate_word(path: str):
    content = []
    with open(path, 'r') as file:
        content = file.readlines()
    
    with open(path, 'w') as file:
        file.writelines(list(dict.fromkeys(content)))
  

def remove_compose_word(path: str):
    content = []
    new_content = [] 
    with open(path, 'r') as file:
        content = file.readlines()
        
    for word in content:
        if len(word.split(' ')) == 1:
            new_content.append(word)
            
    with open(path, 'w') as file:
        file.writelines(new_content)   
      

def remove_conjugated_verb(path: str):
    content = []
    new_content = []
    with open(path, 'r') as file:
        content = file.readlines()
        
    for verb in content:
        if not verb.replace('\n', '').endswith('ed') or verb == 'need\n':
            new_content.append(verb)
        if verb.replace('\n', '').endswith('ing'):
            pass
            # print(f"{verb}  -> {path}")
        
    with open(path, 'w') as file:
        file.writelines(list(dict.fromkeys(new_content)))   
        
# PURE FUNCTIONAL      
def check_and_update_all_list_of_word(native:str , to_learn: str, logfile: TextIO):
    global all_words
    folders = os.listdir(f"data/{native}_{to_learn}")
    for folder in folders:
        files = os.listdir(f"data/{native}_{to_learn}/{folder}/list")
        for file in files:
            path = f"data/{native}_{to_learn}/{folder}/list/{file}"
            letter = file.split('.')[0][-1]
            remove_numeration_and_bad_word(path, letter)
            remove_duplicate_word(path)
            remove_compose_word(path)
            if folder == 'verbs':
                remove_conjugated_verb(path)

    for folder in folders:
        files = os.listdir(f"data/{native}_{to_learn}/{folder}/list")
        for file in files:
            path = f"data/{native}_{to_learn}/{folder}/list/{file}"
            with open(path, 'r') as f:
                all_words[folder] += len(f.readlines())
    print_all(f"words per type: {all_words}", logfile)
    print_all(f"total words: {sum([all_words[key] for key in all_words])}", logfile)


def create_all_list_of_word(native: str, to_learn: str, logfile: TextIO):
    type_of_words = ['verbs', 'nouns', 'adjectives', 'adverbs']
    
    for type_word in type_of_words:
        path = f'data/{native}_{to_learn}/{type_word}'
        os.makedirs(path)
        print_all(f"[CREATE_FOLDER]: {path}", logfile)
            
        for letter_code in range(ord('a'), ord('z')+1):
            letter = chr(letter_code)
            file_path = f"{path}/list/start_by_{letter}.txt"
            if os.path.exists(file_path):
                print_all(f"[ALREADY_EXIST] {file_path}", logfile)
                continue
            words = create_list_of_word(type_word, letter, file_path, to_learn, logfile)
            print_all(f"[CREATE_FILE] list/start_by_{letter}.csv sucessfully", logfile)


def create_list_of_word(type_word: str, letter: str, file_path: str, language: str, log_file: TextIO):
    info = "always in infinitive form" if type_word == "verbs" else ""
    number = N_VERBS_ADJ_BY_REQUEST if type_word in ['verbs', 'adjectives'] else N_NOUNS_BY_REQUEST if type_word == 'nouns' else N_ADVERBS_BY_REQUEST
    context = f"""Do not comment, just write one word per line without numbered it.
    Create a list containing a minimum of {number} {language} {type_word} {info}, if possible, otherwise include as many as possible."""
    if type_word == 'nouns':
        context += "don't forget to put the appropriate article before the noun."
    question = f"Write {type_word}s that start by the letter '{letter}'."
    response = answer_to_the_sentence(question, context, type_word, log_file)
    
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
                print_all(f'TRIES: {tries}', logfile)
                question = f"You answer is not correct, please use double quote.{question}"
            answer = answer_to_the_sentence(question, context, type_word, logfile, temperature=0.1)
            answer = ast.literal_eval(answer[answer.find('['):answer.rfind(']') + 1] )
            flag = False
            print_all(f"GOOD: {answer}", logfile)
        except Exception as e:
            tries += 1
            print_all(f'Error occur: {e}', logfile)
            print_all(answer, logfile)
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
        print_all(f"[ALREADY_EXIST] File {base_path}/csv/{letter}.csv", logfile)


def create_all_csv(native: str, to_learn: str, logfile: TextIO):
    folders = os.listdir(f"data/{native}_{to_learn}")
    for folder in folders:
        base_path = f"data/{native}_{to_learn}/{folder}"
        files = os.listdir(f"{base_path}/list")
        if not os.path.exists(f"{base_path}/csv"):
            os.mkdir(f"{base_path}/csv")
            
        for file in files:
            if os.path.exists(f"{base_path}/csv/{file.split('.')[0][-1]}.csv"):
                print_all(f"[ALREADY_EXIST] {base_path}/csv/{file.split('.')[0][-1]}.csv.", logfile)
                continue
            create_csv(native, to_learn, folder, file, base_path, logfile)


def print_all(sentence: str, file: TextIO):
    print(sentence)
    print(sentence, file=file)


def create_data_for_language(native: str, to_learn: str):
    logfile = open(f"logs/{native}_{to_learn}_logs.txt", "w")
    print_all("[CREATE_ALL_LIST_OF_WORD]", logfile)
    create_all_list_of_word(native, to_learn, logfile)
    print_all("[CHECK_AND_UPDATE_ALL_LIST_OF_WORD]", logfile)
    check_and_update_all_list_of_word(native, to_learn, logfile)
    print_all("[CREATE_ALL_CSV]", logfile)
    create_all_csv(native, to_learn, logfile)
    logfile.close()


if __name__ == "__main__":
    create_data_for_language("french", "english")

 

        
        