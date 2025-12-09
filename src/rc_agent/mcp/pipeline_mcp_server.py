"""FastMCP Server for Pipeline Status Tool."""

import json
from fastmcp import FastMCP
from rc_agent.config.settings import settings

# Create FastMCP server instance
mcp = FastMCP("pipeline-status-server")


def _get_pipeline_status_impl(service: str, environment: str) -> dict:
    """
    Implementation of get_pipeline_status tool.

    Args:
        service: The service name (e.g., 'payments', 'checkout')
        environment: The environment (e.g., 'prod', 'staging')

    Returns:
        dict: Pipeline status information
    """
    # Read pipelines data
    pipelines_file = settings.data_dir / "pipelines.json"

    try:
        with open(pipelines_file, 'r') as f:
            pipelines = json.load(f)
    except FileNotFoundError:
        return {
            "found": False,
            "error": "Pipelines data file not found"
        }

    # Search for matching pipeline
    for pipeline in pipelines:
        if pipeline.get("service") == service and pipeline.get("environment") == environment:
            return {
                "found": True,
                "status": pipeline.get("status"),
                "pipeline_id": pipeline.get("pipeline_id"),
                "branch": pipeline.get("branch"),
                "started_at": pipeline.get("started_at"),
                "finished_at": pipeline.get("finished_at"),
                "failed_job_id": pipeline.get("failed_job_id")
            }

    # No matching pipeline found
    return {
        "found": False,
        "message": f"No pipeline found for service '{service}' in environment '{environment}'"
    }


# Expose as plain function for direct imports
get_pipeline_status = _get_pipeline_status_impl


# Register as FastMCP tool
@mcp.tool()
def get_pipeline_status_tool(service: str, environment: str) -> dict:
    """
    Get the status of a deployment pipeline for a specific service and environment.

    Args:
        service: The service name (e.g., 'payments', 'checkout')
        environment: The environment (e.g., 'prod', 'staging')

    Returns:
        dict: Pipeline status information
    """
    return _get_pipeline_status_impl(service, environment)


if __name__ == "__main__":
    # Run with SSE transport on HTTP
    mcp.run(transport="sse", port=8001)
