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
        Retourne : 'fr', 'en', 'ar', ou 'unsupported'
        """
        # Vérifier d'abord les caractères arabes
        if re.search(r'[\u0600-\u06FF]', text):
            return 'ar'
        
        try:
            lang = detect(text)
            lang = lang[:2]
            
            if lang in ['fr', 'en', 'ar']:
                return lang
            else:
                return 'unsupported'  # ✅ corrigé
        except:
            return 'unsupported'  # ✅ corrigé
    
    @staticmethod
    def get_system_prompt(lang: str) -> str:
        prompts = {
            'fr': (
                "Tu es ENSAMIA, un assistant virtuel officiel de l'ENSAM Rabat. "
                "Tu réponds UNIQUEMENT en FRANÇAIS. "
                "Tu te bases sur le contexte fourni. "
                "Si l'information n'est pas dans le contexte, dis-le clairement. "
                "Sois concis et professionnel."
            ),
            'en': (
                "You are ENSAMIA, an official virtual assistant of ENSAM Rabat. "
                "You answer ONLY in ENGLISH. "
                "You base your answers on the provided context. "
                "If the information is not in the context, say so clearly. "
                "Be concise and professional."
            ),
            'ar': (
                "أنت بوت ENSAMIA، مساعد رسمي افتراضي لمدرسة ENSAM الرباط. "
                "أجب فقط بالعربية. "
                "اعتمد فقط على السياق المقدم. "
                "إذا لم تكن المعلومة في السياق، قل ذلك بوضوح. "
                "كن موجزاً ومهنياً."
            )
        }
        return prompts.get(lang, prompts['fr'])