from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse
from collections import Counter
import asyncio
import json
import os
import uuid

from mongo_chatbot.chatbot import CustomChatBot
from mongo_chatbot.language_detector import LanguageDetector
from mongo_chatbot.db import db

app = FastAPI()
chatbot = CustomChatBot()

feedback_collection = db["feedbacks"]

FEEDBACK_FILE = "feedbacks.json"
QUESTIONS_FILE = "questions.json"
CONVERSATIONS_FILE = "conversations.json"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

class FeedbackModel(BaseModel):
    message_id: str
    question: str
    answer: str
    rating: str
    comment: Optional[str] = ""

# ✅ username ajouté
class SaveConversationModel(BaseModel):
    conversation_id: str
    title: str
    messages: list
    username: str

@app.post("/ask")
def ask_question(data: Question):
    answer = chatbot.answer_question(data.question)
    return {"answer": answer}

@app.post("/ask/stream")
async def ask_question_stream(data: Question):
    async def generate():
        lang = LanguageDetector.detect_language(data.question)
        questions = load_json(QUESTIONS_FILE)
        questions.append({
            "question": data.question,
            "lang": lang,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        save_json(QUESTIONS_FILE, questions)

        answer = chatbot.answer_question(data.question)
        for char in answer:
            yield json.dumps({"chunk": char}) + "\n"
            await asyncio.sleep(0.03)

    return StreamingResponse(generate(), media_type="application/x-ndjson")

@app.post("/feedback")
def submit_feedback(data: FeedbackModel):
    doc = {
        "message_id": data.message_id,
        "question": data.question,
        "answer": data.answer,
        "rating": data.rating,
        "comment": data.comment or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    feedbacks = load_json(FEEDBACK_FILE)
    feedbacks.append(doc)
    save_json(FEEDBACK_FILE, feedbacks)

    try:
        doc_mongo = doc.copy()
        doc_mongo["created_at"] = datetime.now(timezone.utc)
        feedback_collection.insert_one(doc_mongo)
    except Exception as e:
        print(f"⚠️ MongoDB non disponible : {e}")

    return {"status": "ok"}

# ✅ Sauvegarder une conversation avec username
@app.post("/conversations/save")
def save_conversation(data: SaveConversationModel):
    conversations = load_json(CONVERSATIONS_FILE)
    
    existing = next((c for c in conversations if c["conversation_id"] == data.conversation_id), None)
    
    if existing:
        existing["messages"] = data.messages
        existing["title"] = data.title
        existing["updated_at"] = datetime.now(timezone.utc).isoformat()
    else:
        conversations.append({
            "conversation_id": data.conversation_id,
            "title": data.title,
            "messages": data.messages,
            "username": data.username,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
    
    save_json(CONVERSATIONS_FILE, conversations)
    return {"status": "ok"}

# ✅ Récupérer les conversations filtrées par username
@app.get("/conversations")
def get_conversations(username: str):
    conversations = load_json(CONVERSATIONS_FILE)
    user_convs = [c for c in conversations if c.get("username") == username]
    return [
        {
            "conversation_id": c["conversation_id"],
            "title": c["title"],
            "updated_at": c["updated_at"],
        }
        for c in sorted(user_convs, key=lambda x: x["updated_at"], reverse=True)
    ]

# ✅ Récupérer une conversation par ID
@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str):
    conversations = load_json(CONVERSATIONS_FILE)
    conv = next((c for c in conversations if c["conversation_id"] == conversation_id), None)
    if not conv:
        return {"error": "Conversation non trouvée"}
    return conv

@app.get("/stats")
def get_stats():
    feedbacks = load_json(FEEDBACK_FILE)
    questions = load_json(QUESTIONS_FILE)

    total_feedbacks = len(feedbacks)
    positive = sum(1 for f in feedbacks if f["rating"] == "positive")
    negative = sum(1 for f in feedbacks if f["rating"] == "negative")

    question_texts = [f["question"] for f in feedbacks]
    top_questions = Counter(question_texts).most_common(5)

    langs = [q["lang"] for q in questions]
    lang_counter = Counter(langs)
    total_langs = len(langs) or 1
    languages = {
        "fr": round(lang_counter.get("fr", 0) / total_langs * 100),
        "en": round(lang_counter.get("en", 0) / total_langs * 100),
        "ar": round(lang_counter.get("ar", 0) / total_langs * 100),
    }

    last_feedbacks = feedbacks[-5:][::-1]

    return {
        "total_questions": len(questions),
        "total_feedbacks": total_feedbacks,
        "positive": positive,
        "negative": negative,
        "positive_pct": round(positive / total_feedbacks * 100) if total_feedbacks else 0,
        "negative_pct": round(negative / total_feedbacks * 100) if total_feedbacks else 0,
        "top_questions": [{"question": q, "count": c} for q, c in top_questions],
        "languages": languages,
        "last_feedbacks": last_feedbacks,
    }

@app.get("/feedback/stats")
def get_feedback_stats():
    try:
        total = feedback_collection.count_documents({})
        positive = feedback_collection.count_documents({"rating": "positive"})
        negative = feedback_collection.count_documents({"rating": "negative"})
        return {"total": total, "positive": positive, "negative": negative}
    except:
        return {"total": 0, "positive": 0, "negative": 0}