QUESTION_FOR_LIST_FORMAT = "Transform the following list of {} into the expected list of lists of {} without comments. {}"
CONTEXT_FOR_LIST_FORMAT = """
I'm giving you a list of {} and guidelines, you have to create a list of list. For each {}, you have to create list with:
- first element, the English word.
- second element, the translation in French. You can use two word for a better comprehension seperate by a '-'.
- third element, the CEFR level between A1 and C2.
- fourth element, the frequency of the word scored ranging from 1 for rarely used to 10 for very commonly used.
{}
return only the list of the lists in python format. Use double quote for elements of list."""

HEADERS_CSV = {
    'verbs': ['english', 'french', 'level', 'frequency', 'type', 'info'],
    'adverbs': ['english', 'french', 'level', 'frequency', 'type'],
    'nouns': ['english', 'french', 'level', 'frequency', 'type'],
    'adjectives': ['english', 'french', 'level', 'frequency'],
}