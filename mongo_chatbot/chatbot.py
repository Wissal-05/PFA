# mongo_chatbot/chatbot.py
import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mongo_chatbot.vectorstore import search_global_documents
from mongo_chatbot.language_detector import LanguageDetector

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
assert GROQ_API_KEY, "Définissez GROQ_API_KEY dans le fichier .env"

class CustomChatBot:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=1024
        )

    def answer_question(self, question: str) -> str:
        # 1. Détection automatique de la langue
        lang = LanguageDetector.detect_language(question)
        print(f"🌐 Langue détectée : {lang}")
        
        # 2. Récupération du contexte
        docs = search_global_documents(question, k=10)
        context = "\n\n---\n\n".join(
            f"[{d.metadata['source']}]\n{d.page_content}" for d in docs
        )
        
        # 3. Prompt système adapté à la langue détectée
        if lang == 'ar':
            system = (
                "أنت مساعد مفيد لمدرسة ENSAM. "
                "أجب فقط بالعربية. "
                "اعتمد فقط على السياق المقدم. "
                "لا تخترع أي معلومات خارج السياق."
            )
        elif lang == 'en':
            system = (
                "You are a helpful assistant for ENSAM school. "
                "You MUST answer ONLY in ENGLISH. "
                "Base your answers only on the provided context. "
                "Do not invent any information outside the context."
            )
        else:  # français par défaut
            system = (
                "Tu es un assistant utile pour l'école ENSAM. "
                "Tu dois répondre UNIQUEMENT en FRANÇAIS. "
                "Base tes réponses uniquement sur le contexte fourni. "
                "N'invente pas d'informations en dehors du contexte."
            )
        
        # 4. Génération de la réponse
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Contexte :\n{context}\n\nQuestion : {question}")
        ]
        
        response = self.llm.invoke(messages).content
        print(f"💬 Réponse ({lang}) : {response[:100]}...")
        
        return response