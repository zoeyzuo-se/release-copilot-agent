from rc_agent.agents.release_copilot_agent import create_release_copilot_agent
from agent_framework_devui import serve


def main():
    """Launch the Release Copilot agent with DevUI interface."""
    # Create the agent
    agent = create_release_copilot_agent()
    
    # Serve with DevUI - it handles conversations, threads, and UI
    serve(entities=[agent], auto_open=True)


if __name__ == "__main__":
    main()
