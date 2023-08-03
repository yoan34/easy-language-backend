import string
import re
import csv
from pathlib import Path
from models.computer import Computer
from models.logger import Logger
from models.chatGPT import ChatGPT
from tools.categories import CATEGORIES


# Tips pour trouver des noms de variables
# Le premier mot avant le underscore donne le contexte
# par exemple "category", ce mot la montre que l'objet est la "catégory"
# le deuxième mot "info" qui donne la variable "category_info" permet de
# qualifier, de détailler le contexte de l'objet étudié.


# JE NE LOG RIEN QUI SOIT DANS COMPUTER
# SI BESOIN DE LOG DEDANS, AJOUTER LE LOGGER DANS COMPUTER
class Generator:
    WORD_CATEGORIES = ['verb', 'noun', 'adjective', 'adverb']
    ALPHABET = list(string.ascii_lowercase)

    def __init__(
            self,
            computer: Computer,
            native_lang: str,
            target_lang: str,
            logger: Logger,
            gpt: ChatGPT,
    ):
        self.computer = computer
        self.logger = logger
        self.gpt = gpt
        self.native_lang = native_lang
        self.target_lang = target_lang
        self.categories = {
            'verb': 0,
            'noun': 0,
            'adjective': 0,
            'adverb': 0
        }
        self.tokens = 0
        self.total_words = 0

    # Text file part
    def create_all_word_files(self) -> None:
        self.logger.log("creation all text file")
        for category in Generator.WORD_CATEGORIES:
            new_folder = f"{category}/list"
            self.computer.create_folder(new_folder).change_directory(new_folder)
            for letter in Generator.ALPHABET[:1]:
                if self.computer.file_exists(letter + '.txt'):
                    continue
                self._create_word_file(category, letter)
            self.computer.comeback_to_base_path()

    def _create_word_file(self, category: str, letter: str) -> None:
        context = ChatGPT.get_context_to_generate_lexicon(self.target_lang, category, letter)
        question = ChatGPT.get_question_to_generate_lexicon(self.target_lang, category, letter)
        response = self.gpt.answer_to_generate_lexicon(context, "", category)
        self.computer.write_file(filename=f'{letter}.txt', content=response)

    # Check text files part
    def fix_word_files_errors(self) -> None:
        for folder in self.computer.list_folders:
            for file in self.computer.change_directory(f"{folder.name}/list").list_files:
                self.logger.log(f"Len of {file.name} before fix errors -> {len(self.computer.read_file(file.name))}")
                self._remove_numeration(file.name)
                self._remove_useless_chatgpt_sentence(file.name)
                self._remove_duplicates(file.name)
                self._remove_quotes(file.name)
                self.categories[folder.name] += len(self.computer.read_file(file.name))
                self.logger.log(f"Len of {file.name} after fix errors -> {len(self.computer.read_file(file.name))}")
            self.computer.comeback_to_base_path()

    def _remove_numeration(self, filename: str) -> None:
        new_content = []
        for line in self.computer.read_file(filename):
            if re.match(r'^\d+\s*-\s*', line):
                word = re.split(r'\d+\s*-\s*', line, maxsplit=1)[1]
                formatted_word = f"{word.replace('.', '').strip()}"
                new_content.append(formatted_word)
            elif re.match(r'^\d+[.\s]?', line):
                word = re.split(r'\d+[.\s]?', line, maxsplit=1)[1]
                formatted_word = f"{word.replace('.', '').strip()}"
                new_content.append(formatted_word)
            else:
                new_content.append(line.strip())
        self.computer.write_file(filename, sorted(new_content))

    def _remove_useless_chatgpt_sentence(self, filename: str) -> None:
        new_content = []
        useless_content = ["Sorry, ", "sorry, ", "Certainly,"]
        for line in self.computer.read_file(filename):
            if any(content in line for content in useless_content):
                continue
            new_content.append(line)
        self.computer.write_file(filename, sorted(new_content))

    def _remove_duplicates(self, filename: str) -> None:
        file_content = self.computer.read_file(filename)
        unique_content = list(set(file_content))
        self.computer.write_file(filename, sorted(unique_content))

    def _remove_quotes(self, filename: str) -> None:
        new_content = []
        for line in self.computer.read_file(filename):
            new_line = line.replace("'", "")
            new_line = new_line.replace('"', '')
            new_content.append(new_line)
        self.computer.write_file(filename, sorted(new_content))

    # CSV file part
    def create_all_csv_files(self) -> None:
        self.logger.log("creation all csv files")
        for category in Generator.WORD_CATEGORIES:
            self.computer.create_folder(f"{category}/csv")
            files = self.computer.change_directory(f"{category}/list").list_files
            self.computer.change_directory('../csv')
            for file in files:
                if not self.computer.file_exists(file.name):
                    self._create_csv_file(category, file)
            self.computer.comeback_to_base_path()
    
    def _create_csv_file(self, category: str, file: Path) -> None:
        # on est au bon dossier on doit:
        # - envoyer la bonne requête a chatGPT
        # - écrire le fichier CSV
        # words = self.computer.read_file(filename)
        words = file.read_text()
        question = ChatGPT.get_question_to_generate_csv(self.target_lang, self.native_lang, category, words)
        response = self.gpt.answer_to_generate_lexicon(question, "", category)
        self.computer.write_file(filename=f'{file.name[0]}.csv', content=response)
        
    def compare_file_contents(self):
        for folder in self.computer.list_folders:
            n_file_txt = self.computer.change_directory(f"{folder.name}/list").list_files
            n_file_csv = self.computer.change_directory(f"../csv").list_files
            print(f"TXT: {n_file_txt}    -    CSV: {n_file_csv}")
            self.computer.comeback_to_base_path()



