import asyncio
from agent_framework import RequestInfoEvent, WorkflowOutputEvent
from rc_agent.agents.orchestrator import create_orchestrator
from rc_agent.telemetry import init_tracing


async def main():
    """Interactive CLI chat with the Release Copilot multi-agent workflow."""
    # Initialize OpenTelemetry tracing
    # This creates timestamped trace files in traces/ directory
    init_tracing()

    print("Release Copilot - CI/CD Multi-Agent Assistant")
    print("=" * 60)
    print("This system uses multiple specialized agents:")
    print("  • Coordinator: Routes your queries to the right specialist")
    print("  • Pipeline Status Agent: Provides deployment status info")
    print("  • Job Logs Analyzer: Analyzes failures and errors")
    print("\nType 'exit' or 'quit' to end the conversation.\n")

    # Create the orchestrator workflow
    workflow = create_orchestrator()

    # Get initial user input
    user_input = input("You: ").strip()

    # Check for immediate exit
    if user_input.lower() in ("exit", "quit"):
        print("Goodbye!")
        return

    # Run the workflow with streaming to observe events
    try:
        async for event in workflow.run_stream(user_input):
            # Handle workflow outputs (responses from agents)
            if isinstance(event, WorkflowOutputEvent):
                # This is the final response from a specialist or coordinator
                messages = event.data
                if messages:
                    # Get the last assistant message
                    for msg in reversed(messages):
                        if msg.role.value == "assistant" and msg.text:
                            print(f"\nAgent: {msg.text}\n")
                            break

            # Handle requests for user input (continuation of conversation)
            elif isinstance(event, RequestInfoEvent):
                user_input = input("You: ").strip()

                # Check for exit
                if user_input.lower() in ("exit", "quit"):
                    print("Goodbye!")
                    return

                # Send user response back to workflow
                await workflow.send_response(event.data.request_id, user_input)

    except Exception as e:
        print(f"Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
