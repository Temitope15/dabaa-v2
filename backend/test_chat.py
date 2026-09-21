import os
from app.agents.assessment_agent import assessment_agent
from dotenv import load_dotenv

def run_chat():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: Please add GOOGLE_API_KEY to your .env file to run this test.")
        return

    print("==================================================")
    print("🏥 Daaba AI Triage PoC")
    print("Type 'quit' to exit.")
    print("==================================================")
    
    chat_history = []
    
    print("\nDaaba: Hello! I'm Daaba, your virtual nurse. What symptoms are you experiencing today?")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        print("\n[Daaba is thinking & checking medical guidelines...]")
        try:
            response = assessment_agent.run(user_input, chat_history)
            print(f"\nDaaba: {response}")
            
            # Store in chat history
            chat_history.append(("human", user_input))
            chat_history.append(("ai", response))
        except Exception as e:
            print(f"\n❌ Error during generation: {e}")

if __name__ == "__main__":
    run_chat()
