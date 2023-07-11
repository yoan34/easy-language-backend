from models.computer import Computer
from models.generator import Generator
from models.logger import Logger
from models.chatGPT import ChatGPT


# N_VERBS_ADJ_BY_REQUEST = 50
# N_NOUNS_BY_REQUEST = 100
# N_ADVERBS_BY_REQUEST = 20
N_VERBS_ADJ_BY_REQUEST = 15
N_NOUNS_BY_REQUEST = 15
N_ADVERBS_BY_REQUEST = 15

native_lang = "french"
target_lang = "english"

logger = Logger(f"{native_lang}_{target_lang}.log")
computer = Computer(f"../data/{native_lang}_{target_lang}", logger)
chatGPT = ChatGPT(logger)
generator = Generator(computer, native_lang, target_lang, logger, chatGPT)


generator.create_all_word_files()
