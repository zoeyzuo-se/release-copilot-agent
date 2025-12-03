"""MCP Server for Job Logs Tool."""

import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from rc_agent.config.settings import settings


# Create MCP server instance
app = Server("job-logs-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_job_logs",
            description="Get the logs from a specific job to understand what happened during execution",
            inputSchema={
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "The job ID to retrieve logs for (e.g., 'job-789')"
                    }
                },
                "required": ["job_id"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name != "get_job_logs":
        raise ValueError(f"Unknown tool: {name}")

    job_id = arguments.get("job_id")

    # Read logs data
    logs_file = settings.data_dir / "log.json"

    try:
        with open(logs_file, 'r') as f:
            all_logs = json.load(f)
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text=json.dumps({
                "found": False,
                "error": "Logs data file not found"
            })
        )]

    # Look up the job logs
    if job_id in all_logs:
        logs = all_logs[job_id]
        result = {
            "found": True,
            "job_id": job_id,
            "logs": logs
        }
        return [TextContent(type="text", text=json.dumps(result))]

    # Job not found
    return [TextContent(
        type="text",
        text=json.dumps({
            "found": False,
            "message": f"No logs found for job '{job_id}'"
        })
    )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
