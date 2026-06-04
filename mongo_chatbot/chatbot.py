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
        'formation', 'cycle', 'master', 'préparatoire', 'préparatoires',
        'ingénieur', 'débouché', 'coordonnateur', 'coordinateur',
        'aéronautique', 'mécanique', 'biomédical', 'industriel',
        'data science', 'énergie', 'matériaux', 'électrique',
        'énergétique', 'filière', 'cursus', 'programme',
        'objectif', 'débouchés', 'email coordinateur'
    ],
    'departements': [
        'département', 'departement', 'départements', 'departements'
    ],
    'evenements': [
        'événement', 'evenement', 'événements', 'evenements',
        'robotics', 'conférence', 'conference', 'symposium',
        'journée', 'cérémonie', 'ceremonie', 'diplôme',
        'innov', 'cistem', 'ieee', 'doctoriale', 'biomasse',
        'mathematica', 'stage', 'pfe', '3dexperience', 'hongrie', 'rennes',
        'activité', 'activités', 'manifestation'
    ],
    'gouvernance': [
        'directeur', 'email', 'secrétaire', 'adjoint', 'assistante',
        'responsable', 'gouvernance', 'administration', 'pr.',
        'professeur', 'contact', 'qui est', 'chef', 'doyen'
    ],
    'description_ecole': [
        'ensam', 'école', 'université', 'approche', 'pédagogique',
        'learning by doing', 'objectif', 'présentation', 'histoire',
        'campus', 'localisation', 'adresse'
    ]
}


def detect_collections(question: str) -> list:
    question_lower = question.lower()
    scores = {}
    for collection, keywords in COLLECTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in question_lower)
        if score > 0:
            scores[collection] = score
    return sorted(scores, key=scores.get, reverse=True)


class CustomChatBot:
    def __init__(self):
        self.llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            api_key=GROQ_API_KEY,
            temperature=0.2,
            max_tokens=2048
        )

    def answer_question(self, question: str) -> str:
        # 1. Détection automatique de la langue
        lang = LanguageDetector.detect_language(question)
        print(f"🌐 Langue détectée : {lang}")

        # 2. Bloquer les langues non supportées
        if lang == 'unsupported':
            print("🚫 Langue non supportée")
            return UNSUPPORTED_LANG_MESSAGE

        # 3. Récupération du contexte vectoriel (k=5 pour la vitesse)
        docs = search_global_documents(question, k=5)

        # 4. Ajouter les documents de TOUTES les collections pertinentes
        collections = detect_collections(question)
        if collections:
            print(f"📁 Collections détectées : {collections}")
            for col in collections:
                extra_docs = get_all_documents_by_source(col)
                docs = docs + extra_docs[:5]
        else:
            print("📁 Aucune collection détectée")

        # 5. Dédupliquer
        seen = set()
        unique_docs = []
        for doc in docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                unique_docs.append(doc)

        unique_docs = unique_docs[:15]
        print(f"📄 Documents uniques : {len(unique_docs)}")

        context = "\n\n---\n\n".join(
            f"[{d.metadata['source']}]\n{d.page_content}" for d in unique_docs
        )
        context = context[:4000]

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

        try:
            response = self.llm.invoke(messages).content
            print(f"💬 Réponse ({lang}) : {response[:100]}...")
            return response
        except Exception as e:
            print(f"❌ Erreur LLM : {str(e)}")
            return f"Erreur : {str(e)}"