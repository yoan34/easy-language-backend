from models.computer import Computer
from models.generator import Generator
from models.logger import Logger
from models.chatGPT import ChatGPT
from tools.enumerators import ModelType


native_lang = "french"
target_lang = "english"

logger = Logger(f"{native_lang}_{target_lang}.log")
computer = Computer(f"../data/{native_lang}_{target_lang}", logger)
chatGPT4 = ChatGPT(logger, model=ModelType.GPT_4)
generator = Generator(computer, native_lang, target_lang, logger, chatGPT4)


# generator.create_all_word_files()
# generator.fix_word_files_errors()
# generator.create_all_csv_files()
generator.compare_file_contents()