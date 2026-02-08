"""
CLI Interface
"""
import asyncio
from core.orchestrator.orchestrator import CognitiveOrchestrator

async def main():
    orchestrator = CognitiveOrchestrator()
    print("🖥️  OpenCngsm CLI Interface")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
            
        result = await orchestrator.process_message(user_input, "cli_user")
        print(f"Bot: {result['response']}\n")

if __name__ == "__main__":
    asyncio.run(main())
