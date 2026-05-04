from dotenv import load_dotenv
load_dotenv()
from mongo_chatbot.vectorstore import search_global_documents

collections = ["directeur", "formations", "département", "événement", "école"]

for mot in collections:
    print(f"\n{'='*50}")
    print(f"🔍 Recherche : {mot}")
    print(f"{'='*50}")
    docs = search_global_documents(mot, k=3)
    for doc in docs:
        print(f"📁 Source: {doc.metadata['source']}")
        print(doc.page_content)
        print("---")