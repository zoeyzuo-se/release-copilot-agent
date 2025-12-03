"""Example usage of simplified tool-based Release Copilot Agent."""

import asyncio
from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator


async def main():
    """Run example queries using the tool-based orchestrator."""

    # Create the orchestrator (uses direct tools instead of sub-agents)
    print("Creating orchestrator with direct tools...")
    agent = create_mcp_orchestrator()    # Example 1: Check pipeline status
    print("\n" + "="*60)
    print("Example 1: Checking pipeline status")
    print("="*60)

    result = await agent.run("What's the status of the payments service in prod?")
    print("\nAgent response:")
    for msg in result.messages:
        if msg.role.value == "assistant" and msg.text:
            print(msg.text)

    # Example 2: Analyze a failure
    print("\n" + "="*60)
    print("Example 2: Analyzing a failed deployment")
    print("="*60)

    result = await agent.run("The checkout service failed in staging. What went wrong?")
    print("\nAgent response:")
    for msg in result.messages:
        if msg.role.value == "assistant" and msg.text:
            print(msg.text)

    # Example 3: Direct log analysis (if you know the job ID)
    print("\n" + "="*60)
    print("Example 3: Direct log analysis")
    print("="*60)

    result = await agent.run("Can you check the logs for job-456?")
    print("\nAgent response:")
    for msg in result.messages:
        if msg.role.value == "assistant" and msg.text:
            print(msg.text)

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
