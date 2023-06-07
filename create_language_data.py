import os
import csv
import time
import ast
from typing import List, TextIO


"""
Il me faut créer des classes pour être plus clair. 
Actuellement, je créer des fichier 'txt' simplement pour stocker les liste de mots.
Je check/update les fichier 'txt'.
Je créer des fichiers "csv" pour avoir plus d'information sur les mots.
Une fois valider, je dois appliquer le calcule de la distribution.
A savoir que les score de fréquence se retrouve entre [1, 10].
Je dois demander à chatGPT le score de fréquence en lui fournissant une liste de mot d'un certain niveau:
    def create_frequency_score(words, repartition)
    avec repartition: [20%, 30%, 30%, 20%] sur 4 étapes
                      [15+14+13+12+11+9+8+7+6+5] sur 10 étapes == 100%
                      
                      
                      
Il faut également créer des Classes pour gérer mieux les fichiers/méthodes.

"""

from tools.constants import (
    QUESTION_FOR_LIST_FORMAT,
    CONTEXT_FOR_LIST_FORMAT,
    HEADERS_CSV,
    get_more_info_for_context,
    answer_to_the_sentence,
    print_all
)

# https://universaldependencies.org/u/dep/


N_VERBS_ADJ_BY_REQUEST = 50
N_NOUNS_BY_REQUEST = 100
N_ADVERBS_BY_REQUEST = 20
CSV_STEP_FOR_CREATE_ROW = 5
# N_VERBS_ADJ_BY_REQUEST = 15
# N_NOUNS_BY_REQUEST = 15
# N_ADVERBS_BY_REQUEST = 15
ARTICLE_ALLOW = ['a', 'an', 'the', 'un', 'une', 'la', 'le'] #fr et en
all_tokens = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}
all_words = {'verbs': 0, 'adverbs': 0, 'nouns': 0, 'adjectives': 0}



# ---------------------------------------------------------------------------------------------------

def add_article_or_to_before_word(words: List[str], letter: str, folder: str):
    words = [word.strip() for word in words]
    if folder == 'verbs':
        words = [f"to {word}" for word in words]
    return words


def remove_numeration_and_bad_word(language: str, path: str, letter: str):
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
        if line[0] == '-':
            word = line.split('- ')[1]
            word_formatted = f"{word.replace('.', '').strip()}\n"
            new_content.append(word_formatted)
        if 'Sorry,' in line:
            continue
        # CREER CONDITION POUR LES NOUN QUI SONT PAS INTEGRER CAR "a cat", "a" != "c"
        
        if line.startswith(letter) or line.startswith(letter.capitalize()):
            line_formatted = f"{line.replace('.', '').strip()}\n"
            new_content.append(line_formatted)
            
        if not line.startswith(letter) and not line.startswith(letter.capitalize()):
            word_splitted = line.split(' ')
            if word_splitted[0].lower() in ARTICLE_ALLOW:
                new_content.append(line)
            
        
            
        ## METTRE QUELQUES CHOSE POUR LES NOMS, ICI ON SUPPRIME LES NOMS
            
    new_content.sort()
    with open(path, 'w') as file:
        file.writelines(new_content)
        

def remove_duplicate_word(path: str):
    content = []
    with open(path, 'r') as file:
        content = file.readlines()
    
    with open(path, 'w') as file:
        file.writelines(list(dict.fromkeys(content)))
  

def remove_compose_word(word_type: str, path: str, logfile: TextIO):
    content = []
    new_content = [] 
    with open(path, 'r') as file:
        content = file.readlines()
        
    for word in content:
        word_splitted = word.split(' ')
        if len(word_splitted) == 1:
            new_content.append(word)
        if len(word_splitted) == 2 and word_type == 'nouns':
            print_all(f"[DONT_REMOVE_ARTICLE]: {word}", logfile)
            if word_splitted[0].lower() in ARTICLE_ALLOW:
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
            remove_numeration_and_bad_word(to_learn, path, letter)
            remove_duplicate_word(path)
            remove_compose_word(folder, path, logfile)
            if folder == 'verbs':
                remove_conjugated_verb(path)

    for folder in folders:
        files = os.listdir(f"data/{native}_{to_learn}/{folder}/list")
        for file in files:
            path = f"data/{native}_{to_learn}/{folder}/list/{file}"
            with open(path, 'r') as f:
                all_words[folder] += len(f.readlines())


def create_all_list_of_word(native: str, to_learn: str, logfile: TextIO):
    type_of_words = ['verbs', 'nouns', 'adjectives', 'adverbs']
    
    for type_word in type_of_words:
        path = f'data/{native}_{to_learn}/{type_word}'
        if not os.path.isdir(path):
            os.makedirs(path)
            print_all(f"{' '*4}[CREATE_FOLDER]: {path}", logfile)
            
        for letter_code in range(ord('a'), ord('z')+1):
            letter = chr(letter_code)
            file_path = f"{path}/list/start_by_{letter}.txt"
            if os.path.exists(file_path):
                print_all(f"{' '*4}[ALREADY_EXIST] {file_path}", logfile)
                continue
            create_list_of_word(type_word, letter, file_path, to_learn, logfile)
            print_all(f"{' '*4}[CREATE_FILE] {type_word}list/start_by_{letter}.txt sucessfully", logfile)
            print_all(' '*4 + "-"*80, logfile)


def create_list_of_word(type_word: str, letter: str, file_path: str, language: str, logfile: TextIO):
    global all_tokens
    info = "always in infinitive form" if type_word == "verbs" else ""
    number = N_VERBS_ADJ_BY_REQUEST if type_word in ['verbs', 'adjectives'] else N_NOUNS_BY_REQUEST if type_word == 'nouns' else N_ADVERBS_BY_REQUEST
    context = f"""Do not comment, just write one word per line without numbered it.
    Create a python list containing a minimum of {number} {language} {type_word} {info}, if possible, otherwise include as many as possible. Never comments, juste write {type_word}"""
    if type_word == 'nouns':
        context += " and don't forget to put the appropriate article before the noun."
    question = f"Write {type_word} that start by the letter '{letter}'."
    response, tokens = answer_to_the_sentence(question, context, type_word, logfile)
    all_tokens[type_word] += tokens
    
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(file_path, 'w', newline='') as file:
        file.write(response)


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


#### Specific for one letter and one type of word
def create_specific_csv(native: str, to_learn: str, folder: str, letter: str):
    logfile = open(f"logs/{native}_{to_learn}_{folder}_{letter}_logs.txt", "w")
    filepath = f'data/{native}_{to_learn}/{folder}/list/start_by_{letter}.txt'
    create_list_of_word(folder, letter, filepath, to_learn, logfile)
    print_all(f"{' '*4}[CREATE_FILE] {folder}list/start_by_{letter}.txt sucessfully", logfile)
    

if __name__ == "__main__":
    create_data_for_language("french", "english")
        
        


 

        
        