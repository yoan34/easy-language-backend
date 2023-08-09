import spacy

with open("alice.txt", "r") as f:
    text = f.read()
    chapters = text.split("CHAPTER ")[1:]
    print(len(chapters))
    
chapter1 = chapters[0]


nlp = spacy.load("en_core_web_sm")

doc = nlp(chapter1)
sentences = list(doc.sents)
sentence = sentences[1]

for token in sentence:
    print(token.text, token.pos_)