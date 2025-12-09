from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator
from agent_framework_devui import serve


def main():
    """Launch the Release Copilot agent with DevUI interface."""
    # Create the agent (using MCP orchestrator)
    agent = create_mcp_orchestrator()

    # Serve with DevUI - it handles conversations, threads, and UI
    serve(entities=[agent], auto_open=True)


if __name__ == "__main__":
    main()
