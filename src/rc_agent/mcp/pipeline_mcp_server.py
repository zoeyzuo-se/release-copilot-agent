"""MCP Server for Pipeline Status Tool."""

import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from rc_agent.config.settings import settings


# Create MCP server instance
app = Server("pipeline-status-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_pipeline_status",
            description="Get the status of a deployment pipeline for a specific service and environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "The service name (e.g., 'payments', 'checkout')"
                    },
                    "environment": {
                        "type": "string",
                        "description": "The environment (e.g., 'prod', 'staging')"
                    }
                },
                "required": ["service", "environment"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    if name != "get_pipeline_status":
        raise ValueError(f"Unknown tool: {name}")

    service = arguments.get("service")
    environment = arguments.get("environment")

    # Read pipelines data
    pipelines_file = settings.data_dir / "pipelines.json"

    try:
        with open(pipelines_file, 'r') as f:
            pipelines = json.load(f)
    except FileNotFoundError:
        return [TextContent(
            type="text",
            text=json.dumps({
                "found": False,
                "error": "Pipelines data file not found"
            })
        )]

    # Search for matching pipeline
    for pipeline in pipelines:
        if pipeline.get("service") == service and pipeline.get("environment") == environment:
            result = {
                "found": True,
                "status": pipeline.get("status"),
                "pipeline_id": pipeline.get("pipeline_id"),
                "branch": pipeline.get("branch"),
                "started_at": pipeline.get("started_at"),
                "finished_at": pipeline.get("finished_at"),
                "failed_job_id": pipeline.get("failed_job_id")
            }
            return [TextContent(type="text", text=json.dumps(result))]

    # No matching pipeline found
    return [TextContent(
        type="text",
        text=json.dumps({
            "found": False,
            "message": f"No pipeline found for service '{service}' in environment '{environment}'"
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
