
import os
import json
import openai
from dotenv import load_dotenv
import spacy
import time

# https://universaldependencies.org/u/dep/
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")


def answer_to_the_sentence(sentence):
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {'role':'system', 'content':'The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.'},
      {"role": "user", "content": sentence},    
    ],
    temperature=0.8
  )
  return completion.choices[0].message.content

def correct_the_sentence(sentence):
  context = """Correct spelling mistakes and meaning of the sentence if necessary.
  Just return the correction WITHOUT comment. Return only the word 'correct' if nothing should be change otherwise only the sentence. Never comment."""
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {'role':'system', 'content':context},
      {"role": "user", "content": sentence},    
    ],
    temperature=0
  )
  return completion.choices[0].message.content

def translate_the_sentence(sentence, lang='fr'):
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {'role':'system', 'content':f'translate the following sentence into {lang}. Just return the correction.'},
      {"role": "user", "content": sentence},    
    ],
    temperature=0
  )
  return completion.choices[0].message.content

def parseText(sentence):
  completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
      {'role':'system', 'content':f""},
      {"role": "user", "content": sentence},    
    ],
  )
  return completion.choices[0].message.content



if __name__ == "__main__":

  text = """
  Voici un petit texte d'environ 300 mots en français pour vous. J'espère qu'il vous plaira !
  Il était une fois un petit garçon nommé Antoine qui aimait jouer dans les bois derrière sa maison. Un jour, alors qu'il jouait près d'un ruisseau, il aperçut un petit oiseau qui semblait blessé. Antoine s'approcha doucement et vit que l'oiseau avait une aile cassée. Sans hésiter, il décida de l'emmener chez lui pour le soigner.
  Arrivé chez lui, Antoine a pris soin de l'oiseau blessé en lui donnant de l'eau et de la nourriture. Il a même improvisé un petit nid douillet pour qu'il puisse se reposer et guérir. Au fil des jours, l'oiseau a commencé à se rétablir et à prendre confiance en Antoine. Ils sont devenus amis et ont passé beaucoup de temps ensemble.
  Un jour, alors qu'Antoine et son nouvel ami oiseau étaient en train de jouer dans les bois, ils ont rencontré un vieux sage. Le sage a vu qu'Antoine avait un grand cœur et lui a dit : "Mon petit garçon, tu as un don rare. Tu as la capacité d'aider les autres, même les plus petits et les plus vulnérables." Antoine a été ému par les paroles du sage et a décidé de devenir un guérisseur pour les animaux.
  À partir de ce jour, Antoine a utilisé ses compétences pour aider les animaux blessés dans les bois. Il a soigné des oiseaux, des écureuils et même des lapins. Tous les animaux de la forêt ont appris à faire confiance à Antoine et à venir à lui pour obtenir de l'aide.
  Le temps a passé et Antoine est devenu un guérisseur célèbre dans la région. Les gens venaient de partout pour demander son aide pour leurs animaux malades. Antoine était heureux de pouvoir aider les autres, mais il n'oubliait jamais son ami oiseau qui lui avait appris l'importance de la gentillesse et de l'empathie.
  Et c'est ainsi que l'histoire d'Antoine, le guérisseur des animaux, est devenue légendaire dans toute la région.
  """
  a = time.time()
  nlp = spacy.load("fr_core_news_lg")
  b = time.time()
  print(f"TIME TO LOAD: {b-a}")
  doc = nlp(text)
  for token in doc:
    print(f"{token.text:<15}  {token.lemma_:<15}  {token.pos_:<6}  {token.dep_} --> {token.prob}")