import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from mongo_chatbot.vectorstore import search_global_documents

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
assert OPENROUTER_API_KEY, "Définissez OPENROUTER_API_KEY"

class CustomChatBot:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="openrouter/auto",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=OPENROUTER_API_KEY,
            temperature=0.2,
            max_tokens=512
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