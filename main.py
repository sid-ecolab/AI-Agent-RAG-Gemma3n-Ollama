from agent import run_agent

if __name__ == "__main__":
    print("AI Agent with RAG & Tool Calling")
    print("Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in ("quit", "exit"):
            break
        response = run_agent(user_input)
        print(f"Agent: {response}\n")
