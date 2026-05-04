# evaluate.py
from dotenv import load_dotenv
load_dotenv()

from mongo_chatbot.chatbot import CustomChatBot
from questions_test import QA_PAIRS

def evaluate():
    bot = CustomChatBot()
    
    print("🧪 ÉVALUATION DU CHATBOT ENSAM")
    print("="*60)
    
    score = 0
    total = len(QA_PAIRS)
    resultats = []

    for i, qa in enumerate(QA_PAIRS):
        question = qa["question"]
        mots_cles = qa["mots_cles_attendus"]
        
        print(f"\n❓ Question {i+1}/{total}: {question}")
        
        try:
            reponse = bot.answer_question(question)
            print(f"🤖 Réponse: {reponse[:150]}...")
            
            reponse_lower = reponse.lower()
            mots_trouves = [m for m in mots_cles if m.lower() in reponse_lower]
            taux = len(mots_trouves) / len(mots_cles)
            
            if taux >= 0.5:
                print(f"✅ Correct ({len(mots_trouves)}/{len(mots_cles)} mots clés)")
                score += 1
            else:
                print(f"❌ Incorrect ({len(mots_trouves)}/{len(mots_cles)} mots clés)")
                
        except Exception as e:
            print(f"💥 Erreur: {e}")

    accuracy = (score / total) * 100
    print("\n" + "="*60)
    print("📊 RÉSULTATS FINAUX")
    print("="*60)
    print(f"✅ Bonnes réponses : {score}/{total}")
    print(f"📈 Accuracy        : {accuracy:.1f}%")
    print("="*60)
    
    if accuracy >= 80:
        print("🟢 Excellent ! Le bot est très performant.")
    elif accuracy >= 60:
        print("🟡 Moyen. Le bot peut être amélioré.")
    else:
        print("🔴 Faible. Le bot nécessite des améliorations.")

if __name__ == "__main__":
    evaluate()