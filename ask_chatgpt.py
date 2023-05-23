import os
import openai
import csv
import time
import ast
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


### CSV PART
def create_csv():
    pass

if __name__ == "__main__":
    consonnes = ['B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'X', 'Z']
    voyelles = ['A', 'E', 'I', 'O', 'U', 'Y']
    logfile = open('test_format_csv.txt', 'w')
    native = "test1"
    to_learn = "test2"
    folders = os.listdir(f"data/{native}_{to_learn}")
    for folder in folders:
        base_path = f"data/{native}_{to_learn}/{folder}"
        files = os.listdir(f"{base_path}/list")
        if not os.path.exists(f"{base_path}/csv"):
            os.mkdir(f"{base_path}/csv")
            
        for file in files:
            letter = file.split('.')[0][-1]
            filepath = f"data/{native}_{to_learn}/{folder}/list/{file}"
            # file by file, we have to take the list and ask to get a CSV format.
            words = []
            new_content = []
            with open(filepath, 'r') as f:
                words = f.readlines()
                
            words = [word.strip() for word in words]
            if letter.upper() in consonnes:
                words = [f"a {line}" for line in words]
            if letter.upper() in voyelles:
                words = [f"an {line}" for line in words]
            portion_size = 20
            total_items = len(words)

            for i in range(0, total_items, portion_size):
                portion = words[i:i+portion_size]
                
                # Have to ask chatgpt
                header_to_add = ''
                if folder == 'verbs':
                    header_to_add = "'type' to determine whether the verb is an ACTION verb or a STATE verb."
                    
                question = f"Transform the following list of {folder} into the expected list of lists of {folder} without comments. {portion}"
                context = f"""
                I'm giving you a list of {folder} and guidelines, you have to create a list of list. For each {folder}, you have to create list with:
                - first element, the English word.
                - second element, the translation in French. You can use two word for a better comprehension seperate by a '-'.
                - third element, the CEFR level between A1 and C2.
                - fourth element, the frequency of the word scored ranging from 1 for rarely used to 10 for very commonly used.
                return only the list of the lists in python format."""
                flag = True
                tries = 0
                while flag:
                    try:
                        if tries:
                            print(f'TRIES: {tries}')
                            question = f"You answer is not correct, please return only the python list.{question}"
                        answer, tokens = answer_to_the_sentence(question, context, logfile, temperature=0.1)
                        start_index = answer.find('[')
                        end_index = answer.rfind(']')
                        actual_list = ast.literal_eval(answer[start_index:end_index + 1] )
                        flag = False
                        print(f"GOOD: {answer}")
                    except Exception as e:
                        tries += 1
                        print(f'Error occur: {e}')
                        print(answer)
                        time.sleep(1)
                    
                new_content += actual_list
                print(tokens)
            with open(f"data/{native}_{to_learn}/{folder}/csv/{file}.csv", "w", newline='') as f:
                writer = csv.writer(f, delimiter=';')
                # Write the data to the CSV file
                writer.writerow(['english', 'french', 'level', 'frequency'])
                writer.writerows(new_content)
                print_all(f"File data/{native}_{to_learn}/{folder}/csv/{file} write successfully!", logfile)
            
    logfile.close()
            
 

        
        