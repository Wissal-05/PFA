# mongo_chatbot/vectorstore.py

import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from mongo_chatbot.retriever import MongoRetriever

CHROMA_DIR = "./chroma_db"
GLOBAL_COLLECTION = "all_docs"

# embedders multilingues
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def create_global_index(collection_names: list[str]) -> None:
    all_docs: list[Document] = []
    for coll in collection_names:
        retriever = MongoRetriever(coll)
        docs = retriever.get_documents_as_langchain_objects()
        all_docs.extend(docs)
    persist_dir = os.path.join(CHROMA_DIR, GLOBAL_COLLECTION)
    os.makedirs(persist_dir, exist_ok=True)
    print(f"📦 Index global : {len(all_docs)} docs")
    Chroma.from_documents(
        documents=all_docs,
        embedding=embedding,
        persist_directory=persist_dir,
        collection_name=GLOBAL_COLLECTION,
        collection_metadata={"hnsw:space":"cosine"}
    )
    print("[✓] Index global créé.")


def search_global_documents(query: str, k: int = 5) -> list[Document]:
    from langchain_chroma import Chroma
    persist_dir = os.path.join(CHROMA_DIR, GLOBAL_COLLECTION)
    vectorstore = Chroma(
        embedding_function=embedding,
        persist_directory=persist_dir,
        collection_name=GLOBAL_COLLECTION
    )
    return vectorstore.similarity_search(query, k=k)