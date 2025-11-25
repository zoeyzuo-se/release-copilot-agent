import asyncio
from rc_agent.agents.release_copilot_agent import create_release_copilot_agent


async def main():
    """Interactive CLI chat with the Release Copilot agent."""
    print("Release Copilot - CI/CD Assistant")
    print("Type 'exit' to quit\n")

    # Create the agent
    agent = create_release_copilot_agent()

    # Chat loop
    while True:
        # Get user input
        user_input = input("You: ").strip()

        # Check for exit command
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        # Skip empty input
        if not user_input:
            continue

        # Send message to agent and get response
        try:
            result = await agent.run(user_input)
            print(f"Agent: {result.text}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
