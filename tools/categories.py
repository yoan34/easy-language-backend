CATEGORIES = {
    "english": {
        "noun": {
            "info": " Each noun should be preceded by its correct definite or indefinite article.",
            "number": 100,
        },
        "verb": {
            "info": " Write the verb in the infinitive form",
            "number": 50,
        },
        "adverb": {
            "info": "",
            "number": 20,
        },
        "adjective": {
            "info": "",
            "number": 50,
        },
    }
}

# Create a Python list containing at least {number} {type_word} in {language},
# with additional {info} where applicable. If it's not possible to find
# {number} {type_word}, include as many as possible. Write each word on
# a separate line, without numbering or adding comments. If the
# {type_word} is a verb, provide it in infinitive form; if it's a noun,
# include the definite article where applicable.
# CONTEXT = """
# Create a Python list containing at least {} {}s in {}.
# Write each word on a separate line, without numbering or adding
# comments. {}.
# """

QUESTION_FOR_GENERATE_LIST_WORD = """
Create a Python list containing at least {} different {}s in {} that start by the letter '{}'. Write each word on
a separate line, without numbering or adding comments. If the
type of word to search is a verb, provide it in infinitive form; if it's a noun,
include the definite article where applicable.
"""

QUESTION_GENERATE_CSV_ROWS = """
I'm giving you a list of {} and guidelines, you have to create a list of csv rows.The CSV separator is ";". For each {}, you have to create a row with:
- first element, the {} word.
- second element, the translation in {}. You can use two word for a better comprehension seperate by a '-'.
- third element, the CEFR level between A1 and C2.
- fourth element, the frequency of the word scored ranging from 1 for rarely used to 10 for very commonly used but you must using a range 1 to 10 for every CEFR level..
{}
return only the list of rows with one row per line. Here is the list of {}s:
{}"""

def get_more_info_for_context(category: str):
    if category == 'verb':
        return """
- fifth element, the type of verb choice the appropriate value between ACTION and STATE.
- sixth element, choice the appropriate value between REGULAR and IRREGULAR.
        """
    if category == 'adverb':
        return "- fifth element, determine the appropriate type of adverb."
    if category == 'noun':
        return "- fifth element, determine the appropriate type of noun between ABSTRACT and CONCRETE."