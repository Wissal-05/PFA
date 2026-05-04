from dotenv import load_dotenv
load_dotenv()

from mongo_chatbot.vectorstore import search_global_documents

docs = search_global_documents("ENSAM", k=186)

collections = {}
for doc in docs:
    source = doc.metadata['source']
    if source not in collections:
        collections[source] = []
    collections[source].append(doc.page_content)

for collection, contenus in collections.items():
    print(f"\n{'='*60}")
    print(f"📁 COLLECTION : {collection.upper()}")
    print(f"{'='*60}")
    for i, contenu in enumerate(contenus):
        print(f"\n--- Document {i+1} ---")
        print(contenu)