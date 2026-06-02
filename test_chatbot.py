from dotenv import load_dotenv
load_dotenv()

from mongo_chatbot.chatbot import CustomChatBot

bot = CustomChatBot()

print("🎓 ENSAMIA prêt ! Tapez 'exit' pour quitter.\n")

while True:
    question = input("Vous : ")
    if question.lower() == "exit":
        break
    reponse = bot.answer_question(question)
    print(f"Bot : {reponse}\n")