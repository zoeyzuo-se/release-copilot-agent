import asyncio
import sys
from rc_agent.agents.release_copilot_agent import create_release_copilot_agent


async def show_thinking_animation(task):
    """Show a thinking animation while waiting for the agent response."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    idx = 0
    while not task.done():
        sys.stdout.write(f"\rAgent is thinking {frames[idx]} ")
        sys.stdout.flush()
        idx = (idx + 1) % len(frames)
        await asyncio.sleep(0.1)
    sys.stdout.write("\r" + " " * 30 + "\r")  # Clear the line
    sys.stdout.flush()


async def main():
    """Interactive CLI chat with the Release Copilot agent."""
    print("Release Copilot - CI/CD Assistant")
    print("Type 'exit' to quit\n")

    # Create the agent
    agent = create_release_copilot_agent()

    # Create a thread for conversation memory
    thread = agent.get_new_thread()

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
            # Create task for agent response
            agent_task = asyncio.create_task(
                agent.run(user_input, thread=thread))

            # Show thinking animation while waiting
            await show_thinking_animation(agent_task)

            # Get the result
            result = await agent_task
            print(f"Agent: {result.text}\n")
        except Exception as e:
            print(f"Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
