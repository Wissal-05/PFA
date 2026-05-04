from mongo_chatbot.db import db
from typing import List, Dict, Optional
from langchain_core.documents import Document


class MongoRetriever:
    # Mapping des collections vers champs importants pour la recherche (utile pour keyword search)
    SEARCH_FIELDS = {
        "description_ecole": [
            "page",
            "meta.titre",
            "meta.université",
            "organisation_pedagogique.équipes.description",
            "organisation_pedagogique.équipes.staff",
            "organisation_pedagogique.approches.pédagogiques",
            "organisation_pedagogique.approches.objectifs"
        ],
        "gouvernance": ["role", "name", "email"],
        "formations": ["cycle", "titre", "objectifs", "debouches", "coordonnateur", "email"],
        "departements": ["nom"],
        "evenements": ["titre", "description"]
    }

    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.collection = db[collection_name]
        self.search_fields = self.SEARCH_FIELDS.get(collection_name, [])

    def get_all_documents(self) -> List[Dict]:
        return list(self.collection.find({}))

    def find_documents_by_keyword(self, keyword: str) -> List[Dict]:
        if not self.search_fields:
            query = {"$text": {"$search": keyword}}
        else:
            or_conditions = [{field: {"$regex": keyword, "$options": "i"}} for field in self.search_fields]
            query = {"$or": or_conditions}
        return list(self.collection.find(query))

    def flatten_document(self, doc: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """
        Fonction récursive pour aplatir un document MongoDB.
        Exemple : {"a": {"b": 1}} devient {"a.b": 1}
        """
        items = []
        for k, v in doc.items():
            if k == "_id":
                continue  # Ne pas inclure _id
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_document(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                joined = ", ".join(
                    str(item) if not isinstance(item, dict) else str(self.flatten_document(item))
                    for item in v
                )
                items.append((new_key, joined))
            else:
                items.append((new_key, v))
        return dict(items)

    def format_flattened_document(self, flat_doc: Dict) -> str:
        """
        Formate un document aplati selon sa collection pour le rendre lisible par le LLM.
        """
        collection = self.collection_name
        lines = []

        def add_line(label, key):
            value = flat_doc.get(key)
            if value:
                lines.append(f"{label} : {value}")

        if collection == "gouvernance":
            add_line("Rôle", "role")
            add_line("Nom", "name")
            add_line("Email", "email")

        elif collection == "description_ecole":
            add_line("Titre", "meta.titre")
            add_line("Université", "meta.université")
            add_line("Description équipes", "organisation_pedagogique.équipes.description")
            add_line("Staff", "organisation_pedagogique.équipes.staff")
            add_line("Approches pédagogiques", "organisation_pedagogique.approches.pédagogiques")
            add_line("Objectifs pédagogiques", "organisation_pedagogique.approches.objectifs")

        elif collection == "formations":
            add_line("Cycle", "cycle")
            add_line("Titre", "titre")
            add_line("Objectifs", "objectifs")
            add_line("Débouchés", "debouches")
            add_line("Coordonnateur", "coordonnateur")
            add_line("Email", "email")

        elif collection == "departements":
            add_line("Nom du département", "nom")

        elif collection == "evenements":
            add_line("Titre", "titre")
            add_line("Description", "description")

        else:
            # Fallback générique si collection inconnue
            for k, v in flat_doc.items():
                if "_id" not in k and "url" not in k:
                    lines.append(f"{k.replace('_', ' ')} : {v}")

        return "\n".join(lines)


    def get_text_chunks(self) -> List[str]:
        """
        Retourne une liste de textes prêts à être encodés (strings).
        """
        chunks = []
        for doc in self.get_all_documents():
            flat = self.flatten_document(doc)
            text = self.format_flattened_document(flat)
            chunks.append(text)
        return chunkss

    def get_documents_as_langchain_objects(self) -> List[Document]:
        """
        Retourne une liste de `langchain.schema.Document`, format idéal pour Chroma.
        """
        docs = []
        for doc in self.get_all_documents():
            flat = self.flatten_document(doc)
            text = self.format_flattened_document(flat)
            docs.append(Document(page_content=text, metadata={"source": self.collection_name}))
        return docs