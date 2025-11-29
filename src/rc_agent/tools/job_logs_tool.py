import json
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
from rc_agent.config.settings import settings


@ai_function(
    name="get_job_logs",
    description="Get the logs from a specific job to understand what happened during execution"
)
def get_job_logs(
    job_id: Annotated[str, Field(
        description="The job ID to retrieve logs for (e.g., 'job-789')")]
) -> dict:
    """
    Retrieve the execution logs for a specific job.

    Returns:
        dict: Contains 'found' (bool) and 'logs' (list of log lines) if found
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
