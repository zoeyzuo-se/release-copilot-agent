"""FastMCP Server for Job Logs Tool."""

import json
from fastmcp import FastMCP
from rc_agent.config.settings import settings

# Create FastMCP server instance
mcp = FastMCP("job-logs-server")


def _get_job_logs_impl(job_id: str) -> dict:
    """
    Implementation of get_job_logs tool.

    Args:
        job_id: The job ID to retrieve logs for (e.g., 'job-789')

    Returns:
        dict: Job logs information
    """
    # Read logs data
    logs_file = settings.data_dir / "log.json"

    try:
        with open(logs_file, 'r') as f:
            all_logs = json.load(f)
    except FileNotFoundError:
        return {
            "found": False,
            "error": "Logs data file not found"
        }

    # Look up the job logs
    if job_id in all_logs:
        logs = all_logs[job_id]
        return {
            "found": True,
            "job_id": job_id,
            "logs": logs
        }

    # Job not found
    return {
        "found": False,
        "message": f"No logs found for job '{job_id}'"
    }


# Expose as plain function for direct imports
get_job_logs = _get_job_logs_impl


# Register as FastMCP tool
@mcp.tool()
def get_job_logs_tool(job_id: str) -> dict:
    """
    Get the logs from a specific job to understand what happened during execution.

    Args:
        job_id: The job ID to retrieve logs for (e.g., 'job-789')

    Returns:
        dict: Job logs information
    """
    return _get_job_logs_impl(job_id)


if __name__ == "__main__":
    # Run with SSE transport on HTTP
    mcp.run(transport="sse", port=8002)
