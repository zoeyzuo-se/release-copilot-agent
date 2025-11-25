import json
from typing import Annotated
from pydantic import Field
from agent_framework import ai_function
from rc_agent.config.settings import settings


@ai_function(
    name="get_pipeline_status",
    description="Get the status of a deployment pipeline for a specific service and environment"
)
def get_pipeline_status(
    service: Annotated[str, Field(description="The service name (e.g., 'payments', 'checkout')")],
    environment: Annotated[str, Field(
        description="The environment (e.g., 'prod', 'staging')")]
) -> dict:
    """
    Check the status of a deployment pipeline for a given service and environment.

    Returns:
        dict: Contains 'found' (bool), 'status' (str), and 'pipeline_id' (str) if found
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
