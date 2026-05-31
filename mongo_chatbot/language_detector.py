# mongo_chatbot/language_detector.py
from langdetect import detect, DetectorFactory
import re

# Fixer la graine pour des résultats cohérents
DetectorFactory.seed = 0

class LanguageDetector:
    @staticmethod
    def detect_language(text: str) -> str:
        """
        Détecte la langue du texte.
        Retourne : 'fr', 'en', 'ar', ou 'fr' par défaut
        """
        # Vérifier d'abord les caractères arabes
        if re.search(r'[\u0600-\u06FF]', text):
            return 'ar'
        
        try:
            lang = detect(text)
            # Ne garder que les 2 premières lettres (fr, en, es, de, etc.)
            lang = lang[:2]
            
            # Langues supportées
            if lang in ['fr', 'en', 'ar']:
                return lang
            else:
                return 'fr'  # Défaut français
        except:
            return 'fr'  # En cas d'erreur, français
    
    @staticmethod
    def get_system_prompt(lang: str) -> str:
        """
        Retourne le prompt système dans la bonne langue
        """
        prompts = {
            'fr': (
                "Tu es ENSAMBot, un assistant virtuel officiel de l'ENSAM Rabat. "
                "Tu réponds UNIQUEMENT en FRANÇAIS. "
                "Tu te bases sur le contexte fourni. "
                "Si l'information n'est pas dans le contexte, dis-le clairement. "
                "Sois concis et professionnel."
            ),
            'en': (
                "You are ENSAMBot, an official virtual assistant of ENSAM Rabat. "
                "You answer ONLY in ENGLISH. "
                "You base your answers on the provided context. "
                "If the information is not in the context, say so clearly. "
                "Be concise and professional."
            ),
            'ar': (
                "أنت بوت ENSAMBot، مساعد رسمي افتراضي لمدرسة ENSAM الرباط. "
                "أجب فقط بالعربية. "
                "اعتمد فقط على السياق المقدم. "
                "إذا لم تكن المعلومة في السياق، قل ذلك بوضوح. "
                "كن موجزاً ومهنياً."
            )
        }
        return prompts.get(lang, prompts['fr'])