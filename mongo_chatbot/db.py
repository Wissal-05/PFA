# mongo_chatbot/db.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI est introuvable dans le fichier .env")

client = MongoClient(
    MONGODB_URI,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    retryWrites=False
)

db_name = os.getenv("MONGODB_DB", "ensam_chatbot")
db = client[db_name]

def test_connection():
    try:
        client.admin.command("ping")
        print("✅ Connexion réussie :", db.name)
        collections = db.list_collection_names()
        print("📦 Collections :", collections)
        for coll in collections:
            count = db[coll].count_documents({})
            print(f"  - {coll} : {count} documents")
    except Exception as e:
        print("❌ Erreur :", e)