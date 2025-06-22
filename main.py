from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mongo_chatbot.chatbot import CustomChatBot

app = FastAPI()
chatbot = CustomChatBot()

# Autoriser le frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask_question(data: Question):
    answer = chatbot.answer_question(data.question)
    return {"answer": answer}
