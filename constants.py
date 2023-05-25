QUESTION_FOR_LIST_FORMAT = "Transform the following list of {} into the expected list of lists of {} without comments. {}"
CONTEXT_FOR_LIST_FORMAT = """
I'm giving you a list of {} and guidelines, you have to create a list of list. For each {}, you have to create list with:
- first element, the {} word.
- second element, the translation in {}. You can use two word for a better comprehension seperate by a '-'.
- third element, the CEFR level between A1 and C2.
- fourth element, the frequency of the word scored ranging from 1 for rarely used to 10 for very commonly used.
{}
return only the list of the lists in python format. Use double quote for elements of list."""


HEADERS_CSV = lambda native, to_learn: {
    'verbs': [native, to_learn, 'level', 'frequency', 'type', 'info'],
    'adverbs': [native, to_learn, 'level', 'frequency', 'type'],
    'nouns': [native, to_learn, 'level', 'frequency', 'type'],
    'adjectives': [native, to_learn, 'level', 'frequency'],
}

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