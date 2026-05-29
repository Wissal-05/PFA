# mongo_chatbot/db.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI est introuvable dans le fichier .env")

client = MongoClient(
    MONGODB_URI,
    tls=True,
    tlsCAFile=certifi.where(),      # tlsAllowInvalidCertificates removed
    serverSelectionTimeoutMS=30000,
    connectTimeoutMS=30000,
    socketTimeoutMS=30000,
    retryWrites=False
)

db_name = os.getenv("MONGODB_DB", "ensam_chatbot")
db = client[db_name]

def test_connection():
    try:
        result = client.admin.command("ping")
        print("✅ Connexion réussie à la base :", db.name)
        try:
            collections = db.list_collection_names()
            print("📦 Collections disponibles :", collections)
        except Exception as e2:
            print("⚠️ Connecté mais liste collections échoue :", e2)
    except Exception as e:
        print("❌ Erreur de connexion :", e)