# debug_formations.py
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

vectorstore = Chroma(
    embedding_function=embedding,
    persist_directory="./chroma_db/all_docs",
    collection_name="all_docs"
)

all_docs = vectorstore.get()

print(f"Total documents : {len(all_docs['documents'])}")
print("\n=== DOCUMENTS SOURCE=formations ===")
for content, meta in zip(all_docs['documents'], all_docs['metadatas']):
    if meta.get('source') == 'formations':
        print("---")
        print(content)