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
            max_tokens=2048
        )

    def answer_question(self, question: str) -> str:
        docs = search_global_documents(question, k=15)
        context = "\n\n---\n\n".join(
            f"[{d.metadata['source']}]\n{d.page_content}" for d in docs
        )
        system = (
            "Tu es un assistant compétent de l'ENSAM. "
            "Tu réponds TOUJOURS dans la même langue que la question posée. "
            "Si la question est en français, tu réponds en français. "
            "Si la question est en anglais, tu réponds en anglais. "
            "Tu réponds uniquement avec les informations du contexte fourni."
        )
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Contexte :\n{context}\n\nQuestion : {question}")
        ]
        return self.llm.invoke(messages).content