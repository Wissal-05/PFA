# resume_data.py
from dotenv import load_dotenv
load_dotenv()
from mongo_chatbot.vectorstore import search_global_documents

docs = search_global_documents("ENSAM", k=186)

# Compter par collection
collections = {}
for doc in docs:
    source = doc.metadata['source']
    if source not in collections:
        collections[source] = 0
    collections[source] += 1

print("📊 RÉSUMÉ DES DONNÉES DANS CHROMADB")
print("="*40)
for collection, count in collections.items():
    print(f"📁 {collection} : {count} documents")
print("="*40)
print(f"📦 Total : {len(docs)} documents")