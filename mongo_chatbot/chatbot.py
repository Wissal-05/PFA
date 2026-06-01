# mongo_chatbot/chatbot.py
import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from mongo_chatbot.vectorstore import search_global_documents, get_all_documents_by_source
from mongo_chatbot.language_detector import LanguageDetector

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
assert GROQ_API_KEY, "Définissez GROQ_API_KEY dans le fichier .env"

UNSUPPORTED_LANG_MESSAGE = (
    "⚠️ Je supporte uniquement le français, l'anglais et l'arabe.\n"
    "I only support French, English and Arabic.\n"
    "أنا أدعم الفرنسية والإنجليزية والعربية فقط."
)

COLLECTION_KEYWORDS = {
    'formations': [
        'formation', 'cycle', 'master', 'préparatoire', 'ingénieur',
        'débouché', 'coordonnateur', 'aéronautique', 'mécanique',
        'biomédical', 'industriel', 'data science', 'énergie', 'matériaux',
        'électrique', 'énergétique', 'filière', 'cursus', 'programme'
    ],
    'departements': [
        'département', 'departement'
    ],
    'evenements': [
        'événement', 'evenement', 'robotics', 'conférence', 'conference',
        'symposium', 'journée', 'cérémonie', 'ceremonie', 'diplôme',
        'innov', 'cistem', 'ieee', 'doctoriale', 'biomasse', 'mathematica',
        'stage', 'pfe', '3dexperience', 'hongrie', 'rennes'
    ],
    'gouvernance': [
        'directeur', 'email', 'secrétaire', 'adjoint', 'assistante',
        'responsable', 'gouvernance', 'administration', 'pr.', 'professeur'
    ],
    'description_ecole': [
        'ensam', 'école', 'université', 'approche', 'pédagogique',
        'learning by doing', 'objectif', 'présentation'
    ]
}

def detect_collection(question: str) -> str | None:
    question_lower = question.lower()
    for collection, keywords in COLLECTION_KEYWORDS.items():
        if any(kw in question_lower for kw in keywords):
            return collection
    return None


class CustomChatBot:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=2048  # ✅ augmenté
        )

    def answer_question(self, question: str) -> str:
        # 1. Détection automatique de la langue
        lang = LanguageDetector.detect_language(question)
        print(f"🌐 Langue détectée : {lang}")

        # 2. Bloquer les langues non supportées
        if lang == 'unsupported':
            print("🚫 Langue non supportée")
            return UNSUPPORTED_LANG_MESSAGE

        # 3. Récupération du contexte
        docs = search_global_documents(question, k=20)

        # 4. Ajouter TOUS les documents de la collection pertinente
        collection = detect_collection(question)
        if collection:
            print(f"📁 Collection détectée : {collection}")
            extra_docs = get_all_documents_by_source(collection)
            docs = docs + extra_docs

        # 5. Dédupliquer
        seen = set()
        unique_docs = []
        for doc in docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc)

        print(f"📄 Documents uniques : {len(unique_docs)}")

        context = "\n\n---\n\n".join(
            f"[{d.metadata['source']}]\n{d.page_content}" for d in unique_docs
        )

        # 6. Prompt système
        system = LanguageDetector.get_system_prompt(lang)

        # 7. Génération de la réponse
        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"""Contexte :
{context}

Question : {question}

IMPORTANT :
- Réponds de façon CONCISE et COMPLÈTE
- Pour les listes, donne juste le NOM sans trop de détails
- Maximum 200 mots
- Base-toi UNIQUEMENT sur le contexte fourni
- Ne dis jamais qu'il pourrait y avoir d'autres informations""")
        ]

        response = self.llm.invoke(messages).content
        print(f"💬 Réponse ({lang}) : {response[:100]}...")

        return response