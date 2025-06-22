# mongo_chatbot/chatbot.py

import os
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from mongo_chatbot.vectorstore import search_global_documents

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
assert OPENROUTER_API_KEY, "Définissez OPENROUTER_API_KEY"

class CustomChatBot:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="mistralai/mistral-7b-instruct:free",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=OPENROUTER_API_KEY,
            temperature=0.2, max_tokens=512
        )

    def answer_question(self, question: str) -> str:
        docs = search_global_documents(question, k=15)
        context = "\n\n---\n\n".join(
            f"[{d.metadata['source']}]\n{d.page_content}" for d in docs
        )
        system = (
            "Tu es un assistant compétent, multilingue FR/EN, "
            "tolérant aux fautes. Réponds uniquement avec le contexte."
        )
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Contexte :\n{context}\n\nQuestion : {question}")
        ]
        return self.llm.invoke(messages).content
