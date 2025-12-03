"""Service for accessing pipeline data."""

import json
from typing import Optional
from pathlib import Path
from rc_agent.config.settings import settings


class PipelineService:
    """Service for retrieving pipeline status information."""

    def __init__(self, data_file: Optional[Path] = None):
        """
        Initialize the pipeline service.

        Args:
            data_file: Path to pipelines data file. Defaults to settings.data_dir/pipelines.json
        """
        self.data_file = data_file or settings.data_dir / "pipelines.json"

    def get_pipeline_status(self, service: str, environment: str) -> dict:
        """
        Get the status of a deployment pipeline for a specific service and environment.

        Args:
            service: The service name (e.g., 'payments', 'checkout')
            environment: The environment (e.g., 'prod', 'staging')

        Returns:
            dict: Pipeline status information with keys:
                - found (bool): Whether a matching pipeline was found
                - status (str): Pipeline status if found
                - pipeline_id (str): Pipeline ID if found
                - branch (str): Branch name if found
                - started_at (str): Start timestamp if found
                - finished_at (str): Finish timestamp if found
                - failed_job_id (str): Failed job ID if applicable
                - error/message (str): Error or informational message if not found
        """
        try:
            with open(self.data_file, 'r') as f:
                pipelines = json.load(f)
        except FileNotFoundError:
            return {
                "found": False,
                "error": f"Pipelines data file not found: {self.data_file}"
            }
        except json.JSONDecodeError as e:
            return {
                "found": False,
                "error": f"Invalid JSON in pipelines data file: {e}"
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

    def list_all_pipelines(self) -> list:
        """
        List all pipelines in the data file.

        Returns:
            list: List of all pipeline records
        """
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
