CATEGORIES = {
    "english": {
        "noun": {
            "info": " Each noun should be preceded by its correct definite or indefinite article.",
            "number": 10,
        },
        "verb": {
            "info": " Write the verb in the infinitive form",
            "number": 5,
        },
        "adverb": {
            "info": "",
            "number": 2,
        },
        "adjective": {
            "info": "",
            "number": 5,
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

CONTEXT = """
You are asked to generate a list of {} {} {}s.{}"
"""
