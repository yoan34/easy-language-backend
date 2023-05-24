import os
import openai
import csv
import time
import ast
from typing import List
from dotenv import load_dotenv

from prompt import QUESTION_FOR_LIST_FORMAT, CONTEXT_FOR_LIST_FORMAT

# https://universaldependencies.org/u/dep/
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")


create_log_file = lambda native, to_learn: open(f"logs/{native}_{to_learn}_logs.txt", "w")


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
def answer_to_the_sentence(question, context, log_file, temperature=0.2):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role':'system', 'content': context},
            {"role": "user", "content": question},    
        ],
        temperature=temperature,
    )
    answer = completion.choices[0].message.content
    tokens = completion.usage['completion_tokens']
    return answer, tokens

def print_all(sentence, file):
    print(sentence)
    print(sentence, file=file)

# ---------------------------------------------------------------------------------------------------

def create_list_of_word_and_get_token(type_word, letter, path, language, log_file):
    info = "always in infinitive form" if type_word == "verbs" else ""
    number = 50 if type_word in ['verbs', 'adjectives'] else 100 if type_word == 'nouns' else 20
    context = f"""Do not comment, just write one word per line without numbered it.
    Create a list containing a minimum of {number} {language} {type_word} {info}, if possible, otherwise include as many as possible."""
    question = f"Write {type_word}s that start by the letter '{letter}'."
    response, tokens = answer_to_the_sentence(question, context, log_file)
    
    file_path = f"{path}/list/start_by_{letter}.txt"
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    total_words = 0
    with open(file_path, 'w', newline='') as file:
        file.write(response)
    with open(file_path, 'r') as file:  
        total_words = len(file.readlines())
            
    return tokens, total_words
         

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
        
            
def check_and_update_all_list(native, to_learn, log_file):
    
    words = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}
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
                words[folder] += len(f.readlines())
    print(words)
    print(f"total words: {sum([words[key] for key in words])}")


def format_and_create_csv_file():
    pass

def create_all_list_of_word(native, to_learn):
    """
    Create a structure like this.
    data/
     |__native_learn/
            |__verbs/
                |__list/
                     |__start_by_A.txt
                     |__start_by_B.txt
                     |__start_by_C.txt
                     |__...
                |__csv/
                     |__start_by_A.txt
                     |__start_by_B.txt
                     |__start_by_C.txt
                     |__...
    """
    type_of_words = ['verbs', 'nouns', 'adjectives', 'adverbs']
    all_tokens = 0
    all_words = 0
    log_file = create_log_file(native, to_learn)
    
    
    for type_word in type_of_words:
        tokens_per_type_word = 0
        words_per_type_word = 0
        path = f'data/{native}_{to_learn}/{type_word}'
        os.makedirs(path)
        print_all(f"create folder: {path}", log_file)
            
        for letter_code in range(ord('a'), ord('z')+1):
            letter = chr(letter_code)
            tokens, words = create_list_of_word_and_get_token(type_word, letter, path, to_learn, log_file)
            print_all(f"     create file list/start_by_{letter}.csv sucessfully ({tokens} tokens)  -  ({words} {type_word})", log_file)
            tokens_per_type_word += tokens
            words_per_type_word += words
        print_all(f"Total tokens use for '{type_word}' -> {tokens_per_type_word} tokens.", log_file)
        print_all(f"Total words use for '{type_word}' -> {words_per_type_word} {type_word}.", log_file)
        all_tokens += tokens_per_type_word
        all_words += words_per_type_word
    log_file.close()
    check_and_update_all_list(native, to_learn, log_file)


def add_article_or_to_before_word(words: List[str], letter: str, folder: str):
    vowels = ['A', 'E', 'I', 'O', 'U', 'Y']
    words = [word.strip() for word in words]
    if folder == 'nouns':
        words = [f"an {line}" for line in words] if letter.upper() in vowels else [f"a {line}" for line in words]
    if folder == 'verbs':
        words = [f"to {word}" for word in words]
    return words


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


def manage_incorrect_answer(question: str, context: str, logfile: any):
    flag, tries = True, 0
    while flag:
        try:
            if tries:
                print(f'TRIES: {tries}')
                question = f"You answer is not correct, please use double quote.{question}"
            answer, tokens = answer_to_the_sentence(question, context, logfile, temperature=0.1)
            answer = ast.literal_eval(answer[answer.find('['):answer.rfind(']') + 1] )
            flag = False
            print(f"GOOD: {answer}")
        except Exception as e:
            tries += 1
            print(f'Error occur: {e}')
            print(answer)
            time.sleep(1)
    return answer, tokens
    

### CSV PART
def create_csv(folder: str, filename: str, base_path:str, logfile: any):
    letter = filename.split('.')[0][-1]
    words, new_content = [], []
    with open(f"{base_path}/list/{filename}", 'r') as f:
        words = f.readlines()
        
    words = add_article_or_to_before_word(words, letter, folder)

    for i in range(0, len(words), 10):
        info_to_add = get_more_info_for_context(folder)
        question = QUESTION_FOR_LIST_FORMAT.format(folder, folder, words[i:i+10])
        context = CONTEXT_FOR_LIST_FORMAT.format(folder, folder, info_to_add)
        print(f"QUESTION: {question}")
        print(f"CONTEXT: {context}")
        answer, tokens = manage_incorrect_answer(question, context, logfile)
        new_content += answer

    with open(f"{base_path}/csv/{letter}.csv", "w", newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['english', 'french', 'level', 'frequency'])
        writer.writerows(new_content)
        print_all(f"File {base_path}/csv/{letter}.csv write successfully!", logfile)

def create_all_csv(native, to_learn):
    logfile = open('test_format_csv.txt', 'w')
    folders = os.listdir(f"data/{native}_{to_learn}")
    for folder in ['nouns']:
        base_path = f"data/{native}_{to_learn}/{folder}"
        files = os.listdir(f"{base_path}/list")
        if not os.path.exists(f"{base_path}/csv"):
            os.mkdir(f"{base_path}/csv")
            
        for file in files:
            create_csv(folder, file, base_path, logfile) 
    logfile.close()


def create_data_for_language(native, to_learn):
    create_all_list_of_word(native, to_learn)
    create_all_csv(native, to_learn)



if __name__ == "__main__":
    # create_data_for_language("test1", "test2")
    create_all_csv("test1", "test2")

 

        
        