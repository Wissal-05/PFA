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

from mongo_chatbot.chatbot import CustomChatBot
from mongo_chatbot.language_detector import LanguageDetector
from mongo_chatbot.db import db

app = FastAPI()
chatbot = CustomChatBot()

feedback_collection = db["feedbacks"]

# ✅ Fichier JSON local
FEEDBACK_FILE = "feedbacks.json"
QUESTIONS_FILE = "questions.json"

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

@app.post("/ask")
def ask_question(data: Question):
    answer = chatbot.answer_question(data.question)
    return {"answer": answer}

@app.post("/ask/stream")
async def ask_question_stream(data: Question):
    async def generate():
        # ✅ Détecter la langue et sauvegarder la question
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
    # ✅ Sauvegarde JSON toujours
    feedbacks = load_json(FEEDBACK_FILE)
    feedbacks.append(doc)
    save_json(FEEDBACK_FILE, feedbacks)

    # ✅ Essaye MongoDB sans planter
    try:
        doc_mongo = doc.copy()
        doc_mongo["created_at"] = datetime.now(timezone.utc)
        feedback_collection.insert_one(doc_mongo)
    except Exception as e:
        print(f"⚠️ MongoDB non disponible : {e}")

    return {"status": "ok"}

@app.get("/stats")
def get_stats():
    feedbacks = load_json(FEEDBACK_FILE)
    questions = load_json(QUESTIONS_FILE)

    # Stats feedbacks
    total_feedbacks = len(feedbacks)
    positive = sum(1 for f in feedbacks if f["rating"] == "positive")
    negative = sum(1 for f in feedbacks if f["rating"] == "negative")

    # Top 5 questions
    question_texts = [f["question"] for f in feedbacks]
    top_questions = Counter(question_texts).most_common(5)

    # Langues
    langs = [q["lang"] for q in questions]
    lang_counter = Counter(langs)
    total_langs = len(langs) or 1
    languages = {
        "fr": round(lang_counter.get("fr", 0) / total_langs * 100),
        "en": round(lang_counter.get("en", 0) / total_langs * 100),
        "ar": round(lang_counter.get("ar", 0) / total_langs * 100),
    }

    # Derniers feedbacks
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