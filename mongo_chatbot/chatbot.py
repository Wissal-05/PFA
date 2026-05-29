import os
# from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mongo_chatbot.vectorstore import search_global_documents

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
assert GROQ_API_KEY, "Définissez GROQ_API_KEY"


class CustomChatBot:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0.2, 
            max_tokens=1024
        )

    def answer_question(self, question: str) -> str:
        docs = search_global_documents(question, k=10)
        context = "\n\n---\n\n".join(
            f"[{d.metadata['source']}]\n{d.page_content}" for d in docs
        )
        system = (
            "You are a helpful assistant for ENSAM school. "
            "CRITICAL RULE: always reply in the exact same language the user used to ask their question. "
            "If the question is in English, your entire response must be in English. "
            "If the question is in French, your entire response must be in French. "
            "If the question is in Arabic, your entire response must be in Arabic. "
            "Base your answers only on the provided context. "
            "Do not translate or change the language under any circumstances."
        )
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Contexte :\n{context}\n\nQuestion : {question}")
        ]
        return self.llm.invoke(messages).content