import string
from models.computer import Computer
from models.logger import Logger
from models.chatGPT import ChatGPT
from tools.categories import CATEGORIES, CONTEXT


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
        self.verbs = 0
        self.nouns = 0
        self.adjectives = 0
        self.adverbs = 0
        self.tokens = 0
        self.total_words = 0


    def create_all_word_files(self):
        self.logger.log("creation all text file")
        for category in Generator.WORD_CATEGORIES:
            new_folder = f"{category}/list"
            self.computer.create_folder(new_folder).change_directory(new_folder)
            for letter in Generator.ALPHABET[:5]:
                if self.computer.file_exists(letter + '.txt'):
                    continue
                self.create_word_file(category, letter)
            self.computer.comeback_to_base_path()


    def create_word_file(self, category: str, letter: str):
        context = ChatGPT.get_context_to_generate_lexicon(self.target_lang, category)
        question = ChatGPT.get_question_to_generate_lexicon(category, letter)
        response = self.gpt.answer_to_generate_lexicon(question, context, category)
        self.computer.write_file(filename=f'{letter}.txt', content=response)
        # A voir pour ajouter les mots comment faire
        self.total_words += len(response.split())

    def fix_word_files_errors(self):
        for folder in self.computer.list_folders:
            for file in self.computer.change_directory(f"{folder.name}/list").list_files:
                remove_numeration_and_bad_word_from_file(file)
                remove_duplicate_word_from_file(file.name)
                remove_compose_word_from_file(file.name)
                if folder == 'verbs':
                    remove_conjugated_verb_from_file(file.name)
                all_words[folder] += len(computer.read_file(file.name))








