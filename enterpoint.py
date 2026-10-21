import os

from dotenv import load_dotenv

from memory import Memory
from model import create_client
from run_Agent import run_agent

load_dotenv()

memory = Memory()


def enteryPoint():
    api_key = os.getenv("FREELLMAPI_API_KEY")
    model_name = os.getenv("FREELLMAPI_MODEL")
    base_url = os.getenv("FREELLMAPI_BASE_URL", "")
    if not api_key or not model_name:
        raise ValueError(
            "Set FREELLMAPI_API_KEY and FREELLMAPI_MODEL in your environment."
        )
    client = create_client(api_key, base_url)

    while True:

        user_input = input("\nAsk Question : ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        memory.add_memory("user", user_input)

        print("\n[MEMORY]")
        print(memory.get_memory())

        try:
            print("WE ARE ENTRING INTO THE RUN_AGENT FUNCTION")
            response = run_agent(memory, client, model_name)
            print("WE ARE EXITING FROM THE RUN_AGENT FUNCTION")
            memory.add_memory("assistant", response)
            print("response", response)

        except Exception as e:
            print(f"\n[ERROR IS SHOWING HERE] {e}")
