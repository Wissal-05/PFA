from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer l'URI MongoDB depuis les variables d'environnement
MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI est introuvable dans le fichier .env")

# Connexion au client MongoDB
client = MongoClient(MONGODB_URI)

# Choix de la base de données
db_name = os.getenv("MONGODB_DB", "ensam_chatbot")  # nom par défaut = chatbot
db = client[db_name]

# Test simple pour vérifier la connexion
def test_connection():
    try:
        print("✅ Connexion réussie à la base :", db.name)
        print("📦 Collections disponibles :", db.list_collection_names())
    except Exception as e:
        print("❌ Erreur de connexion :", e)
