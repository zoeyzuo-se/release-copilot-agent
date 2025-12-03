# Examples

This directory contains usage examples for the Release Copilot Agent.

## MCP Architecture Example

**File:** `mcp_usage_example.py`

Demonstrates how to use the MCP-based orchestrator with both MCP tools (pipeline status and job logs).

### Run the example:

```bash
python examples/mcp_usage_example.py
```

### What it does:

1. Creates an MCP orchestrator agent
2. Connects to two MCP servers (pipeline and logs)
3. Runs three example queries:
   - Check pipeline status for a service
   - Analyze a failed deployment
   - Check job logs directly

### Prerequisites:

- MCP package installed: `pip install mcp>=1.0.0`
- Azure OpenAI credentials configured (`.env` file)
- Azure login: `az login` on host machine

### Expected output:

```
Creating MCP orchestrator...

============================================================
Example 1: Checking pipeline status
============================================================

Agent response:
The payments service in production has a status of "success"...

============================================================
Example 2: Analyzing a failed deployment
============================================================

Agent response:
The checkout service in staging failed...

============================================================
Example 3: Direct log analysis
============================================================

Agent response:
The logs for job-456 show...

============================================================
Examples completed!
============================================================
```

## Custom Usage

You can create your own scripts using the MCP orchestrator:

```python
import asyncio
from rc_agent.agents.mcp_orchestrator import create_mcp_orchestrator


async def main():
    # Create the agent
    agent = create_mcp_orchestrator()
    
    # Ask a question
    result = await agent.run("Your question here")
    
    # Print the response
    for msg in result.messages:
        if msg.role.value == "assistant" and msg.text:
            print(msg.text)


if __name__ == "__main__":
    asyncio.run(main())
```

## More Information

- Quick start guide: `../QUICKSTART_MCP.md`
- Full documentation: `../README.md`
- Architecture comparison: `../COMPARISON.md`
- Migration guide: `../MIGRATION_GUIDE.md`
