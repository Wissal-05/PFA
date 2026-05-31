from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse

import asyncio
import json
from mongo_chatbot.chatbot import CustomChatBot
from mongo_chatbot.db import db

app = FastAPI()
chatbot = CustomChatBot()

# Feedback collection
feedback_collection = db["feedbacks"]

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ────────────────────────────────────────────────────────────────────
class Question(BaseModel):
    question: str


class FeedbackModel(BaseModel):
    message_id: str
    question: str
    answer: str
    rating: str                    # "positive" | "negative"
    comment: Optional[str] = ""


# ── Routes ────────────────────────────────────────────────────────────────────
@app.post("/ask")
def ask_question(data: Question):
    answer = chatbot.answer_question(data.question)
    return {"answer": answer}

@app.post("/ask/stream")
async def ask_question_stream(data: Question):
    async def generate():
        answer = chatbot.answer_question(data.question)
        for char in answer:
            yield json.dumps({"chunk": char}) + "\n"
            await asyncio.sleep(0.03)
    
    return StreamingResponse(generate(), media_type="application/x-ndjson")


@app.post("/feedback")
def submit_feedback(data: FeedbackModel):
    """
    Store user feedback for a single assistant message.
    Document shape stored in MongoDB:
    {
        message_id : str,
        question   : str,
        answer     : str,
        rating     : "positive" | "negative",
        comment    : str,
        created_at : datetime (UTC)
    }
    """
    doc = {
        "message_id": data.message_id,
        "question": data.question,
        "answer": data.answer,
        "rating": data.rating,
        "comment": data.comment or "",
        "created_at": datetime.now(timezone.utc),
    }
    feedback_collection.insert_one(doc)
    return {"status": "ok"}


@app.get("/feedback/stats")
def get_feedback_stats():
    """
    Quick summary: total ratings, positive vs negative count.
    Useful for an admin dashboard later.
    """
    total = feedback_collection.count_documents({})
    positive = feedback_collection.count_documents({"rating": "positive"})
    negative = feedback_collection.count_documents({"rating": "negative"})
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
    }