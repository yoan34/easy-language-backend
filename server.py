import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import os

import openai
from dotenv import load_dotenv
import spacy

from generator import correct_the_sentence, translate_the_sentence, answer_to_the_sentence


# https://universaldependencies.org/u/dep/
load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")
nlp = spacy.load("fr_core_news_lg")


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*","OpenAI-ApiKey"]
)


class Message(BaseModel):
    input: str


@app.post("/message")
def root(message: Message):
    print(message.input)
    answer = answer_to_the_sentence(message.input)
    return answer

@app.post("/correct_message")
def root(message: Message):
    print(message.input)
    answer = correct_the_sentence(message.input)
    return answer


@app.post("/translate_message")
def root(message: Message):
    print(message.input)
    answer = translate_the_sentence(message.input)
    return answer


if __name__ == "__main__":
    uvicorn.run('server:app', host="0.0.0.0", port=8000, reload=True)