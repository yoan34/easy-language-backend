import pytest
from pathlib import Path
from models.generator import Generator
from models.logger import Logger
from models.computer import Computer
from models.chatGPT import ChatGPT


@pytest.fixture
def generator():
    native_lang = "french"
    target_lang = "english"
    logger = Logger(f"{native_lang}_{target_lang}.log")
    computer = Computer(f"", logger)
    chatGPT = ChatGPT(logger)
    generator = Generator(computer, native_lang, target_lang, logger, chatGPT)
    return generator

def test_remove_numeration(generator):
    test_file = Path("test/remove_numeration.txt")

    lines = [
        "1. line 1",
        "23. line 2",
        "123. line 3",
        "1- line 4",
        "23- line 5",
        "123- line 6",
        "1 line 7",
        "23 line 8..",
        "123   line 9 ",
        "  line 10"
    ]
    
    test_file.write_text("\n".join(lines))
    generator.remove_numeration(test_file)

    processed_content = test_file.read_text()

    for i in range(1, 10):
        assert f"line {i}" in processed_content
    test_file.unlink()

def test_remove_useless_chatgpt_sentence(generator):
    test_file = Path("test/remove_useless_chatgpt_sentence.txt")
    lines = [
        "maison",
        "Sorry, you lose",
        "plate",
        "sorry, but its fine"
    ]
    test_file.write_text("\n".join(lines))
    generator.remove_useless_chatgpt_sentence(test_file)

    processed_content = test_file.read_text()
    assert "maison" in processed_content
    assert "plate" in processed_content
    assert "Sorry, " not in processed_content
    assert "sorry, " not in processed_content
    test_file.unlink()

def test_remove_duplicates(generator):
    test_file = Path("test/remove_duplicates.txt")
    lines = [
        "maison",
        "plate",
        "hello",
        "maison",
        "plate",
        "plate"
    ]
    test_file.write_text("\n".join(lines))
    generator.remove_duplicates(test_file)
    processed_content = test_file.read_text().splitlines()
    assert "maison" in processed_content
    assert "plate" in processed_content
    assert "hello" in processed_content
    assert processed_content.count("maison") == 1
    assert processed_content.count("plate") == 1
    assert processed_content.count("hello") == 1
    test_file.unlink()


def test_remove_quotes(generator):
    test_file = Path("test/remove_quotes.txt")
    lines = [
        "'maison'",
        "'plate'",
        '"chien"',
    ]
    test_file.write_text("\n".join(lines))
    generator.remove_quotes(test_file)
    processed_content = test_file.read_text().splitlines()
    assert "'maison'" not in processed_content
    assert "maison" in processed_content
    assert '"plate"' not in processed_content
    assert "plate" in processed_content
    test_file.unlink()


def test_fix_word_files_errors(generator):
    test_file = Path("fix_word_files_errors.txt")
    lines = [
        "1. maison",
        "2 - Sorry, you lose",
        "3 - plate",
        "4.sorry, but its fine"
    ]
    test_file.write_text("\n".join(lines))
    generator.remove_numeration(test_file)
    generator.remove_useless_chatgpt_sentence(test_file)
    
    processed_content = test_file.read_text()
    assert "maison" in processed_content
    assert "plate" in processed_content
    assert "Sorry, " not in processed_content
    assert "sorry, " not in processed_content
    test_file.unlink()

