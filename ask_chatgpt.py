import os
import openai
import csv
import time
from dotenv import load_dotenv

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

def create_list_of_word_and_get_token(type_word, letter, path, log_file):
    info = "always in infinitive form" if type_word == "verbs" else ""
    number = 50 if type_word in ['verbs', 'adjectives'] else 100 if type_word == 'nouns' else 20
    context = f"""Do not comment, just write one word per line without numbered it.
    Create a list containing a minimum of {number} {type_word} {info}, if possible, otherwise include as many as possible."""
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
            new_content.append(word.replace('.', ''))
            continue
        if 'Sorry,' in line:
            continue
        if line.startswith(letter) or line.startswith(letter.capitalize()):
            new_content.append(line.replace('.', ''))
    
    with open(path, 'w') as file:
        file.writelines(new_content)
        

def remove_duplicate_word(path: str):
    content = []
    with open(path, 'r') as file:
        content = file.readlines()
    
    
    with open(path, 'w') as file:
        file.writelines(list(dict.fromkeys(content)))
        
        
            


def check_and_update_all_list(native, to_learn, log_file):
    
 folders = os.listdir(f"data/{native}_{to_learn}")
 for folder in folders:
    files = os.listdir(f"data/{native}_{to_learn}/{folder}/list")
    for file in files:
        path = f"data/{native}_{to_learn}/{folder}/list/{file}"
        letter = file.split('.')[0][-1]
        remove_numeration_and_bad_word(path, letter)
        remove_duplicate_word(path)
        
        
        # with open(f"data/{native}_{to_learn}/{folder}/list/{file}", 'r') as f:
        #     for line in f:
        #         letter = file.split('.')[0][-1]
        #         if 'Sorry,' in line:
        #             print(f"data/{native}_{to_learn}/{folder}/list/{file}  --> SORRY,")
        #             break
        #         if not line.startswith(letter) and not line.startswith(letter.capitalize()):
        #             # mean its start by another word that not start by the good letter or its start with number
        #             print(f"data/{native}_{to_learn}/{folder}/list/{file} --> START: {line[0]}")
        #             break
         



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
            tokens, words = create_list_of_word_and_get_token(type_word, letter, path, log_file)
            print_all(f"     create file list/start_by_{letter}.csv sucessfully ({tokens} tokens)  -  ({words} {type_word})", log_file)
            tokens_per_type_word += tokens
            words_per_type_word += words
        print_all(f"Total tokens use for '{type_word}' -> {tokens_per_type_word} tokens.", log_file)
        print_all(f"Total words use for '{type_word}' -> {words_per_type_word} {type_word}.", log_file)
        all_tokens += tokens_per_type_word
        all_words += words_per_type_word
    log_file.close()
    check_and_update_all_list(native, to_learn, log_file)

if __name__ == "__main__":
    # Here we try to normalize the file for having a great format.
    #   - remove the number numerotation
    #   - remove the '.' at the end
    #   - remove duplicate value
    log_file = create_log_file('test1', 'test2')
    check_and_update_all_list('test1', 'test2', log_file)
 

        
        